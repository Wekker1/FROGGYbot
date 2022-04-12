import discord
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

    #async def on_member_join(self, member):

    @client.event
	async def on_message(message):
    	if message.content.startswith('!member'):
        	for guild in client.guilds:
            	for member in guild.members:
                	print(member)



client = MyClient()
client.run(os.getenv("DISCORD_TOKEN"))
