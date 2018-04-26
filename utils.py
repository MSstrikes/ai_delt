import json
from collections import OrderedDict
import os
import shutil
import logging
import configparser

section = 'base_conf'
config = configparser.ConfigParser()
config.read("/Users/youhaolin/config.ini")

PTS_FL = config.get(section, 'pts_file')
LOG_FILE = config.get(section, 'log_file')
ACS_TK = config.get(section, 'access_token')
DST_FL_POP = config.get(section, 'dst_pop')
DST_FL_UIQ_OWN = config.get(section, 'dst_own')
DST_FL_UIQ_HIS = config.get(section, 'dst_his')
ACT_UID = config.get(section, 'account_id')
NAT_URL = config.get(section, 'nat_url')
DELIVERY_PTS_DIR = config.get(section, 'delivery_dir')
BLOOD_LISTEN_OBJ = config.get(section, 'ad_seeds')

MIN_EP = 100000
FB_API_VERSION = 'v2.12'
METHOD_POST = 'POST'
ACT_ID = 'act_' + ACT_UID
STATUS_PAUSE = 'status=PAUSED'
POST_HEADER = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Connection': 'keep-alive'
}
FB_HOST_URL = 'https://graph.facebook.com/v2.12/'
BID_STEP = 5000
BID_MAX = 60000

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
