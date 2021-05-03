import asyncio
import aioredis
import logging
from app.utils import config

logger = logging.getLogger("sub")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

async def subscriber(server_addr, channel_name):
    redis = await aioredis.create_redis_pool(server_addr, encoding='utf-8')

    #[channel] = await redis.psubscribe(channel_name)

    #while True:
    #    msg = await channel.get()
    #    logger.info(msg)
    #return
    while True:
        msg = await redis.xread(["tweet"])
        logger.info(msg)
    return

if __name__ == "__main__":
    logger.info("starting subscriber")
    cfg = config.get_config()
    addr = cfg['redis_uri']
    chan = "tweet"
    asyncio.run(subscriber(addr, chan))