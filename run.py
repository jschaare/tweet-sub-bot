
import os
import tweepy
import asyncio
import time

from app.discordbot.bot import Bot
from app.utils import config
from app.twitter.listener import TwitterListener
from app.twitter.handler import TwitterHandler

""" cfg = config.get_config()

TOKEN = cfg["discord_token"]

bot = Bot(command_prefix="+")
bot.load_extension("bot.cogs.example")

bot.run(TOKEN) """

def start_twitter():
    return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #refactor this
    try:
        cfg = config.get_config()
        consumer_key = cfg['twitter_api_key']
        consumer_secret = cfg['twitter_api_secret']
        access_token = cfg['twitter_access_token']
        access_token_secret = cfg['twitter_access_secret']
        redis_addr = cfg['redis_uri']
        twhandler = TwitterHandler(consumer_key, consumer_secret, access_token, access_token_secret, redis_addr)
        asyncio.ensure_future(twhandler.run())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        twhandler.close_stream()
        asyncio.run(twhandler.close_redis())