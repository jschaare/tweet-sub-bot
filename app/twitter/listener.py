import tweepy
import asyncio
import aioredis
from app.utils.log import setup_logger

logger = setup_logger(__name__)

class TwitterListener(tweepy.StreamListener):
    def __init__(self, handler, loop):
        super().__init__()
        self.handler = handler
        self.loop = loop
 
    def on_status(self, status):
        logger.debug('Tweet text: ' + status.text)
        data = {
            'id_str': status.id_str,
            'text': status.text,
            'screen_name': status.user.screen_name,
            'link': f"https://twitter.com/twitter/statuses/{status.id_str}"
        }
        asyncio.run_coroutine_threadsafe(self.handler(data), self.loop)
        return True
 
    def on_error(self, status_code):
        logger.error('Got an error with status code: ' + str(status_code))
        return True
 
    def on_timeout(self):
        logger.error('Timeout...')
        return True