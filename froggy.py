import discord
import logging
from discord.ext import commands
from discord.utils import get
import random
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents = intents)


random_role_names = [
'Test 1',
'Test 2',
'Test 3',
]

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

@bot.event
async def on_message(message):
    if message.content.startswith('!role'):
        member = message.author
        role = get(member.guild.roles, name=random_role_names[random.randint(0,2)])
        print(member.name + " given role: " + role.name)
        await member.add_roles(role)

@bot.event
async def on_member_join(member):
    print(member.name + " joined!")
    role = get(member.guild.roles, name=random_role_names[random.randint(0,2)])
    await member.add_roles(role)


bot.run(os.getenv("DISCORD_TOKEN"))
