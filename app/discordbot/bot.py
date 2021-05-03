
import datetime
import aioredis
import asyncio
from discord.ext import commands
from app.utils import config
from app.utils.log import setup_logger

logger = setup_logger(__name__)

class Bot(commands.Bot):
    # Subclass of discord.ext.commands.Bot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_addr = None
        self.redis = None

    def add_cog(self, cog):
        super().add_cog(cog)
        logger.info(f"Cog loaded: {cog.qualified_name}")

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
            logger.info(self.guilds)
            for guild in self.guilds:
                for channel in guild.text_channels:
                    logger.info(channel)
        
        logger.info("starting redis connection")
        cfg = config.get_config()
        self.redis_addr = cfg["redis_uri"]
        logger.debug(self.redis_addr)
        #await self._start_redis()

        logger.info(f'Ready: {self.user} (ID: {self.user.id})')

    async def _start_redis(self):
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')
        if self.redis is None:
            logger.error("redis not started")