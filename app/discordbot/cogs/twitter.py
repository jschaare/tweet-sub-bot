from discord.ext import commands
from app.discordbot.bot import Bot

class Twitter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.redis = None

    async def start_redis(self):
        self.redis = await aioredis.create_redis_pool(self.redis_addr, encoding='utf-8')

    async def close_redis(self):
        await self.redis.wait_closed()

    @commands.command()
    async def tryme(self, ctx):
        response = "Nice, Ayy lmao"
        await ctx.send(response)

    @commands.command()
    async def whoami(self, ctx):
        response = f"Hey there, {ctx.author.display_name}!"
        await ctx.send(response)

def setup(bot):
    bot.add_cog(Twitter(bot))