# 血量监控代码
# author : you hao lin

import facebook_api as fp
import utils as tool
import time
import datetime
import os
import json
import nats_proc as ntp
import math
import random

# ----------------------------------------------------------


def blood(spend, install, pay, acc_spend, acc_pay):
    # 计算血量
    if spend > 0:
        if install > 0:
            if pay > 0:
                return p_func(acc_spend / acc_pay)
            else:
                return h_func(spend / install)
        else:
            return -spend
    else:
        return -10


def h_func(cpi):
    if cpi <= 6:
        return 10
    if 6 < cpi <= 8:
        return 40 - 5 * cpi
    if cpi > 8:
        return 8 - cpi


def p_func(acc_cpp):
    if acc_cpp <= 200:
        return 20
    else:
        return 40 - 0.1 * acc_cpp


# ----------------------------------------------------------


ads_group_index = {}
ads_group_blood = {}
ads_group_roi = {}
bid_b0 = 5000
period_cnt = 1


def get_ad_index():
    # 获得广告的状态
    str_cmd = 'sh getStatus.sh "\\"fields=status\\"" ' + tool.ad_id_str + ' > ' + tool.JSON_TMP_FILE1
    out = os.system(str_cmd)
    ad_status = {}
    if out == 0:
        print('get ad status success!')
        with open(tool.JSON_TMP_FILE1, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                ad_status[json_obj['detail']['id']] = json_obj['detail']['status']
    else:
        print('get ad status failure!')
    # print(ad_status)
    # 获得广告的insights
    from_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    to_date = from_date
    str_cmd = 'sh getIndex.sh "\\"fields=ad_id,spend,actions&time_range={\\\\"\\"since\\\\"\\":\\\\"\\"' + from_date + \
              '\\\\"\\",\\\\"\\"until\\\\"\\":\\\\"\\"' + to_date + '\\\\"\\"}\\"" ' + tool.ad_id_str + ' > ' + \
              tool.JSON_TMP_FILE2
    out = os.system(str_cmd)
    ad_dict = {}
    if out == 0:
        print("get ad index success!")
        with open(tool.JSON_TMP_FILE2, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  #读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                if len(json_obj['detail']['data']) != 0:
                    if 'ad_id' in json_obj['detail']['data'][0]:
                        tmp_ad_id = json_obj['detail']['data'][0]['ad_id']
                        if tmp_ad_id in ad_status and ad_status[tmp_ad_id] == 'ACTIVE':
                            ad_dict[tmp_ad_id] = fp.get_insights_by_json(json_obj['detail'])
    else:
        print("get ad index failure!")
    for ad_id in ad_status:
        if ad_id not in ad_dict:
            ad_dict[ad_id] = (0, 0, 0)
    return ad_dict


def stop_campaign_process(stop_campaigns):
    start = 0
    step = 500
    end = step
    n_len = len(stop_campaigns)
    if end <= n_len:
        while True:
            ntp.stop_campaign(stop_campaigns[start:end], cmd_type='PAUSED')
            time.sleep(30)
            start = end
            end = start + step
            if end > n_len:
                end = n_len
            if start >= end:
                break
    else:
        ntp.stop_campaign(stop_campaigns, cmd_type='PAUSED')


def set_blood(ad_id, blood_val):
    if ad_id not in ads_group_blood:
        ads_group_blood[ad_id] = 100
    ads_group_blood[ad_id] = round(ads_group_blood[ad_id] + blood_val, 2)
    if ads_group_blood[ad_id] < 0:
        ads_group_blood[ad_id] = 0
    if ads_group_blood[ad_id] > 100:
        ads_group_blood[ad_id] = 100
    tool.logger.info(ad_id + '\tblood\t' + str(round(blood_val, 2)))


def calc_ad_blood(ad_id, ad_indexes):
    spend, install, pay = ad_indexes[ad_id]
    if ad_id not in ads_group_index:
        blood_val = blood(spend, install, pay, spend, pay)
    else:
        spend_old, install_old, pay_old = ads_group_index[ad_id]
        if spend < spend_old:
            blood_val = blood(spend, install, pay, spend, pay)
        else:
            blood_val = blood(spend - spend_old, install - spend_old, pay - pay_old, spend, pay)
    return blood_val


def cal_roi(sum_install, sum_spend):
    if sum_install > 0 and sum_spend > 0:
        return 0.03 * sum_install * 10 / sum_spend
    else:
        return 0


def handler():
    sum_spend = 0
    sum_install = 0
    stop_campaigns = []
    ad_indexes = get_ad_index()
    adset_bid = get_bid()
    for ad_id in ad_indexes:
        # 排除血量已为0的广告
        if ad_id in ads_group_blood and ads_group_blood[ad_id] == 0:
            continue
        # 设置广告blood
        set_blood(ad_id, calc_ad_blood(ad_id, ad_indexes))
        ads_group_index[ad_id] = ad_indexes[ad_id]

        # 使用模拟退火算法调整广告出价
        cur_roi = cal_roi(ad_indexes[ad_id][1], ad_indexes[ad_id][0])
        ad_set_id = tool.ad_collections[ad_id]['adset']
        cur_bid = adset_bid[ad_set_id]
        if ad_id not in ads_group_roi:
            old_roi = 0
        else:
            old_roi = ads_group_roi[ad_id]
        if cur_roi > old_roi:
            print("Adset " + ad_set_id + " 接受出价")
        else:
            bid_delta = bid_b0 * 1.0 / math.log(1 + period_cnt, math.e)
            trigger_prob = math.pow(math.e, -(0.06 - cur_roi) * 1000 / (bid_delta * 1.0 / 100))
            print("Adset " + ad_set_id + " trigger_prob:" + str(trigger_prob))
            tool.logger.info("Adset " + ad_set_id + " trigger_prob:" + str(trigger_prob))
            if random.uniform(0, 1) <= trigger_prob:
                print("Adset " + ad_set_id + " 提高出价...")
                new_bid = cur_bid + bid_delta
            else:
                print("Adset " + ad_set_id + " 降低出价...")
                new_bid = cur_bid - bid_delta
            if new_bid > tool.BID_MAX:
                new_bid = tool.BID_MAX
            if new_bid < 5000:
                new_bid = 5000
            new_bid = int(round(new_bid, 0))
            fp.update_bid_amount(ad_set_id, new_bid)
            tool.logger.info("ad set " + ad_set_id + '<ad_id:' + ad_id + '> adjust bid amount from ' + str(cur_bid) +
                             " to " + str(new_bid))
        ads_group_roi[ad_id] = cur_roi
        # 如果血量为0，则关闭广告
        if ads_group_blood[ad_id] == 0:
            tmp_campaign = tool.ad_collections[ad_id]['campaign']
            stop_campaigns.append(tmp_campaign)
            tool.logger.info('campaign\t' + tmp_campaign + '\tclosed for 0 blood.')
        else:
            sum_spend = sum_spend + ad_indexes[ad_id][0]
            sum_install = sum_install + ad_indexes[ad_id][1]

    # stop ads by 500
    stop_campaign_process(stop_campaigns)

    # estimate roi
    return cal_roi(sum_install, sum_spend)


def calc_new_bid(cur_blood, threshold):
    new_bid = 600 - 350 * (cur_blood - 100) / (threshold - 100 + 0.001)
    if new_bid > 600:
        new_bid = 600
    if new_bid < 250:
        new_bid = 250
    new_bid = int(round(new_bid * 100, 0))
    return new_bid


def get_bid():
    str_cmd = 'sh getBidAmount.sh "\\"fields=bid_amount\\"" ' + tool.ad_set_str + ' > ' + tool.JSON_TMP_FILE4
    out = os.system(str_cmd)
    adset_bid = {}
    if out == 0:
        print('get ad bid amount success!')
        with open(tool.JSON_TMP_FILE4, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  #读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                adset_bid[json_obj['detail']['id']] = json_obj['detail']['bid_amount']
    else:
        print('get ad bid amount failure!')
    return adset_bid


def monitor():
    cur_minutes = time.strftime('%M', time.localtime(time.time()))
    print('cur_minutes:' + cur_minutes)
    while True:
        if time.strftime('%M', time.localtime(time.time())) == cur_minutes:
            print("start.....")
            estimated_roi = handler()
            print(estimated_roi)
            d_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M').replace(':', "-").replace(' ', "-")
            tool.save_json('logs/blood-status-' + tool.BLOOD_LISTEN_OBJ + '-' + d_name + ".log", ads_group_blood)
            time.sleep(60)
            global period_cnt
            period_cnt = period_cnt + 1
        else:
            time.sleep(1)


if __name__ == '__main__':
    monitor()
