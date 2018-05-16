import json
from collections import OrderedDict
import os
import shutil
import logging
import configparser
import requests
import urllib3
import urllib
import time


section = 'base_conf'
config = configparser.ConfigParser()
config.read("/Users/youhaolin/config.ini")

ACS_TK = config.get(section, 'access_token')
ACT_UID = config.get(section, 'account_id')
NAT_URL = config.get(section, 'nat_url')
DELIVERY_PTS_DIR = config.get(section, 'delivery_dir')


def get_obj_key():
    day = int(time.strftime('%d', time.localtime(time.time())))
    month = int(time.strftime('%m', time.localtime(time.time())))
    key = str(day) + '-' + str(month)
    return key


BLOOD_LISTEN_OBJ = get_obj_key()
listen_seeds = [BLOOD_LISTEN_OBJ]
LOG_FILE = config.get(section, 'log_file') + '/blood-' + BLOOD_LISTEN_OBJ + '.log'
DST_FL_POP = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_pop')
DST_FL_UIQ_OWN = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_own')
DST_FL_UIQ_HIS = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_his')
BUILDER_JS_PATH = 'nodejs/builder.js'

MIN_EP = 10000  # 预估MAU最小值，用于选取显著的pt
FB_API_VERSION = 'v2.12'
ACT_ID = 'act_' + ACT_UID
POST_HEADER = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Connection': 'keep-alive'
}
FB_HOST_URL = 'https://graph.facebook.com/v2.12/'
BID_MAX = 60000
BID_MIN = 5000
JSON_TMP_FILE1 = '/tmp/json_tmp_001' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE2 = '/tmp/json_tmp_002' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE3 = '/tmp/json_tmp_003' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE4 = '/tmp/json_tmp_004' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE5 = '/tmp/json_tmp_005' + BLOOD_LISTEN_OBJ + '.json'  # not used.
REPLY_TO = 'cador_delt_pro_stop_campaign'

# 配置mysql连续信息
MYSQL_HOST = config.get('mysql_conf', 'mysql_host')
MYSQL_PORT = int(config.get('mysql_conf', 'mysql_port'))
MYSQL_USER = config.get('mysql_conf', 'mysql_user')
MYSQL_PASSWORD = config.get('mysql_conf', 'mysql_password')
MYSQL_DB = config.get('mysql_conf', 'mysql_database')

# 配置logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(LOG_FILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

max_up_bid = [0.8, 0.8, 0.85, 0.9, 0.85, 0.8, 0.7, 0.8, 0.95, 0.9, 0.82, 0.6, 0.5, 0.4, 0.35, 0.3, 0.3, 0.4, 0.55, 0.6,
              0.65, 0.7, 0.8, 0.8]  # from 0 - 23
max_down_bid = [round(1 - i, 2) for i in max_up_bid]
bid_change_base = 5000  # 单位为美分
# 加载广告ID集合的数据
ad_collections = {}
ad_id_str = ''
ad_set_str = ''


def load_json(json_file):
    with open(json_file, 'r', encoding='UTF-8') as load_f:
        load_dict = json.load(load_f, object_pairs_hook=OrderedDict)
    return load_dict


def move_file(src_file, dst_file):
    if not os.path.isfile(src_file):
        print("%s not exist!" % src_file)
    else:
        f_path, f_name = os.path.split(dst_file)  # 分离文件名和路径
        if not os.path.exists(f_path):
            os.makedirs(f_path)  # 创建路径
        shutil.move(src_file, dst_file)  # 移动文件
        print("move %s -> %s" % (src_file, dst_file))


def save_json(json_file, json_obj):
    with open(json_file, "w") as f:
        json.dump(json_obj, f, indent=4)


def compose(data, is_utf8=False):
    dic = {'access_token': ACS_TK}
    for key in data:
        dic[key] = data[key]
    query_str = urllib.parse.urlencode(dic)
    if is_utf8:
        return query_str.encode('utf-8')
    else:
        return query_str


