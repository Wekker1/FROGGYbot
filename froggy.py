import discord
import logging
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

# role ids from teams 1-7 in order
roles = [963089891078582382,963089970237677651,963090032405659718,963090085144834069,963090166581444628,963090236836040745,963572386475692042]

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
