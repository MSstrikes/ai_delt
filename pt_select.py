import json
import utils as tool
import facebook_api as fp


def selectPt():
    outpt = []
    with open(tool.PTS_FL, 'r', encoding='UTF-8') as load_f:
        load_dict = json.load(load_f)
    for pt in load_dict:
        target_val = json.dumps(pt['adset_spec']['targeting'])
        opt_val = pt['adset_spec']['optimization_goal']
        ep_val = fp.get_esmau(target_val, opt_val)
        if ep_val >= tool.MIN_EP:
            print('---> ' + str(ep_val))
            outpt.append(pt)
    with open(tool.DST_FL_POP, 'w') as json_file:
        json.dump(outpt, json_file, indent=4)
        # json_file.write(json.dumps(outpt))
    print(str(len(outpt)) + ' pt saved.')
