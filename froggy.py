import discord
import logging
from discord.ext import commands
from discord.utils import get
import pickle
import random
import os
from os.path import exists
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents = intents)

guildIDs = [
856341009218666506, # Wekker Test Sever
847560709730730064, # Community Server
]

pickleFiles = {
856341009218666506 : 'testAss.pickle',
847560709730730064 : 'commAss.pickle',
}

# Team role ids from teams 1-7 in order
teams = [
963089891078582382,
963089970237677651,
963090032405659718,
963090085144834069,
963090166581444628,
963090236836040745,
963572386475692042]
spectator = 0

npcRoles = [
# Bots
963573981632405517,
874051960372883467,
958645682611302444,

# Users
951230650680225863, # GM
951999879637516418, # Spectator
]

Testroles = [
963563122294149180,
963563192137699339,
963563228888186931,
]

roleListByGuild = {
856341009218666506 : Testroles,
847560709730730064 : teams,
}

async def pickleLoadMemberData(guild):
    read = {}
    pickleFile = pickleFiles[guild.id]

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)
    return read

async def pickleWrite(memberData, guild):
    pickleFile = pickleFiles[guild.id]

    with open(pickleFile, 'wb') as f:
        pickle.dump(memberData, f, pickle.HIGHEST_PROTOCOL)

async def pickleClear(guild):
    await pickleWrite({}, guild)

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

async def generateSelectorList(length):
    selector = []
    for i in range(length):
        selector.append(i)
    return selector

async def assignRandomTeams(memberList, guild):
    teamList = roleListByGuild[guild.id]
    selector = await generateSelectorList(len(teamList))
    assignMemory = await pickleLoadMemberData(guild)

    for member in memberList:
        if member.id in assignMemory:
            assignment = assignMemory[member.id]
            role = get(member.guild.roles, id=assignment)
            await member.add_roles(role)
        else:
            if(len(selector) <= 1):
                selector = await generateSelectorList(len(teamList))

            it = random.randint(0, len(selector)-1)
            ind = selector[it]

            assignment = teamList[ind]

            assignMemory[member.id] = assignment
            role = get(member.guild.roles, id=assignment)
            await member.add_roles(role)

    return assignMemory


async def removeTeamRolesFromMembers(memberList, guild):
    teamList = roleListByGuild[guild.id]

    for member in memberList:
        for team in teamList:
            await member.remove_roles(get(guild.roles, id=team))

async def reassignMemberTeam(member, guild):
    roleList = roleListByGuild[guild.id]

    memberAssignments = pickleLoadMemberData(guild)

    if member.id in memberAssignments:
        role = get(member.guild.roles, id=assignment)
        await member.add_roles(role)
        return True

    return False


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

@bot.event
async def on_message(message):
    guild = message.guild

    if message.content.startswith('!toggleSpectator'):
        member = message.author
        print(member.name)
    if message.content.startswith('!toggleSpectatorTest'):
        member = message.author
        print(member.name)

    if message.content.startswith('!getEligibleMembers'):
        memberList = await PCmembers(message)
        for member in memberList:
            print(member.name + " : " + str(member.id))

    if message.content.startswith('!assignTeams'):
        memberList = await PCmembers(message)
        await pickleWrite(await assignRandomTeams(memberList, guild), guild)

    if message.content.startswith('!clearAllTeams'):
        memberList = await PCmembers(message)
        await removeTeamRolesFromMembers(memberList, guild)
        await pickleClear(guild)

@bot.event
async def on_member_join(member):
    print(member.name + " joined!")
    guild = member.guild
    if(not(await reassignMemberTeam(member, guild))):
        print("do stuff")
        ### Do stuff if member do not have a team?


bot.run(os.getenv("DISCORD_TOKEN"))
