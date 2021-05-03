import aioredis
import asyncio
from discord.ext import commands, tasks
from app.discordbot.bot import Bot
from app.utils.log import setup_logger
from app.utils import config

logger = setup_logger(__name__)

class Twitter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.redis = None
        self.redis_addr = None
        self.tweet_chan = 'tweet'
        self.follow_chan = 'follow'

    @commands.command()
    async def subscribe(self, ctx, username : str):
        logger.info(username)
        await self._subscribe(username)
        await self.redis.sadd(username, ctx.channel.id)
        await ctx.send(f"Subscribed to user: {username}")

    @tasks.loop(seconds=1.0)
    async def poll_redis(self):
        msgs = await self._receive()
        await self._handle_msgs(msgs)

    #@poll_redis.before_loop
    #async def before_poll_redis(self):
    #    logger.debug("waiting for cog to be ready")
    #    await self.bot.wait_until_ready()

    async def _subscribe(self, username):
        stream_msg = {
            'type': 'follow',
            'username': username
        }
        logger.debug(stream_msg)
        if self.redis is None:
            logger.error('redis not started')
            return
        await self.redis.xadd(self.follow_chan, stream_msg)

    async def _receive(self):
        if self.redis is None:
            logger.error('redis not started')
            return
        return await self.redis.xread([self.tweet_chan], timeout=1000)

    async def _handle_msgs(self, msgs):
        for msg in msgs:
            msg_data = msg[2] #msg = ('chan', 'time', data)
            link = ''
            if 'link' in msg_data:
                link = msg_data['link']
            else:
                continue
            if 'screen_name' in msg_data:
                subbed_chans = await self.redis.smembers(msg_data['screen_name'])
                for chan_id in subbed_chans:
                    chan = await self.bot.fetch_channel(int(chan_id))
                    await chan.send(link)

    async def _post(self, chan, link):
        await chan.send(link)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("starting redis connection")
        cfg = config.get_config()
        self.redis_addr = cfg["redis_uri"]
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')
        if self.redis is None:
            logger.error("redis not started")
        self.poll_redis.start()

def setup(bot):
    bot.add_cog(Twitter(bot))