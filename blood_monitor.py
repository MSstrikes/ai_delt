# 血量监控代码
# author : you hao lin

import facebook_api as fp
import csv
import utils as tool
import time
import datetime


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


def handler():
    sum_spend = 0
    sum_install = 0
    blood_pool = []
    with open(tool.BLOOD_LISTEN_OBJ, 'r') as csv_file:
        spam_reader = csv.reader(csv_file)
        for row in spam_reader:
            ad_id = row[0]
            # 排除血量已为0的广告
            if ad_id in ads_group_blood and ads_group_blood[ad_id] == 0:
                continue

            spend, install, pay = fp.get_insights(ad_id)

            if ad_id not in ads_group_index:
                blood_val = blood(spend, install, pay, spend, pay)
            else:
                spend_old, install_old, pay_old = ads_group_index[ad_id]
                if spend < spend_old:
                    blood_val = blood(spend, install, pay, spend, pay)
                else:
                    blood_val = blood(spend - spend_old, install - spend_old, pay - pay_old, spend, pay)

            ads_group_index[ad_id] = (spend, install, pay)
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
                fp.stopCompaign(ad_id)
                fp.stopCompaign(fp.get_adset_id(ad_id))
                fp.stopCompaign(fp.get_compaign_id(ad_id))
                tool.logger.info('campaign\t' + ad_id + '\tclosed for 0 blood.')
            else:
                sum_spend = sum_spend + spend
                sum_install = sum_install + install

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
        if time.strftime('%M', time.localtime(time.time()))[1] == '3':
            estimated_roi, threshold = handler()
            if estimated_roi >= 0.05 * (1 + 0.2):
                tool.logger.info('adjust some ads\' bid amount......')
                # 触发出价上调机会
                # 按blood选择前10个广告，给予调价机会
                for key in ads_group_blood:
                    org_advertise_set_id = fp.get_adset_id(key)
                    org_bid = fp.get_bid_amount(org_advertise_set_id)
                    new_bid = 25000
                    if ads_group_blood[key] >= threshold:
                        # new_bid = random.uniform(25000,60000)
                        new_bid = 600 - 350 * (ads_group_blood[key] - 100) / (threshold - 100 + 0.001)
                        if new_bid > 600:
                            new_bid = 600
                    fp.update_bid_amount(org_advertise_set_id, new_bid)
                    tool.logger.info("ad set " + org_advertise_set_id + ' adjust bid amount from ' +
                                     str(org_bid) + " to " + str(new_bid))
            d_name = datetime.datetime.now().strftime('%Y-%m-%d %H:%M').replace(':', "-").replace(' ', "-")
            tool.saveJson('logs/blood-status-' + d_name + ".log", ads_group_blood)
            time.sleep(60)
        else:
            time.sleep(1)


if __name__ == '__main__':
    monitor()
