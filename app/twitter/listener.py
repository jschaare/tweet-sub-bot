import tweepy
import asyncio
import aioredis
from app.utils.log import setup_logger

logger = setup_logger(__name__)

class TwitterListener(tweepy.StreamListener):
    def __init__(self, redis_addr, chan):
        super().__init__()
        self.redis = None
        self.redis_addr = redis_addr
        self.tweet_chan = chan
 
    def on_status(self, status):
        logger.info('Tweet text: ' + status.text)
        data = {
            'id_str': status.id_str,
            'text': status.text,
            'screen_name': status.user.screen_name,
            'link': f"https://twitter.com/twitter/statuses/{status.id_str}"
        }
        asyncio.run(self._publish(data))
        return True
 
    def on_error(self, status_code):
        logger.error('Got an error with status code: ' + str(status_code))
        return True
 
    def on_timeout(self):
        logger.error('Timeout...')
        return True

    async def start(self):
        logger.info("starting TwitterListener")
        await self._start_redis()

    async def _publish(self, data):
        if self.redis is None:
            logger.error('redis not started')
            return
        await self.redis.xadd(self.tweet_chan, data)

    async def _start_redis(self):
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')

    async def _close_redis(self):
        await self.redis.wait_closed()