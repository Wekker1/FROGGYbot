import discord
import logging
from discord.ext import commands

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
client.run('OTYzNTYzODUyNDcyMTQ3OTk4.YlX6xA.hjhom0dPsoPJybXnmjJGpf0Sdx8')
