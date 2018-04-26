import json
from collections import OrderedDict
import os
import shutil
import logging

PTS_FL = '/Users/youhaolin/ai_adt/data/pts.json'
LOG_FILE = 'logs/blood.log'
ACS_TK = 'EAAIzxloXbZCEBALoTpDg2QGasR9JvCR41oAl44OIClJxr7uikwI0PNHxyU0MYHvgNKwPCDOiiZACrKZA72c5ckYlALHybCue9NABpzANvjWsONWQWMqhZA95rPCvtWfftbGcTZByObOZBUJjW9lcPlpNLeHi2ZC2ZAUZD'
MIN_EP = 100000
DST_FL_POP = '/tmp/pop.json'
DST_FL_UIQ_OWN = '/tmp/unique_own.json'
DST_FL_UIQ_HIS = '/tmp/unique_his.json'
FB_API_VERSION = 'v2.12'
METHOD_POST = 'POST'
ACT_UID = '2035998863338806'
ACT_ID = 'act_' + ACT_UID
STATUS_PAUSE = 'status=PAUSED'
NATS_URL = 'nats://52.34.215.198:20002'
DELIVERY_PTS_DIR = '/Users/youhaolin/ai_adt/data/delivery_pts'
BLOOD_LISTEN_OBJ = '/Users/youhaolin/Downloads/export_20180425_1832.csv'
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


def loadJson(json_file):
    with open(json_file, 'r', encoding='UTF-8') as load_f:
        load_dict = json.load(load_f, object_pairs_hook=OrderedDict)
    return load_dict


def movefile(srcfile, dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!" % (srcfile))
    else:
        fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)  # 创建路径
        shutil.move(srcfile, dstfile)  # 移动文件
        print("move %s -> %s" % (srcfile, dstfile))


def saveJson(json_file, jsonObj):
    with open(json_file, "w") as f:
        json.dump(jsonObj, f, indent=4)
