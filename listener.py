import asyncio
from nats.aio.client import Client as NATS
import os

# 设置环境变量
os.environ["CONFIG_FILE_PATH"] = '/Users/youhaolin/config.ini'
import utils as tool


async def listen(loop):
    nc = NATS()
    await nc.connect(io_loop=loop, servers=[tool.NAT_URL])

    async def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    await nc.subscribe(tool.REPLY_TO, cb=message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(listen(loop))
        loop.run_forever()
    except Exception as e:
        raise e
    finally:
        loop.close()
