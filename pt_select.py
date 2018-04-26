import json
import utils as tool
import facebook_api as fp


def select_pt():
    out_pt = []
    with open(tool.PTS_FL, 'r', encoding='UTF-8') as load_f:
        load_dict = json.load(load_f)
    for pt in load_dict:
        target_val = json.dumps(pt['adset_spec']['targeting'])
        opt_val = pt['adset_spec']['optimization_goal']
        ep_val = fp.get_estimate_mau(target_val, opt_val)
        if ep_val >= tool.MIN_EP:
            print('---> ' + str(ep_val))
            out_pt.append(pt)
    with open(tool.DST_FL_POP, 'w') as json_file:
        json.dump(out_pt, json_file, indent=4)
    print(str(len(out_pt)) + ' pt saved.')
