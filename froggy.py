import discord
import logging
from discord.ext import commands
from discord.utils import get
import random
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents = intents)

# role ids from teams 1-7 in order
roles = [963089891078582382,963089970237677651,963090032405659718,963090085144834069,963090166581444628,963090236836040745,963572386475692042]
spectator = 0

npcRoles = [
963573981632405517,
874051960372883467,
958645682611302444,
]


Testroles = [
963563122294149180,
963563192137699339,
963563228888186931,
]

async def PCmembers(message):
    memberList = message.author.guild.members
    newList = []
    for member in memberList:
        illegalFlag = False

        for role in npcRoles:
            if(not(illegalFlag)):
                for irole in member.roles:
                    if(not(illegalFlag)):
                        if(role == irole.id):
                            illegalFlag = True

        if(not(illegalFlag)):
            newList.append(member)

    return newList

async def memberHasRole(member):
    for role in Testroles:
            for irole in member.roles:
                if(role == irole.id):
                    return True

    return False

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

@bot.event
async def on_message(message):
    if message.content.startswith('Toggle Spectator'):
        member = message.author

        mydb = mysql.connector.connect(
            host=os.getenv("SQL_HOST"),
            user=os.getenv("SQL_USER"),
            password=os.getenv("SQL_PASS"),
            database=os.getenv("DBNAME")
        )
        mycursor = mydb.cursor()

        sql = "SELECT * FROM users WHERE username = %s"
        val = (member.name,)

        mycursor.execute(sql, val)
        results = mycursor.fetchall()

        if(len(results) > 0):
            print(bool(results[0][1]))

            sql = "UPDATE users SET playing = %s WHERE userid = %s"
            val = (not(bool(results[0][1])), results[0][3])
            print(val)

            mycursor.execute(sql, val)

            mydb.commit()
            mycursor.close()
            mydb.close()
        else:
            sql = "INSERT INTO users (username, userid, playing, currentrole) VALUES (%s, %s, %s, %s)"
            val = (member.name, int(member.id), False, spectator)
            print(val)

            mycursor.execute(sql, val)

            mydb.commit()
            mycursor.close()
            mydb.close()

    if message.content.startswith('!getEligibleMembers'):
        await PCmembers(message)

    if message.content.startswith('!assignTeams'):
        memberList = await PCmembers(message)
        for member in memberList:
            print(member.name)
            hasRole = await memberHasRole(member)
            print(hasRole)
            if(not(hasRole)):
                role = get(member.guild.roles, id=Testroles[random.randint(0,len(Testroles)-1)])
                print(role.name)
                await member.add_roles(role)

@bot.event
async def on_member_join(member):
    print(member.name + " joined!")
    role = get(member.guild.roles, id=Testroles[random.randint(0,len(Testroles)-1)])
    await member.add_roles(role)


bot.run(os.getenv("DISCORD_TOKEN"))
