import json
import utils as tool
import os


def select_pt():
    out_pt = []
    out = os.system("sh getEmau.sh " + tool.PTS_FL + " > " + tool.JSON_TMP_FILE3)
    if out == 0:
        print('get Emau info success!')
        with open(tool.JSON_TMP_FILE3, 'r', encoding='UTF-8') as json_file:
            lines = json_file.readlines()  # 读取全部内容 ，并以列表方式返回
        for line in lines:
            json_obj = json.loads(line)
            if json_obj['level'] == 30:
                if json_obj['detail']['result']['data'][0]['estimate_mau'] >= tool.MIN_EP:
                    out_pt.append(json_obj['detail']['pt'])
    else:
        print('get Emau info failure!')
    with open(tool.DST_FL_POP, 'w') as json_file:
        json.dump(out_pt, json_file, indent=4)
        # json_file.write(json.dumps(outpt))
    print(str(len(out_pt)) + ' pt saved.')
