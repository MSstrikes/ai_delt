from ptbuilder import unique_history, compare_pt, pt_select
import utils as tool
import json
import random
import time
import os


def build_pts(num):
    str_cmd = 'sh shell-script/buildpts.sh ' + str(num)
    out = os.system(str_cmd)
    if out == 0:
        print('build pts success!')
    else:
        print('build pts failure!')


def gen_pt(num, pt_pool=list()):
    build_pts(3 * num)
    pt_select.select_pt()
    compare_pt.unique_process()
    pts = unique_history.unique_his()

    out_pt = []
    for pt in pts:
        key = compare_pt.get_pt_key(pt)
        if key not in pt_pool:
            out_pt.append(pt)

    if len(out_pt) >= num:
        out = [out_pt[i] for i in random.sample(range(0, len(out_pt)), num)]
        return out
    else:
        if len(out_pt) > 0:
            t0 = list(out_pt)
            t0.extend(pt_pool)
            t = gen_pt(num - len(out_pt), t0)
            out_pt.extend(t)
            return out_pt
        else:
            return gen_pt(num)


def create_ads(num):
    pts = gen_pt(num)
    with open('nodejs/pts.json', 'w') as json_file:
        json.dump(pts, json_file, indent=4)
    print('new create ' + str(len(pts)) + ' pt saved.')
    # create ads.
    str_cmd = 'sh shell-script/createAds.sh'
    out = os.system(str_cmd)
    if out == 0:
        print('create ads success!')
        new_file = tool.DELIVERY_PTS_DIR + "/" + str(time.time()) + '.pts.json'
        tool.move_file('nodejs/pts.json', new_file)
        return 0
    else:
        print('create ads failure!')
        return -1

