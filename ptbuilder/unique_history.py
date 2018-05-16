import os
import utils as tool
from ptbuilder import compare_pt


def unique_his():
    exist_keys = []
    pt_list = os.listdir(tool.DELIVERY_PTS_DIR)
    for i in range(0, len(pt_list)):
        path = os.path.join(tool.DELIVERY_PTS_DIR, pt_list[i])
        if os.path.isfile(path):
            his_json = tool.load_json(path)
            for pt in his_json:
                key = compare_pt.get_pt_key(pt)
                if key not in exist_keys:
                    exist_keys.append(key)
    cur_json = tool.load_json(tool.DST_FL_UIQ_OWN)
    out_pt = []
    for pt in cur_json:
        key = compare_pt.get_pt_key(pt)
        if key not in exist_keys:
            out_pt.append(pt)
    return out_pt
