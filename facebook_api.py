import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import time
import asyncio
from nats.aio.client import Client as nats
from nats.aio.errors import ErrTimeout
import json
import utils as tool


def compose(data, is_utf8=False):
    dic = {'access_token': tool.ACS_TK}
    for key in data:
        dic[key] = data[key]
    query = urllib.parse.urlencode(dic)
    if is_utf8:
        return query.encode('utf-8')
    else:
        return query


def get_estimate_mau(target_val, opt_val):
    query = compose({'targeting_spec': target_val, 'optimization_goal': opt_val})
    out = urllib.request.urlopen(tool.FB_HOST_URL + tool.ACT_ID + '/delivery_estimate?{}'.format(query))
    json_out = json.loads(out.read().decode("utf-8"))
    return json_out['data'][0]['estimate_mau']


def url_get(url_open_link):
    while True:
        try:
            out = urllib.request.urlopen(url_open_link)
        except HTTPError as e:
            tool.logger.info('The server could n\'t fulfill  the request.  ')
            tool.logger.info('Error code: ' + str(e.code))
            print('', e.reason)
            time.sleep(10)
        except URLError as e:
            tool.logger.info('We failed to reach a server.')
            tool.logger.info('Reason: ' + str(e.reason))
            print('', e.reason)
            time.sleep(10)
        except TimeoutError:
            tool.logger.info('connect time out...')
            time.sleep(10)
        else:
            return out.read().decode("utf-8")


def get_insights_by_json(json_out):
    if len(json_out['data']) == 0:
        return 0, 0, 0
    spend = float(json_out['data'][0]['spend'])
    install = 0
    pay = 0
    if 'actions' not in json_out['data'][0]:
        return spend, install, pay
    else:
        for act_type in json_out['data'][0]['actions']:
            if act_type['action_type'] == 'mobile_app_install':
                install = int(act_type['value'])
            if act_type['action_type'] == 'app_custom_event.fb_mobile_purchase':
                pay = int(act_type['value'])
        return spend, install, pay


def get_insights(ad_id):
    time_obj = {'since': time.strftime('%Y-%m-%d', time.localtime(time.time()))}
    time_obj['until'] = time_obj['since']
    query = compose({'time_range': json.dumps(time_obj), 'fields': 'spend,actions'})
    out = url_get(tool.FB_HOST_URL + ad_id + '/insights?{}'.format(query))
    json_out = json.loads(out)
    return get_insights_by_json(json_out)


def get_ad_status(ad_id):
    query = compose({'fields': 'status'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['status']


def get_adset_id(ad_id):
    query = compose({'fields': 'adset_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['adset_id']


def get_campaign_id(ad_id):
    query = compose({'fields': 'campaign_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['campaign_id']


def run(loop, json_val):
    nc = nats()
    yield from nc.connect(io_loop=loop, servers=[tool.NAT_URL])
    try:
        response = yield from nc.request("fb_api.sync.request", json_val, 60)  # 60秒
        print("Received response: {message}".format(message=response.data.decode()))
    except ErrTimeout:
        print("Request timed out")
    yield from asyncio.sleep(1, loop=loop)
    yield from nc.close()


def json_compose(campaign_id):
    dic = {'apiVersion': tool.FB_API_VERSION, 'path': campaign_id, 'method': tool.METHOD_POST,
           'body': tool.STATUS_PAUSE}
    out = {'token': tool.ACS_TK, 'request': dic, 'account': tool.ACT_UID, 'priority': 1}
    j = json.dumps(out)
    return j.encode(encoding="utf-8")


def stop_campaign(campaign_id):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, json_compose(campaign_id)))
    # loop.close()


def update_bid_amount(ad_set_id, bid_amount):
    url = tool.FB_HOST_URL + ad_set_id
    data = compose({'bid_amount': bid_amount}, is_utf8=True)
    while True:
        try:
            req = urllib.request.Request(url, headers=tool.POST_HEADER, data=data)
            page = urllib.request.urlopen(req).read()
            page = page.decode('utf-8')
        except HTTPError as e:
            tool.logger.info('The server could n\'t fulfill  the request.  ')
            tool.logger.info('Error code: ' + str(e.code))
            print('', e.reason)
            time.sleep(10)
        except URLError as e:
            tool.logger.info('We failed to reach a server.')
            tool.logger.info('Reason: ' + str(e.reason))
            print('', e.reason)
            time.sleep(10)
        except TimeoutError:
            tool.logger.info('connect time out...')
            time.sleep(10)
        else:
            print('adset ' + ad_set_id + ' update bid amount to ' + str(bid_amount))
            break


def get_bid_amount(ad_set_id):
    query = compose({'fields': 'bid_amount'})
    out = url_get(tool.FB_HOST_URL + ad_set_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['bid_amount']
