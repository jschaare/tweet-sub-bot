import tweepy
import asyncio
import aioredis
from app.utils.log import setup_logger

logger = setup_logger(__name__)

class TwitterListener(tweepy.StreamListener):
    def __init__(self, redis_addr, loop):
        super().__init__()
        self.loop = loop
        self.redis = None
        self.redis_addr = redis_addr
        self.tweet_chan = "tweet"
 
    def on_status(self, status):
        logger.debug('Tweet text: ' + status.text)
        data = {
            'id_str': status.id_str,
            'text': status.text,
            'screen_name': status.user.screen_name,
            'link': f"https://twitter.com/twitter/statuses/{status.id_str}"
        }
        future = asyncio.run_coroutine_threadsafe(self.publish(data), self.loop)
        future.result()
        return True
 
    def on_error(self, status_code):
        logger.error('Got an error with status code: ' + str(status_code))
        return True
 
    def on_timeout(self):
        logger.error('Timeout...')
        return True

    async def publish(self, data):
        logger.debug(data)
        if self.redis is None:
            logger.error('redis not started')
            return
        await self.redis.xadd(self.tweet_chan, data)
        logger.debug("sent")

    async def start_redis(self):
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')

    async def close_redis(self):
        await self.redis.wait_closed()