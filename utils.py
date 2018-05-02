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

PTS_FL = config.get(section, 'pts_file')
ACS_TK = config.get(section, 'access_token')
ACT_UID = config.get(section, 'account_id')
NAT_URL = config.get(section, 'nat_url')
DELIVERY_PTS_DIR = config.get(section, 'delivery_dir')
BLOOD_LISTEN_OBJ = config.get(section, 'ad_seeds')
LOG_FILE = config.get(section, 'log_file') + '/blood-' + BLOOD_LISTEN_OBJ + '.log'
DST_FL_POP = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_pop')
DST_FL_UIQ_OWN = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_own')
DST_FL_UIQ_HIS = '/tmp/' + BLOOD_LISTEN_OBJ + config.get(section, 'dst_his')

MIN_EP = 100000  # 预估MAU最小值，用于选取显著的pt
FB_API_VERSION = 'v2.12'
ACT_ID = 'act_' + ACT_UID
POST_HEADER = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Connection': 'keep-alive'
}
FB_HOST_URL = 'https://graph.facebook.com/v2.12/'
BID_STEP = 5000
BID_MAX = 60000
JSON_TMP_FILE1 = '/tmp/json_tmp_001' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE2 = '/tmp/json_tmp_002' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE3 = '/tmp/json_tmp_003' + BLOOD_LISTEN_OBJ + '.json'
JSON_TMP_FILE4 = '/tmp/json_tmp_004' + BLOOD_LISTEN_OBJ + '.json'
REPLY_TO = 'cador_delt_pro_stop_campaign'
TOP_N_UPDATE_BID = 10
DEFAULT_BID = 10000

# 配置logger
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(LOG_FILE)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


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


# 加载广告ID集合的数据
ad_collections = {}
ad_id_str = ''
ad_set_str = ''


def ad_init():
    print('ID:' + BLOOD_LISTEN_OBJ)
    print("初始化监控广告集合...")
    urllib3.disable_warnings()
    query = compose({'fields': 'name,adsets{ads}', 'limit': 1000})
    dst_url = FB_HOST_URL + ACT_ID + '/campaigns?{}'.format(query)
    cset = []
    while True:
        html = requests.get(dst_url, verify=False).text
        json_out = json.loads(html)
        if 'data' not in json_out:
            time.sleep(5)
        else:
            for node in json_out['data']:
                if node['name'].startswith(BLOOD_LISTEN_OBJ):
                    campaign_id = node['id']
                    cset.append(campaign_id)
                    adset_id = node['adsets']['data'][0]['id']
                    ad_id = node['adsets']['data'][0]['ads']['data'][0]['id']
                    ad_collections[ad_id] = {'campaign': campaign_id, 'adset': adset_id}
                    global ad_id_str, ad_set_str
                    ad_id_str = ad_id_str + ad_id + ' '
                    ad_set_str = ad_set_str + adset_id + ' '
            if 'next' in json_out['paging']:
                dst_url = json_out['paging']['next']
            else:
                print("<------finished!------>")
                print("listen ads size " + str(len(ad_collections)))
                break
