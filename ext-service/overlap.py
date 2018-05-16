import json
import asyncio
from nats.aio.client import Client as NATS


def json_compose():
    json_obj = {
        'originId': '23842749273890541',
        'targetId': '23842749273900541',
        'businessId': '165781974078066',
        'accountId': '2035998863338806'
    }
    j = json.dumps(json_obj)
    return j.encode(encoding="utf-8")


async def run(loop, service_type, json_bytes):
    service = ''
    if service_type == "get_overlap":
        service = 'fb-audience-service.audience.overlap'
    if service_type == "create_audience":
        service = 'fb-create-audience.audience.create'
    nc = NATS()
    await nc.connect(io_loop=loop, servers=['nats://52.34.215.198:20010'])
    out = await nc.request(service, timeout=60, payload=json_bytes)
    print(out.data)


def get_overlap():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(loop, 'get_overlap', json_compose()))
    except Exception as e:
        raise e


def create_audience():
    loop = asyncio.get_event_loop()
    out = json.dumps({
        'targeting': {'genders': [2], 'age_min': 18, 'age_max': 55, 'custom_audiences': [
            {'id': '23842749261760541', 'name': 'Lookalike (US, 2% to 5%) - 0130_all_value_gt2k_T-paytime'}],
                      'geo_locations': {'countries': ['US'], 'location_types': ['home', 'recent']},
                      'publisher_platforms': ['facebook', 'audience_network'], 'facebook_positions': ['feed'],
                      'device_platforms': ['mobile'], 'audience_network_positions': ['classic'],
                      'excluded_publisher_categories': ['debated_social_issues', 'tragedy_and_conflict'],
                      'user_device': ['galaxy note 7', '5t', 'g5', 'g6', 'galaxy note 8', 'galaxy note 8.0',
                                      'galaxy s7', 'galaxy s7 active', 'galaxy s7 edge', 'galaxy s8', 'galaxy s8+',
                                      'mate 10 lite', 'mate 10 pro', 'mate 9', 'moto z droid', 'moto z play dual',
                                      'nexus 6p', 'nova 2i', 'nova lite', 'p10', 'p10 lite', 'p9', 'p9 lite', 'pixel',
                                      'pixel 2', 'pixel 2 xl', 'pixel xl', 'r9s', 'u ultra', 'v20', 'v7', 'v7+',
                                      'xperia c5 ultra', 'xperia c5 ultra dual', 'xperia e3', 'xperia e3 dual',
                                      'xperia xz'], 'user_os': ['Android_ver_6.0_and_above'],
                      'app_install_state': 'not_installed'},
        'businessId': '165781974078066',
        'accountId': '2035998863338806'
    }).encode(encoding="utf-8")
    try:
        loop.run_until_complete(run(loop, 'create_audience', out))
    except Exception as e:
        raise e


create_audience()
