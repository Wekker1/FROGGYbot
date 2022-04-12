import discord
import logging
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith('!member'):
            for guild in client.guilds:
                for member in guild.members:
                    print(guild.name + " s " + member.name)

    #async def on_member_join(self, member):

    	



client = MyClient()
client.run(os.getenv("DISCORD_TOKEN"))
