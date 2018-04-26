# 血量监控代码
# author : you hao lin

import facebook_api as fp
import utils as tool
import time
import datetime
import gevent
import os
import json

# ----------------------------------------------------------
# 计算血量


def blood_v1(spend, install, pay):
    if spend > 0:
        if install > 0:
            cpi = spend / install
            if cpi > 10:
                return -5, 0x11
            else:
                if pay > 0:
                    return +20, 0x12
                else:
                    return +5, 0x13
        else:
            return -5, 0x14
    else:
        return -10, 0x15


def blood(spend, install, pay, acc_spend, acc_pay):
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


def stop_ad_action(ad_id):
    fp.stop_campaign(ad_id)
    fp.stop_campaign(fp.get_adset_id(ad_id))
    fp.stop_campaign(fp.get_campaign_id(ad_id))
    tool.logger.info('campaign\t' + ad_id + '\tclosed for 0 blood.')


def get_ad_index():
    ad_id_str = ''
    for ad_id in tool.ad_collections:
        ad_id_str = ad_id_str + ad_id + ' '
    # 获得广告的状态
    str_cmd = 'sh getStatus.sh "\\"fields=status\\"" ' + ad_id_str + ' > ' + tool.JSON_TMP_FILE1
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
    print(ad_status)
    # 获得广告的insights
    from_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    to_date = from_date
    str_cmd = 'sh getIndex.sh "\\"fields=ad_id,spend,actions&time_range={\\\\"\\"since\\\\"\\":\\\\"\\"' + from_date + \
              '\\\\"\\",\\\\"\\"until\\\\"\\":\\\\"\\"' + to_date + '\\\\"\\"}\\"" ' + ad_id_str + ' > ' + tool.JSON_TMP_FILE2
    out = os.system(str_cmd)
    ad_dict = {}
    if out == 0:
        print("get ad index success!")
        with open(tool.JSON_TMP_FILE2, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                if len(json_obj['detail']['data']) != 0:
                    tmp_ad_id = json_obj['detail']['data'][0]['ad_id']
                    if ad_status[tmp_ad_id] == 'ACTIVE':
                        ad_dict[tmp_ad_id] = fp.get_insights_by_json(json_obj['detail'])
    else:
        print("get ad index failure!")

    return ad_dict


def handler():
    sum_spend = 0
    sum_install = 0
    blood_pool = []
    stop_ads = []
    ad_indexes = get_ad_index()
    for ad_id in ad_indexes:
        # 排除血量已为0的广告
        if ad_id in ads_group_blood and ads_group_blood[ad_id] == 0:
            continue

        spend, install, pay = ad_indexes[ad_id]

        if ad_id not in ads_group_index:
            blood_val = blood(spend, install, pay, spend, pay)
        else:
            spend_old, install_old, pay_old = ads_group_index[ad_id]
            if spend < spend_old:
                blood_val = blood(spend, install, pay, spend, pay)
            else:
                blood_val = blood(spend - spend_old, install - spend_old, pay - pay_old, spend, pay)

        ads_group_index[ad_id] = (spend, install, pay)

        # 设置广告blood
        if ad_id not in ads_group_blood:
            ads_group_blood[ad_id] = 100

        ads_group_blood[ad_id] = round(ads_group_blood[ad_id] + blood_val, 2)

        if ads_group_blood[ad_id] < 0:
            ads_group_blood[ad_id] = 0
        if ads_group_blood[ad_id] > 100:
            ads_group_blood[ad_id] = 100

        tool.logger.info(ad_id + '\tblood\t' + str(round(blood_val, 2)))
        blood_pool.append(ads_group_blood[ad_id])

        # 如果血量为0，则关闭广告
        if ads_group_blood[ad_id] == 0:
            stop_ads.append(ad_id)
        else:
            sum_spend = sum_spend + spend
            sum_install = sum_install + install

    # stop ads
    threads = [gevent.spawn(stop_ad_action, ad_id) for ad_id in stop_ads]
    gevent.joinall(threads)

    # threshold process
    blood_pool.sort(reverse=True)
    print(blood_pool)
    if len(blood_pool) == 0:
        tool.logger.info('exit program for 0 blood list size.')
        exit(0)
    if len(blood_pool) >= 10:
        threshold = blood_pool[9]
    else:
        threshold = blood_pool[-1]

    # estimate roi
    if sum_install > 0 and sum_spend > 0:
        return 0.3 * sum_install / sum_spend, threshold
    else:
        return 0, threshold


def monitor():
    while True:
        if time.strftime('%M', time.localtime(time.time())) == '01':
            estimated_roi, threshold = handler()
            print(estimated_roi)

            if estimated_roi >= 0.05 * (1 + 0.2):
                tool.logger.info('adjust some ads\' bid amount......')
                # 触发出价上调机会
                # 按blood选择前10个广告，给予调价机会
                for key in ads_group_blood:
                    org_advertise_set_id = fp.get_adset_id(key)
                    org_bid = fp.get_bid_amount(org_advertise_set_id)
                    new_bid = 25000
                    if ads_group_blood[key] >= threshold:
                        new_bid = 600 - 350 * (ads_group_blood[key] - 100) / (threshold - 100 + 0.001)
                        if new_bid > 600:
                            new_bid = 600
                    fp.update_bid_amount(org_advertise_set_id, new_bid)
                    tool.logger.info("ad set " + org_advertise_set_id + ' adjust bid amount from ' +
                                     str(org_bid) + " to " + str(new_bid))
            d_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M').replace(':', "-").replace(' ', "-")
            tool.save_json('logs/blood-status-' + d_name + ".log", ads_group_blood)
            time.sleep(60)
        else:
            time.sleep(1)


if __name__ == '__main__':
    monitor()
