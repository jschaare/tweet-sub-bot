import asyncio
import aioredis
import logging
import sys
from app.utils import config

# create logger
logger = logging.getLogger("pub")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

async def publisher(server_addr, channel_name):
    redis = await aioredis.create_redis_pool(server_addr, encoding='utf-8')
    i = 0
    while True:
        await asyncio.sleep(5)
        publish(redis, channel_name, i)
        i += 1
    redis.close()
    await redis.wait_closed()

def publish(redis, chan, msg):
    stream_msg = {'msg': msg}
    logger.info(stream_msg)
    return redis.xadd(chan, stream_msg)

async def test(server_addr, channel_name):
    redis = await aioredis.create_redis_pool(server_addr, encoding='utf-8')
    await asyncio.sleep(10)
    stream_msg = {
        'type': 'follow',
        'username': 'Mudkipz16'
    }
    logger.info(stream_msg)
    await redis.xadd(channel_name, stream_msg)
    await asyncio.sleep(60)
    stream_msg = {
        'type': 'unfollow',
        'username': 'Mudkipz16'
    }
    logger.info(stream_msg)
    await redis.xadd(channel_name, stream_msg)
    await redis.wait_closed()


if __name__ == "__main__":
    logger.info("starting publisher")
    cfg = config.get_config()
    addr = addr = cfg['redis_uri']
    chan = "follow"
    asyncio.run(test(addr, chan))