def get_ad_status(ad_ids_string):
    # 获得广告的状态
    str_cmd = 'sh shell-script/getStatus.sh "\\"fields=effective_status\\"" ' + ad_ids_string + ' > ' + JSON_TMP_FILE1
    out = os.system(str_cmd)
    ad_status = dict()
    if out == 0:
        print('get ad status success!')
        with open(JSON_TMP_FILE1, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                ad_status[json_obj['detail']['id']] = json_obj['detail']['effective_status']
    else:
        print('get ad status failure!')
    return ad_status


def get_insights_by_json(json_out):
    if len(json_out['data']) == 0:
        return 0, 0, 0
    spend = float(json_out['data'][0]['spend'])
    install = 0
    pay = 0
    if 'actions' not in json_out['data'][0]:
        return spend, install, pay
    else:
        for act_type in json_out['data'][0]['actions']:
            if act_type['action_type'] == 'mobile_app_install':
                install = int(act_type['value'])
            if act_type['action_type'] == 'app_custom_event.fb_mobile_purchase':
                pay = int(act_type['value'])
        return spend, install, pay


def get_ad_index():
    ad_status = get_ad_status(ad_id_str)
    # print(ad_status)
    # 获得广告的insights
    from_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    to_date = from_date
    str_cmd = 'sh shell-script/getIndex.sh "\\"fields=ad_id,spend,actions&time_range={\\\\"\\"since\\\\"\\":\\\\"\\"' + \
              from_date + \
              '\\\\"\\",\\\\"\\"until\\\\"\\":\\\\"\\"' + to_date + '\\\\"\\"}\\"" ' + ad_id_str + ' > ' + \
              JSON_TMP_FILE2
    out = os.system(str_cmd)
    ad_dict = dict()
    if out == 0:
        print("get ad index success!")
        with open(JSON_TMP_FILE2, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                if len(json_obj['detail']['data']) != 0:
                    if 'ad_id' in json_obj['detail']['data'][0]:
                        tmp_ad_id = json_obj['detail']['data'][0]['ad_id']
                        if tmp_ad_id in ad_status and ad_status[tmp_ad_id] == 'ACTIVE':
                            ad_dict[tmp_ad_id] = get_insights_by_json(json_obj['detail'])
    else:
        print("get ad index failure!")
    for ad_id in ad_status:
        if ad_id not in ad_dict:
            ad_dict[ad_id] = (0, 0, 0)
    return ad_dict


def listen_init():
    # 重置全局变量
    global ad_collections, ad_id_str, ad_set_str
    ad_collections = {}
    ad_id_str = ''
    ad_set_str = ''
    print('listen seeds:' + str(listen_seeds))
    print("初始化监控广告集合...")
    ad_collections_local = {}
    ad_id_str_local=''
    urllib3.disable_warnings()
    query = compose({'fields': 'name,adsets{ads}', 'limit': 1000})
    dst_url = FB_HOST_URL + ACT_ID + '/campaigns?{}'.format(query)
    while True:
        html = requests.get(dst_url, verify=False).text
        json_out = json.loads(html)
        if 'data' not in json_out:
            time.sleep(5)
        else:
            for node in json_out['data']:
                for header_string in listen_seeds:
                    if node['name'].startswith(header_string):
                        campaign_id = node['id']
                        adset_id = node['adsets']['data'][0]['id']
                        ad_id = node['adsets']['data'][0]['ads']['data'][0]['id']
                        ad_collections_local[ad_id] = {'campaign': campaign_id, 'adset': adset_id}
                        ad_id_str_local = ad_id_str_local + ad_id + ' '
            if 'next' in json_out['paging']:
                dst_url = json_out['paging']['next']
            else:
                break
    # 获得广告状态并选择ACTIVE的广告进行监控
    ad_status = get_ad_status(ad_id_str_local)
    for ad_id in ad_status:
        if ad_status[ad_id] == 'ACTIVE':
            ad_collections[ad_id] = ad_collections_local[ad_id]
            ad_id_str = ad_id_str + ad_id + ' '
            ad_set_str = ad_set_str + ad_collections[ad_id]['adset'] + ' '
    print("<------finished!------>")
    print("listen ads size " + str(len(ad_collections)))


def delete_ads(start_with_string):
    urllib3.disable_warnings()
    query = compose({'fields': 'name,adsets{ads}', 'limit': 1000})
    dst_url = FB_HOST_URL + ACT_ID + '/campaigns?{}'.format(query)
    campaign_set = list()
    while True:
        html = requests.get(dst_url, verify=False).text
        json_out = json.loads(html)
        if 'data' not in json_out:
            time.sleep(5)
        else:
            for node in json_out['data']:
                if node['name'].startswith(start_with_string):
                    campaign_id = node['id']
                    campaign_set.append(campaign_id)
            if 'next' in json_out['paging']:
                dst_url = json_out['paging']['next']
            else:
                break
    import nats_proc as ntp
    ntp.stop_campaign(campaign_set)
