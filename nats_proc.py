import asyncio
import json
from nats.aio.client import Client as NATS
import utils as tool


def json_compose(campaign_id):
    json_obj = {
        'token': tool.ACS_TK,
        'request': {
            'apiVersion': tool.FB_API_VERSION,
            'path': campaign_id,
            'body': 'status=PAUSED',
            'method': "POST"
        },
        'account': tool.ACT_UID,
        'priority': 1,
        'noRetry': True,
        'replyTo': tool.REPLY_TO
    }
    j = json.dumps(json_obj)
    return j.encode(encoding="utf-8")


async def run(loop, reqs):
    nc = NATS()
    await nc.connect(io_loop=loop, servers=[tool.NAT_URL])
    for req in reqs:
        print("campaign {idx} is closed.".format(idx=req))
        await nc.publish("fb_api.async.request", json_compose(req))
    nc.close()


def stop_campaign(campaign_ids):
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop, campaign_ids))
    except Exception as e:
        raise e
