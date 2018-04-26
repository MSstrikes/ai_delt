import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import time
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout
import json
import utils as tool


def compose(data, isutf8=False):
    dict = {'access_token': tool.ACS_TK}
    for key in data:
        dict[key] = data[key]
    query = urllib.parse.urlencode(dict)
    if isutf8:
        return query.encode('utf-8')
    else:
        return query


def get_esmau(target_val, opt_val):
    query = compose({'targeting_spec': target_val, 'optimization_goal': opt_val})
    out = urllib.request.urlopen(tool.FB_HOST_URL + tool.ACT_ID + '/delivery_estimate?{}'.format(query))
    jout = json.loads(out.read().decode("utf-8"))
    return jout['data'][0]['estimate_mau']


def url_get(url_open_link):
    while True:
        try:
            out = urllib.request.urlopen(url_open_link)
        except HTTPError as e:
            tool.logger.info('The server couldn\'t fulfill  the request.  ')
            tool.logger.info('Error code: ' + str(e.code))
            time.sleep(10)
        except URLError as e:
            tool.logger.info('We failed to reach a server.')
            tool.logger.info('Reason: ' + str(e.reason))
            print('', e.reason)
            time.sleep(10)
        except TimeoutError as e:
            tool.logger.info('connect time out...')
            tool.logger.info('Error code: ' + str(e.code))
            print('', e.reason)
            time.sleep(10)
        else:
            return out.read().decode("utf-8")


def get_insights(ad_id):
    time_obj = {}
    time_obj['since'] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    time_obj['until'] = time_obj['since']
    query = compose({'time_range': json.dumps(time_obj), 'fields': 'spend,actions'})
    out = url_get(tool.FB_HOST_URL + ad_id + '/insights?{}'.format(query))
    jout = json.loads(out)
    if len(jout['data']) == 0:
        return 0, 0, 0
    spend = float(jout['data'][0]['spend'])
    install = 0
    pay = 0
    if 'actions' not in jout['data'][0]:
        return spend, install, pay
    else:
        for act_type in jout['data'][0]['actions']:
            if act_type['action_type'] == 'mobile_app_install':
                install = int(act_type['value'])
            if act_type['action_type'] == 'app_custom_event.fb_mobile_purchase':
                pay = int(act_type['value'])
        return spend, install, pay


def get_adset_id(ad_id):
    query = compose({'fields': 'adset_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    jout = json.loads(out)
    return jout['adset_id']


def get_compaign_id(ad_id):
    query = compose({'fields': 'campaign_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    jout = json.loads(out)
    return jout['campaign_id']


def run(loop, jval):
    nc = NATS()
    yield from nc.connect(io_loop=loop, servers=[tool.NATS_URL])
    try:
        response = yield from nc.request("fb_api.sync.request", jval, 60)  # 60秒
        print("Received response: {message}".format(message=response.data.decode()))
    except ErrTimeout:
        print("Request timed out")
    yield from asyncio.sleep(1, loop=loop)
    yield from nc.close()


def jsonCompose(compaignId):
    dict = {}
    dict['apiVersion'] = tool.FB_API_VERSION
    dict['path'] = compaignId
    dict['method'] = tool.METHOD_POST
    dict['body'] = tool.STATUS_PAUSE

    out = {}
    out['token'] = tool.ACS_TK
    out['request'] = dict
    out['account'] = tool.ACT_UID
    out['priority'] = 1

    j = json.dumps(out)

    return j.encode(encoding="utf-8")


def stopCompaign(compaignId):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, jsonCompose(compaignId)))
    # loop.close()


def update_bid_amount(adset_id, bid_amount):
    url = tool.FB_HOST_URL + adset_id
    data = compose({'bid_amount': bid_amount}, isutf8=True)
    req = urllib.request.Request(url, headers=tool.POST_HEADER, data=data)
    page = urllib.request.urlopen(req).read()
    page = page.decode('utf-8')
    print(page)


def get_bid_amount(adset_id):
    query = compose({'fields': 'bid_amount'})
    out = url_get(tool.FB_HOST_URL + adset_id + '?{}'.format(query))
    jout = json.loads(out)
    return jout['bid_amount']
