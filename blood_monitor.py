# 血量监控代码
# author : you hao lin

import facebook_api as fp
import utils as tool
import time
import datetime
import os
import json
import nats_proc as ntp
import random
from scipy import stats
import math
from ptbuilder import gen_pts as gp, builder_proc as bp


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
ads_group_index = dict()
ads_group_blood = dict()
ads_group_roi = dict()
x_stats = stats.norm(loc=0, scale=0.025)
y_stats = stats.norm(loc=5, scale=15)
z_stats = stats.norm(loc=5, scale=10)


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
    print("停止" + str(len(stop_campaigns)) + "个广告......finished!")
    if len(stop_campaigns) > 0:
        print("准备创建" + str(len(stop_campaigns)) + "个广告.")
        bp.gen_builder()
        gp.create_ads(len(stop_campaigns))
        key = tool.get_obj_key()
        if key not in tool.listen_seeds:
            tool.listen_seeds.append(key)
        tool.listen_init()


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


def get_cur_hour():
    return int(time.strftime('%H', time.localtime(time.time())))


def update_bid(new_bid, cur_bid, ad_set_id, ad_id):
    if new_bid > tool.BID_MAX:
        new_bid = tool.BID_MAX
    if new_bid < tool.BID_MIN:
        new_bid = tool.BID_MIN
    new_bid = int(round(new_bid, 0))
    fp.update_bid_amount(ad_set_id, new_bid)
    tool.logger.info("ad set " + ad_set_id + '<ad_id:' + ad_id + '> adjust bid amount from ' + str(cur_bid) +
                     " to " + str(new_bid))


def handler():
    sum_spend = 0
    sum_install = 0
    stop_campaigns = list()
    ad_indexes = tool.get_ad_index()
    adset_bid = get_bid()
    for ad_id in ad_indexes:
        # 排除血量已为0的广告
        if ad_id in ads_group_blood and ads_group_blood[ad_id] == 0:
            continue
        # 设置广告blood
        set_blood(ad_id, calc_ad_blood(ad_id, ad_indexes))
        ads_group_index[ad_id] = ad_indexes[ad_id]

        # 调整广告出价
        cur_roi = cal_roi(ad_indexes[ad_id][1], ad_indexes[ad_id][0])
        ad_set_id = tool.ad_collections[ad_id]['adset']
        cur_bid = adset_bid[ad_set_id]
        if ad_id not in ads_group_roi:
            old_roi = 0
        else:
            old_roi = ads_group_roi[ad_id]
        x = cur_roi - old_roi
        spend, install, pay = ad_indexes[ad_id]
        if x >= 0:
            p_remain = math.sqrt((1 - x_stats.cdf(x)) * (y_stats.cdf(spend)))
            print("p_remain:" + str(p_remain))
            if random.uniform(0, 1) <= p_remain:
                print("Adset " + ad_set_id + " 保持出价...")
            else:
                print("Adset " + ad_set_id + " 提高出价...")
                new_bid = cur_bid + tool.max_up_bid[get_cur_hour()] * tool.bid_change_base * (1 - p_remain)
                update_bid(new_bid, cur_bid, ad_set_id, ad_id)
        else:
            if install > 0:
                cpi = spend / install
            else:
                cpi = 0
            p_down = math.sqrt(x_stats.cdf(-x) * z_stats.cdf(cpi))
            print("p_down:" + str(p_down))
            if random.uniform(0, 1) <= p_down:
                print("Adset " + ad_set_id + " 降低出价...")
                new_bid = cur_bid - tool.max_down_bid[get_cur_hour()] * tool.bid_change_base * p_down
                update_bid(new_bid, cur_bid, ad_set_id, ad_id)
            else:
                print("Adset " + ad_set_id + " 提高出价...")
                new_bid = cur_bid + tool.max_up_bid[get_cur_hour()] * tool.bid_change_base * (1 - p_down)
                update_bid(new_bid, cur_bid, ad_set_id, ad_id)
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
    if len(stop_campaigns) > 0:
        stop_campaign_process(stop_campaigns)

    # estimate roi
    return cal_roi(sum_install, sum_spend)


def get_bid():
    str_cmd = 'sh shell-script/getBidAmount.sh "\\"fields=bid_amount\\"" ' + tool.ad_set_str + ' > ' + tool.JSON_TMP_FILE4
    out = os.system(str_cmd)
    adset_bid = dict()
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
        else:
            time.sleep(1)

