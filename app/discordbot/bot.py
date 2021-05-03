
import datetime
from discord.ext import commands

class Bot(commands.Bot):
    # Subclass of discord.ext.commands.Bot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_cog(self, cog):
        super().add_cog(cog)
        print(f"Cog loaded: {cog.qualified_name}")

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
            print(self.guilds)
            for guild in self.guilds:
                for channel in guild.text_channels:
                    print(channel)

        print(f'Ready: {self.user} (ID: {self.user.id})')
