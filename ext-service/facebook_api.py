import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
import time
import json
import utils as tool
import urllib3
import requests

urllib3.disable_warnings()

def get_estimate_mau(target_val, opt_val):
    query = tool.compose({'targeting_spec': target_val, 'optimization_goal': opt_val})
    out = urllib.request.urlopen(tool.FB_HOST_URL + tool.ACT_ID + '/delivery_estimate?{}'.format(query))
    json_out = json.loads(out.read().decode("utf-8"))
    return json_out['data'][0]['estimate_mau']


def url_get(url_open_link, options_decode=True):
    while True:
        try:
            out = requests.get(url_open_link, verify=False).text
            if options_decode == False:
                return out
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


def get_insights(ad_id):
    time_obj = {'since': time.strftime('%Y-%m-%d', time.localtime(time.time()))}
    time_obj['until'] = time_obj['since']
    query = tool.compose({'time_range': json.dumps(time_obj), 'fields': 'spend,actions'})
    out = url_get(tool.FB_HOST_URL + ad_id + '/insights?{}'.format(query))
    json_out = json.loads(out)
    return tool.get_insights_by_json(json_out)


def get_ad_status(ad_id):
    query = tool.compose({'fields': 'status'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['status']


def get_adset_id(ad_id):
    query = tool.compose({'fields': 'adset_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['adset_id']


def get_campaign_id(ad_id):
    query = tool.compose({'fields': 'campaign_id'})
    out = url_get(tool.FB_HOST_URL + ad_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['campaign_id']


def update_bid_amount(ad_set_id, bid_amount):
    url = tool.FB_HOST_URL + ad_set_id
    data = tool.compose({'bid_amount': bid_amount}, is_utf8=True)
    while True:
        try:
            requests.post(url, data=data)
            # req = urllib.request.Request(url, headers=tool.POST_HEADER, data=data)
            # page = urllib.request.urlopen(req).read()
            # page = page.decode('utf-8')
        except Exception:
            tool.logger.info('exception...')
            time.sleep(10)
        else:
            print('adset ' + ad_set_id + ' update bid amount to ' + str(bid_amount))
            break


def get_bid_amount(ad_set_id):
    query = tool.compose({'fields': 'bid_amount'})
    out = url_get(tool.FB_HOST_URL + ad_set_id + '?{}'.format(query))
    json_out = json.loads(out)
    return json_out['bid_amount']
