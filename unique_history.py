import os
import utils as tool
import compare_pt
import json


def uniqueHis():
    exist_keys = []
    list = os.listdir(tool.DELIVERY_PTS_DIR)
    for i in range(0, len(list)):
        path = os.path.join(tool.DELIVERY_PTS_DIR, list[i])
        if os.path.isfile(path):
            his_json = tool.loadJson(path)
            for pt in his_json:
                key = compare_pt.get_pt_key(pt)
                if key not in exist_keys:
                    exist_keys.append(key)
    cur_json = tool.loadJson(tool.DST_FL_UIQ_OWN)
    outpt = []
    for pt in cur_json:
        key = compare_pt.get_pt_key(pt)
        if key not in exist_keys:
            outpt.append(pt)
    with open(tool.DST_FL_UIQ_HIS, 'w') as json_file:
        json.dump(outpt, json_file, indent=4)
    print(str(len(outpt)) + " pt saved.")
