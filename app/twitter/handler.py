import tweepy
import asyncio
import aioredis
import logging
from app.twitter.listener import TwitterListener
from app.utils.log import setup_logger

logger = setup_logger(__name__)

class TwitterHandler():
    def __init__(self, api_key, api_secret, access_token, access_token_secret, redis_addr):
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        self.listener = TwitterListener(redis_addr, loop=asyncio.get_event_loop())
        self.stream = None
        self.redis_addr = redis_addr
        self.redis = None
        self.tweet_chan = "tweet"
        self.follow_chan = "follow"
        self.following = {}

    async def run(self):
        logger.info("starting twitter handler")
        await self.start_redis()

        while True:
            msgs = await self._receive()
            logger.debug(msgs)
            update = False
            for msg in msgs:
                msg_data = msg[2] #msg = ('chan', 'time', data)
                if msg_data and "type" in msg_data:
                    if msg_data['type'] == "follow" and "username" in msg_data:
                        update = True if self._follow_user(msg_data['username']) else update
                    elif msg_data['type'] == "unfollow" and "username" in msg_data:
                        update = True if self._unfollow_user(msg_data['username']) else update
            if update and self.following:
                self.restart_stream()
                logger.debug("waiting 3s for stream to restart")
                await asyncio.sleep(3)
            else:
                self.close_stream()

    async def stop(self):
        self.close_stream()
        self.close_redis()
    
    async def start_redis(self):
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')
        await self.listener.start_redis()

    async def close_redis(self):
        await self.listener.close_redis()
        await self.redis.wait_closed()
    
    async def _receive(self):
        if self.redis is None:
            logger.error('redis not started')
            return
        return await self.redis.xread([self.follow_chan])

    def _get_user_id(self, screen_name):
        user = self.api.get_user(screen_name)
        if user:
            logger.debug(f"{screen_name} - {user.id_str}")
            return user.id_str
        logger.debug("failed to get user")
        return None

    def _follow_user(self, screen_name):
        added = False
        if screen_name not in self.following:
            id_str = self._get_user_id(screen_name)
            if id_str:
                self.following[screen_name] = id_str
                added = True
        return added

    def follow_users(self, screen_names):
        added = False
        for name in screen_names:
            if self._follow_user(name):
                added = True
        return added

    def _unfollow_user(self, screen_name):
        unfollowed = False
        if screen_name in self.following:
            del self.following[screen_name]
            unfollowed = True
        return unfollowed

    def unfollow_users(self, screen_names):
        unfollowed = False
        for name in screen_names:
            if self._unfollow_user(name):
                unfollowed = True
        return unfollowed

    def start_stream(self):
        if not self.stream and self.following:
            logger.debug("hi")
            self.stream = tweepy.Stream(self.api.auth, self.listener, retry_420=3 * 60)
            self.stream.sample(languages=['ja'], is_async=True)
            #self.stream.filter(follow=['455178621'], is_async=True)
            #self.stream.filter(follow=self.following.values(), is_async=True)

    def close_stream(self):
        if self.stream and self.stream.running:
            self.stream.disconnect()
            self.stream = None

    def restart_stream(self):
        logger.debug("restarting twitter stream")
        self.close_stream()
        self.start_stream()
