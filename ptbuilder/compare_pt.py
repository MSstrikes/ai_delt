import utils as tool
import json
import hashlib


def get_pt_key(pt):
    hl = hashlib.md5()
    tmp = ''
    tmp = tmp + str(pt['adset_spec']['targeting'])
    # tmp = tmp + str(pt['adset_spec']['targeting']['age_max'])
    # tmp = tmp + '-' + str(pt['adset_spec']['targeting']['age_min'])
    # tmp = tmp + '-' + json.dumps(pt['adset_spec']['targeting']['genders'])
    # tmp = tmp + '-' + json.dumps(pt['adset_spec']['targeting']['geo_locations']['location_types'])
    # tmp = tmp + '-' + json.dumps(pt['adset_spec']['targeting']['custom_audiences'])

    # if 'wireless_carrier' in pt['adset_spec']['targeting']:
    #     tmp = tmp + '-g'
    # else:
    #     tmp = tmp + '-s'

    tmp = tmp + '-' + json.dumps(pt['creative'])
    hl.update(tmp.encode(encoding='utf-8'))
    return hl.hexdigest()


def unique_process():
    feature = {}
    load_dict = tool.load_json(tool.DST_FL_POP)
    for pt in load_dict:
        key = get_pt_key(pt)
        if key not in feature:
            feature[key] = pt

    print('--- ' + str(len(feature)) + ' ---')
    out_pt = []
    for key in feature:
        out_pt.append(feature[key])
    with open(tool.DST_FL_UIQ_OWN, 'w') as json_file:
        json.dump(out_pt, json_file, indent=4)
