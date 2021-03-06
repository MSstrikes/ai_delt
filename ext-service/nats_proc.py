import asyncio
import json
from nats.aio.client import Client as NATS
import utils as tool


def json_compose(campaign_id, cmd_type):
    json_obj = {
        'token': tool.ACS_TK,
        'request': {
            'apiVersion': tool.FB_API_VERSION,
            'path': campaign_id,
            'body': 'status=' + cmd_type,  # DELETED,PAUSED
            'method': "POST"
        },
        'account': tool.ACT_UID,
        'priority': 1,
        'noRetry': True,
        'replyTo': tool.REPLY_TO,
        'payload': campaign_id
    }
    j = json.dumps(json_obj)
    return j.encode(encoding="utf-8")


async def run(loop, obj_ids, cmd_type):
    nc = NATS()
    await nc.connect(io_loop=loop, servers=[tool.NAT_URL])
    for req in obj_ids:
        print("campaign {idx} is closed.".format(idx=req))
        await nc.publish("fb_api.async.request", json_compose(req, cmd_type))
    await asyncio.sleep(10)  # 10秒够用了，还不知道怎么确定所有请求发送成功
    await nc.close()


def stop_campaign(campaign_ids, cmd_type):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop, campaign_ids, cmd_type))
    except Exception as e:
        raise e
