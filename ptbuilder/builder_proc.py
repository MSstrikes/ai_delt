from ptbuilder import builder_service as bs
import json
import utils as tool

rep_dict = {
    "`{python::get_image_hash}`": {'type': 'json', 'value': bs.get_image_hash()},
    "`{python::get_devices}`": {'type': 'json', 'value': bs.get_devices()},
    "`{python::get_creative('en')}`": {'type': 'json', 'value': bs.get_creative('en')},
    "\"{)(}": {'type': 'string', 'value': ''},
    "{)(}\"": {'type': 'string', 'value': ''},
    "`{python::get_behavoirs}`": {'type': 'json', 'value': bs.get_behavoirs()}
}


def gen_builder():
    with open(r"ptbuilder/builder_template.js", "r", encoding="utf-8") as f:
        # 为a+模式时，因为为追加模式，指针已经移到文尾，读出来的是一个空字符串。
        ftext = f.read()
    for key in rep_dict:
        value = rep_dict[key]
        if "json" == value.get('type'):
            ftext = ftext.replace(key, json.dumps(value.get('value')))
        if "string" == value.get('type'):
            ftext = ftext.replace(key, value.get('value'))
    with open(tool.BUILDER_JS_PATH, 'w', encoding="utf-8") as js_file:
        js_file.write(ftext)
        js_file.close()
    print('builder.js generated!')
