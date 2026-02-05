# Bot/File stuff
import discord
import logging
from discord.ext import commands
from discord.utils import get
from discord.commands import Option
from discord.commands import permissions
from discord.ui import *
import pickle
import random
import os
import io
import pandas
from os.path import exists
from dotenv import load_dotenv

# Froggy specific stuff
import mapRender
from mapRender import *
import playareaRender
from playareaRender import *
import frontend
from frontend import *
import froghandler
from froghandler import *
import spiraldraft
from spiraldraft import *
import components
from components import *

# Math and Time
import datetime
from datetime import *
import time as Time
import sys
import numpy as np

# Robodane import stuff
import asyncio
import sys, getopt
import math
import time
import csv
import re
from Levenshtein import distance
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import cv2
import imageio
import subprocess
import functools
import typing
import spiraldraft
from spiraldraft import *

# SCPT stuff
import csv
from io import StringIO
from typing import Union
from reader import make_reader

# robodane vars
levDistMin = 2
fuzzDistMin = 80
botColor = 0x2b006b
delete_response = False
time_to_delete_response = 300

load_dotenv()

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.all()
bot = discord.Bot(command_prefix='?', intents = intents)
frog = bot.create_group("frog", "Frog of War commands")
misc = bot.create_group("misc", "Miscellaneous commands")
draft = bot.create_group("draft", "Draft commands")
admin = bot.create_group("admin", "Admin commands")
arcs = bot.create_group("arcs", "ARCs commands")

guildIDs = [
        856341009218666506,  # Wekker Test Sever
        847560709730730064,  # Community Server
        1049517171233005608, # Root Server
        409044671508250625,  # SCPT Server
        ]

commPlaysIDs = [

        ]

## Work on combining these:
pickleFiles = {
        856341009218666506 : 'testAss.pickle',
        847560709730730064 : 'commAss.pickle',
        1049517171233005608 : 'root.pickle',
        409044671508250625 : 'scpt.pickle',
        "admin" : "admin.pickle",
        }

backUps = {
        856341009218666506 : 'testAss.pickle',
        847560709730730064 : 'restoreList.txt',
        1049517171233005608 : 'root.pickle',
        409044671508250625 : 'scpt.pickle'
        }

# Team role ids from teams 1-7 in order
CPTIteams = [
        1311388595071877180,
        1318310323287232684,
        1311388071987511396,
        1311388350707400784,
        1318310132525957161,
        1328819699370295326,
        ]
spectator = 0

# Team role ids for chutes and ladders
cnl = [
        1034635887297974284,
        1034635790518587483,
        1034635716732395610,
        1034636021398253638,
        ]

# Root Team Roles
rootTeams = [
        1049525887718133780,
        1049700036226846770,
        1049700548221349958,
        1049700864023085067,
        ]


npcRoles = [
        # Bots
        963573981632405517,
        874051960372883467,
        958645682611302444,
        964306086955999264,
        874051960372883467,
        951970331386585121,
        953386946749681757,
        964311549466517534,
        1051279439247446036,

        # Users - Community
        951230650680225863, # GM
        951999879637516418, # Spectator

        # Users - Root
        1049525124711333899, # GM
        1049794341163520070, # Executer

        # Test Users
        964333967807500310,

        409044671508250625, # SCPT Everyone
        ]

GMRoles = {
        847560709730730064 : 951230650680225863, # Community
        856341009218666506 : 964333967807500310, # Test
        1049517171233005608 : 1111726048153964574,
        409044671508250625 : 814618314952146955, # SCPT
        }

GMRolesList = [
        951230650680225863, # Community
        964333967807500310, # Test
        1049525124711333899, # Root
        814618314952146955, # SCPT
        ]

Testroles = [
        963563122294149180,
        963563192137699339,
        963563228888186931,
        ]

roleListByGuild = {
        856341009218666506 : Testroles,
        847560709730730064 : CPTIteams,
        1049517171233005608 : rootTeams,
        409044671508250625 : [],
        }

playerRoleFromGuild = {
        856341009218666506 : Testroles[0],
        847560709730730064 : 1441171284309442571,
        1049517171233005608 : None, # Root does not have a generic player role.
        409044671508250625 : None, # SCPT does not have a generic player role.
        }

emojiID = {
        "AssaultRolling"       : 1265787998755356752,
        "RaidRolling"          : 1265785421804339211,
        "SkirmishRolling"      : 1265787997526298804,
        "AssaultDie"           : 1265792527789850718,
        "RaidDie"              : 1265792263787647051,
        "SkirmishDie"          : 1265792526707593338,
        "NumberDie"            : 1265792525206159483,
        "EventDie"             : 1265792528540500030,
        "Die_Hit"              : 1254934177875230800, 
        "Die_Hit_Building"     : 1254934178865348710, 
        "Die_Self"             : 1254934182422118563, 
        "Die_Raid"             : 1254934181264359424, 
        "Die_Intercept"        : 1254934180140159059, 
        "Resource_Fuel"        : 1254942078258118727, 
        "Resource_Material"    : 1254942079130402956, 
        "Resource_Psionic"     : 1254942079964942418, 
        "Resource_Weapon"      : 1265380019002150932, 
        "Resource_Relic"       : 1254942081202393138,
        }

dieLookup = {
        "Skirmish" : {
            1 : [],
            2 : [],
            3 : [],
            4 : ["Die_Hit"],
            5 : ["Die_Hit"],
            6 : ["Die_Hit"],
            },
        "Assualt" : {
            1 : [],
            2 : ["Die_Self", "Die_Hit"],
            3 : ["Die_Intercept", "Die_Hit"],
            4 : ["Die_Hit", "Die_Hit", "Die_Self"],
            5 : ["Die_Hit", "Die_Hit"],
            6 : ["Die_Self", "Die_Hit"],
            },
        "Raid" : {
            1 : ["Die_Raid", "Die_Raid", "Die_Intercept"],
            2 : ["Die_Raid", "Die_Self"],
            3 : ["Die_Intercept"],
            4 : ["Die_Self", "Die_Hit_Building"],
            5 : ["Die_Hit_Building", "Die_Raid"],
            6 : ["Die_Self", "Die_Hit_Building"],
            },
        "Raid" : {
            1 : ["Die_Raid", "Die_Raid", "Die_Intercept"],
            2 : ["Die_Raid", "Die_Self"],
            3 : ["Die_Intercept"],
            4 : ["Die_Self", "Die_Hit_Building"],
            5 : ["Die_Hit_Building", "Die_Raid"],
            6 : ["Die_Self", "Die_Hit_Building"],
            },
        "Number" : {
            1 : ["1"],
            2 : ["2"],
            3 : ["3"],
            4 : ["4"],
            5 : ["5"],
            6 : ["6"],
            },
        "Event" : {
            1 : ["Hexagon_Crisis"],
            2 : ["Arrow_Crisis"],
            3 : ["Moon_Crisis"],
            4 : ["Hexagon_Event"],
            5 : ["Arrow_Event"],
            6 : ["Moon_Event"],
            },
        }

newMemberFlag = "pFlagNewMembers"
reactChannelsKey = "rChannels"
bannedThreadsKey = "bThreads"
bannedPhrasesKey = "bPhrases"

class adminObj():
    id = "admin"
    def init(self):
        self.id = "admin"

async def isPickleEmpty(guild):
    pickleFile = pickleFiles[guild.id]

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            if len(pickle.load(f)) > 0:
                return False
    return True

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
    assignMemory = await pickleLoadMemberData(guild)
    if newMemberFlag in assignMemory:
        pFlag = assignMemory[newMemberFlag]
    else:
        pFlag = False
    newMemory = {}
    newMemory[newMemberFlag] = pFlag
    await pickleWrite(newMemory, guild)

async def PCmembers(guild):
    memberList = guild.members
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

async def recreatePickle(guild):
    memberList = await PCmembers(guild)
    roleList = roleListByGuild[guild.id]
    assignMemory = {}

    for member in memberList:
        for role in member.roles:
            for irole in roleListByGuild[guild.id]:
                if irole == role.id:
                    assignMemory[member.id] = role.id

    await pickleWrite(assignMemory, guild)

async def recreatePickleRole(guild, role):
    memberList = await PCmembers(guild)
    roleList = [role.id]
    assignMemory = {}

    for member in memberList:
        for role in member.roles:
            for irole in roleListByGuild[guild.id]:
                if irole == role.id:
                    assignMemory[member.id] = role.id

    await pickleWrite(assignMemory, guild)

async def reportUnassignedMembers(guild):
    memberList = guild.members
    unassignedList = []
    for member in memberList:
        illegalFlag = False

        if len(member.roles) > 1:
            illegalFlag = True

        if(not(illegalFlag)):
            unassignedList.append(member)

    return unassignedList

async def loadBackupList(guild):
    lines = []
    backupFile = backUps[guild.id]

    if exists(backupFile) and os.path.getsize(backupFile):
        with open(backupFile, 'r') as f:
            lines = f.readlines()

    textDict = {}
    for line in lines:
        tempList = line.split()
        if len(tempList) > 2:
            textDict[tempList[0]] = tempList[2]

    for memberName in textDict:
        member = get(guild.members, name=memberName)
        if(member):
            roleName = textDict[memberName]
            role = get(guild.roles, name=roleName)
            await member.add_roles(role)
            print(memberName + " successfully added back to " + role.name)

async def generateSelectorList(length):
    selector = []
    for i in range(length):
        selector.append(i)
    return selector

async def getTeamPop(guild):
    teamList = roleListByGuild[guild.id]
    assignMemory = await pickleLoadMemberData(guild)
    teamPop = {}

    # Initialize population list
    for team in teamList:
        teamPop[team] = 0

    for midn in assignMemory:
        member = get(guild.members, id=midn)
        if(member):
            for role in member.roles:
                if role.id in teamList:
                    teamPop[role.id] = teamPop[role.id] + 1

    return teamPop

async def assignRandomTeamsSpecific(memberList, guild, roleids):
    teamList = roleids
    selector = await generateSelectorList(len(teamList))
    assignMemory = await pickleLoadMemberData(guild)
    teamPop = await getTeamPop(guild)

    if len(assignMemory) < 1:
        assignMemory[newMemberFlag] = False

    for member in memberList:
        if member.id in assignMemory:
            assignment = assignMemory[member.id]
            role = get(member.guild.roles, id=assignment)
            if not(role in member.roles):
                print(member.name + " readded to team " + role.name)
                await member.add_roles(role)
            else:
                print(member.name + " already on team " + role.name)
        else:
            contCheck = True
            assignment = -1
            while(contCheck):
                if(len(selector) <= 1):
                    selector = await generateSelectorList(len(teamList))

                it = random.randint(0, len(selector)-1)
                ind = selector[it]
                assignment = teamList[ind]
                del selector[it]

                tMax = 0
                cPop = 0
                allsame = 1
                for team in teamList:
                    if not(team in teamPop):
                        teamPop[team] = 0
                    elif teamPop[team] > tMax:
                        tMax = teamPop[team]
                    elif teamPop[team] == tMax:
                        allsame = allsame+1
                    if team == assignment:
                        cPop = teamPop[team]

                if cPop == tMax:
                    if(allsame == len(teamList)):
                        contCheck = False
                    elif(len(selector) <= 1):
                        contCheck = False
                    else: 
                        contCheck = True
                else:
                    contCheck = False

            teamPop[assignment] = teamPop[assignment] + 1
            assignMemory[member.id] = assignment
            role = get(member.guild.roles, id=assignment)
            print(member.name + " added to team " + role.name)
            await member.add_roles(role)

    return assignMemory

async def assignRandomTeams(memberList, guild):
    assignMemory = await assignRandomTeamsSpecific(memberList, guild, roleListByGuild[guild.id])
    return assignMemory

async def toggleAutoAddNewMembers(guild):
    assignMemory = await pickleLoadMemberData(guild)

    if len(assignMemory) < 1:
        return None

    if newMemberFlag in assignMemory:
        assignMemory[newMemberFlag] = not(assignMemory[newMemberFlag])
    else:
        assignMemory[newMemberFlag] = True

    await pickleWrite(assignMemory, guild)

    return assignMemory[newMemberFlag]


async def removeTeamRolesFromMembers(memberList, guild):
    teamList = roleListByGuild[guild.id]

    for team in teamList:
        teamRole = get(guild.roles, id=team)
        for member in memberList:
            if teamRole in member.roles:
                await member.remove_roles(teamRole)


async def reassignMemberTeam(member, guild):
    memberAssignments = await pickleLoadMemberData(guild)

    if len(memberAssignments) < 1:
        return None

    if member.id in memberAssignments:
        role = get(member.guild.roles, id=memberAssignments[member.id])
        await member.add_roles(role)
        return True

    return False

async def simpleAssignTeams(guild):
    memberList = await PCmembers(guild)
    await pickleWrite(await assignRandomTeams(memberList, guild), guild)

async def simpleAddSingleMemberToTeam(member, guild):
    singleMemberList = [member,]
    await pickleWrite(await assignRandomTeams(singleMemberList, guild), guild)

async def addSingleMemberToTeam(member, role, guild):
    singleMemberList = [member,]
    await removeTeamRolesFromMembers(singleMemberList, guild)

    assignMemory = await pickleLoadMemberData(guild)

    assignMemory[member.id] = role.id
    await member.add_roles(role)

    await pickleWrite(assignMemory, guild)

async def simpleClearAllTeams(guild):
    memberList = await PCmembers(guild)
    await removeTeamRolesFromMembers(memberList, guild)
    await pickleClear(guild)

async def simpleGetMemberAssignments(guild):
    assignedList = await pickleLoadMemberData(guild)

    if len(assignedList) < 1:
        return None

    conString = ""
    if(len(assignedList) > 0):
        for idn in assignedList:
            member = get(guild.members, id=idn)
            if member:
                role = get(guild.roles, id=assignedList[idn])
                conString = conString + member.name + " : " + role.name + "\n"
            else:
                conString = conString + str(idn) + " : " + str(assignedList[idn]) + "\n"
        conString = conString[0:-1]
    else:
        conString = 'Pickle Empty'
    return conString

@tasks.loop(hours=1)
async def SCPT_RSS():
    scptID = guildIDs[3]
    guild = get(bot.guilds, id=scptID)
    episode_discussion_id = 1100630695606501376
    feedChannel = get(guild.channels, id=episode_discussion_id)
    
    feed_url = "https://feed.podbean.com/spacecatspeaceturtles/feed.xml"

    reader = make_reader("db.sqlite")

    reader.add_feed(feed_url, exist_ok=True)
    reader.update_feeds()

    feed = reader.get_feed(feed_url)

    latest = list(reader.get_entries())[0]
    title = latest.title
    link = latest.link
    desc = latest.summary

    ep_is_posted = get(feedChannel.threads, name=title)
    if(ep_is_posted):
        return

    episode_embed = discord.Embed(title=title, url=link, description=desc, author=discord.EmbedAuthor("Space Cats Peace Turtles", url=r"https://www.spacecatspeaceturtles.com/", 
        icon_url=r"https://pbcdn1.podbean.com/imglogo/image-logo/2044403/Podcast-Logo1400X1400_300x300.jpg"), color=0xEF4136, thumbnail=r"https://pbcdn1.podbean.com/imglogo/image-logo/2044403/Podcast-Logo1400X1400_300x300.jpg")
    feedChannel.create_thread(name=title, embed=episode_embed)

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    await bot.sync_commands()
    SCPT_RSS.start()

    guild = get(bot.guilds, id=guildIDs[1])

    # Persistency for slash commands with buttons
    view = discord.ui.View(timeout=None)
    for i in range(4):
        commandName = "Off by One Error"
        if(i == 0):
            commandName = "Assign Teams"
        elif(i == 1):
            commandName = "Clear Teams"
        elif(i == 2):
            commandName = "Report Team Assignments"
        elif(i == 3):
            commandName = "Toggle Autoassigning New Members"
        view.add_item(ButtonTest(commandName, i))
    bot.add_view(view)

    view = discord.ui.View(timeout=None)
    for i in range(6):
        commandName = "Off by One Error"
        if(i == 0):
            commandName = "Captainize Me!"
        elif(i == 1):
            commandName = "Uncaptainize Me!"
        elif(i == 2):
            commandName = "Add me as a player!"
        elif(i == 3):
            commandName = "Remove me as a player!"
        elif(i == 4):
            commandName = "Add me to Team-Pings!"
        elif(i == 5):
            commandName = "Remove me from Team-Pings!"

        view.add_item(RoleButton(commandName, i+4))
    bot.add_view(view)

    view = factionDecisionRequest(guild, factions)
    bot.add_view(view)

    rList = []
    for r in guild.roles:
        rList.append(r.id)
    view = decisionRoleRequest(rList, guild)
    bot.add_view(view)


async def loadReactChannels(guild):
    assignMemory = await pickleLoadMemberData(guild)
    if not(reactChannelsKey in assignMemory):
        return []
    else:
        return assignMemory[reactChannelsKey]

async def loadBannedThreads(guild):
    assignMemory = await pickleLoadMemberData(guild)
    if not(bannedThreadsKey in assignMemory):
        return []
    else:
        return assignMemory[bannedThreadsKey]

async def writeBannedThreads(guild, bannedThreads):
    assignMemory = await pickleLoadMemberData(guild)
    assignMemory[bannedThreadsKey] = bannedThreads
    await pickleWrite(assignMemory, guild)

async def loadBannedPhrases(guild):
    assignMemory = await pickleLoadMemberData(guild)
    if not(bannedPhrasesKey in assignMemory):
        return {}
    else:
        return assignMemory[bannedPhrasesKey]

async def writeBannedPhrases(guild, bannedPhrases):
    assignMemory = await pickleLoadMemberData(guild)
    assignMemory[bannedPhrasesKey] = bannedPhrases
    await pickleWrite(assignMemory, guild)

urlfindstring = r"([a-zA-Z\d]+:\\\\)?((\w+:\w+@)?([a-zA-Z\d.-]+\.([A-Za-z]{2,4}))(:\d+)?(\.*)?)"

@bot.event
async def on_message(message):
    guild = message.guild
    if not(guild):
        return
    if (message.author == bot.user):
        return
    for role in message.author.roles:
        if role.id in GMRoles.values():
            # return
            pass

    mContent = message.clean_content
    bannedPhrasesDict = await loadBannedPhrases(guild)
    bannedPhrases = list(bannedPhrasesDict.keys())
    delMessageFlag = False
    delinquintPhrases = []
    for banPhrase in bannedPhrases:
        if banPhrase in mContent.lower():
            linkCheck = bannedPhrasesDict[banPhrase]
            if(linkCheck):
                groups = re.match(urlfindstring, mContent).groups()
                tldCandidates = groups[3].split(".")
                for tld in tldCandidates:
                    if tld.upper() in topleveldomains:
                        delMessageFlag = True
                        delinquintPhrases.append(banPhrase)
            else:
                delMessageFlag = True
                delinquintPhrases.append(banPhrase)
    if delMessageFlag:
        author = message.author
        await message.delete()
        phrases = ""
        for phrase in delinquintPhrases:
            phrases+= "* " + phrase + "\n"
        await author.send("Hello, " + author.name + " your recent message in " + guild.name +" has been deleted as it contains the following banned phrase(s): \n" + phrases + "\nPlease contact a moderator of that discord if you believe your message was deleted in error.")
        return

    reactChannels = await loadReactChannels(guild)

    if(message.channel.type == discord.ChannelType.public_thread):
        thread = message.channel
        if(thread.parent.type == discord.ChannelType.forum and thread.parent.id in reactChannels):
            author = message.author
            threadlen = len(await thread.history(limit=10).flatten())
            if(len(message.attachments) < 1 and (re.search(urlfindstring, message.content) == None) and threadlen < 2):
                print(author.name)
                print(thread.name)
                await thread.delete()
                await author.send("Sorry, " + guild.name + " Admins do not allow text posts in " + thread.parent.name + " if you believe your post was deleted in error, please contact an Admin.")

@bot.event
async def on_member_join(member):
    guild = member.guild
    if(guild.id in guildIDs):
        # print(member.name + " joined!")
        if(not(await reassignMemberTeam(member, guild))):
            if(not(await isPickleEmpty(guild))):
                assignMemory = await pickleLoadMemberData(guild)
                if newMemberFlag in assignMemory and assignMemory[newMemberFlag]:
                    await simpleAddSingleMemberToTeam(member, guild)

@admin.command(name="list_guilds")
async def listAllGuilds(ctx: discord.ApplicationContext):
    guildnames = []
    guildids = []
    for guild in bot.guilds:
        guildnames.append(guild.name)
        guildids.append(guild.id)

    outList = ""
    for i in range(len(guildnames)):
        outList = outList + guildnames[i] + " : " + str(guildids[i]) + "\n"

    await ctx.respond("Froggy has been added to the following guilds:\n" + outList);

@admin.command(name="sync_category_all")
async def syncAllChannels(ctx: discord.ApplicationContext, category: Option(discord.CategoryChannel, "The category to sync.", required=True)):
    await ctx.defer()
    for channel in category.channels:
        await channel.edit(sync_permissions=True)

    await ctx.respond("Channels in " + category.name + " updated to sync permissions.", delete_after=10)

@admin.command(name="save_react_channel")
async def savereact(ctx: discord.ApplicationContext, channel: Option(discord.SlashCommandOptionType.channel, "The channel to tune in to.")):
    guild = ctx.guild;
    assignMemory = await pickleLoadMemberData(guild)
    if not(reactChannelsKey in assignMemory):
        assignMemory[reactChannelsKey] = []
        assignMemory[reactChannelsKey].append(channel.id)
    else:
        if(not(channel.id in assignMemory[reactChannelsKey])):
            assignMemory[reactChannelsKey].append(channel.id)
    await pickleWrite(assignMemory, guild)
    await ctx.respond(channel.name + " added to Froggy's watched channels.")

@admin.command(name="backup_pickle")
async def say(ctx: discord.ApplicationContext):
    """This demonstrates how to attach a file with a slash command."""

    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", delete_after=10)
        return

    pickleFile = pickleFiles[guild.id]

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        file = discord.File(pickleFile)
        await ctx.respond("Here's your backup pickle file!", file=file)

class ButtonTest(discord.ui.Button):
    def __init__(self, commandName, commandNum):
        super().__init__(label=commandName, style=discord.enums.ButtonStyle.primary, custom_id=str(commandNum))

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        gmRole = get(guild.roles, id=GMRoles[guild.id])
        #await interaction.defer()
        if(not(gmRole in interaction.user.roles)):
            await interaction.response.send_message("You do not have permission to use this command.", delete_after=10, ephemeral=True)
            return
        commandInd = int(self.custom_id)

        if(commandInd == 0):
            await simpleAssignTeams(guild)
            await interaction.response.send_message(content = "Teams Assigned!", delete_after=10)
        elif(commandInd == 1):
            await simpleClearAllTeams(guild)
            await interaction.response.send_message(content = "Teams Cleared!", delete_after=10)
        elif(commandInd == 2):
            attachment = await simpleGetMemberAssignments(guild)
            fileOut = discord.File(io.StringIO(attachment), filename="MemberAssignments.txt", description="A list of member names and corresponding assinged team.")
            await interaction.response.send_message(content = "Here's a list of team assignments, this message will delete in 1 minute:", delete_after=60, file=fileOut)
        elif(commandInd == 3):
            if await toggleAutoAddNewMembers(guild):
                await interaction.response.send_message(content = "New members will now be automatically assigned a team.", delete_after=10)
            else:
                await interaction.response.send_message(content = "New members will no longer be automatically assigned a team.", delete_after=10)

        else:
            print("Invalid Button ID Detected.")
        return True

@draft.command(name="generate_spiral_draft")
async def generateSpiral(ctx: discord.ApplicationContext, numslices: Option(int, "Number of slices to generate.", choices = [1, 2, 3, 4, 5, 6, 7, 8], default=6), treat_anomaly_planets_as_blue : Option(bool, "Treat cormund and everra as if there were blue tiles.", default=True, required = False)):# , include_te : Option(bool, "Include temp systems.", required = False, default=False)):
    draft = Spiral(numslices, treat_anomaly_planets_as_blue)
    await ctx.respond("Generating Spiral Draft")
    slices = draft.generate_and_verify()
    sliceStrings = ""
    for slic in slices:
        for i in range(0,5):
            sliceStrings = sliceStrings + slic[i] + ","
        sliceStrings = sliceStrings[:-1] + "|"
    sliceStrings = sliceStrings[:-1]
    slicesImage = draft.generateImages()
    draftFile = discord.File(slicesImage, filename=slicesImage[len(spiraldraft.path):])
    await ctx.edit(content=f"Spiral Draft Generated: {sliceStrings}", file=draftFile)

temp_art_path = {
        "image/png" : "./temp/upload.png",
        "image/jpg" : "./temp/upload.jpg",
        "image/jpeg": "./temp/upload.jpeg",
        }

@misc.command(name="generate_event", guild_ids=guildIDs)
async def generateEvent(ctx: discord.ApplicationContext, name: Option(str, "The name of the event.", max_length=24), complexity: Option(int, "The complexity or impact level of the event (1-3).", choices = [1, 2, 3], default = 1), art: Option(discord.Attachment, "500x550px art for the event, as a PNG or JPG.", required=False)):
    passedArt = None
    if art:
        if art.content_type in temp_art_path.keys():
            passedArt = temp_art_path[art.content_type]
            await art.save(passedArt)

    new_event = Event(name, complexity, passedArt)
    event_modal = componentModal(new_event, title=name)
    await ctx.send_modal(event_modal)

@admin.command(name="command_message")
async def say(ctx: discord.ApplicationContext):
    """Create a message with various commands"""

    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", delete_after=10, ephemeral=True)
        return

    view = discord.ui.View(timeout=None)
    for i in range(4):
        commandName = "Off by One Error"
        if(i == 0):
            commandName = "Assign Teams"
        elif(i == 1):
            commandName = "Clear Teams"
        elif(i == 2):
            commandName = "Report Team Assignments"
        elif(i == 3):
            commandName = "Toggle Autoassigning New Members"
        view.add_item(ButtonTest(commandName, i))
    await ctx.respond("Here are some commands:", view=view)

@admin.command(name="clear_members_from_role")
async def clearRole(ctx: discord.ApplicationContext, role: Option(discord.Role, "The Role to Clear")):
    """Clear all members from a role"""
    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", ephemeral=True, delete_after=10)
        return

    await ctx.respond(role.mention + " is being cleared.")
    data = await pickleLoadMemberData(guild)

    if len(data) < 1:
        return None

    memberList = await PCmembers(guild)

    for member in memberList:
        if role in member.roles:
            await member.remove_roles(role)
            if member.id in data:
                if data[member.id] == role.id:
                    del data[member.id]

    await pickleWrite(data, guild)
    await ctx.respond(role.mention + " has been cleared.", delete_after=10)

@admin.command(name="add_members_to_role")
async def addToRole(ctx: discord.ApplicationContext, role: Option(discord.Role, "The Role"), memberone: Option(discord.Member, "Member 1"), membertwo: Option(discord.Member, "Member 2", required=False, default=None), 
                    memberthree: Option(discord.Member, "Member 3", required=False, default=None), memberfour: Option(discord.Member, "Member 4", required=False, default=None), memberfive: Option(discord.Member, "Member 5", required=False, default=None)):
    """Add members to a role"""
    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", ephemeral=True, delete_after=10)
        return

    await ctx.respond("Adding players to " + role.mention)
    data = await pickleLoadMemberData(guild)

    if len(data) < 1:
        return None

    await addSingleMemberToTeam(memberone, role, guild)
    if(membertwo):
        await addSingleMemberToTeam(membertwo, role, guild)
    if(memberthree):
        await addSingleMemberToTeam(memberthree, role, guild)
    if(memberfour):
        await addSingleMemberToTeam(memberfour, role, guild)
    if(memberfive):
        await addSingleMemberToTeam(memberfive, role, guild)

    await ctx.respond("Players added to " + role.mention)

@admin.command(name="copy_members_in_role")
async def copyFromRole(ctx: discord.ApplicationContext, rolefrom: Option(discord.Role, "The Role to copy from"), roleto: Option(discord.Role, "The Role to copy to")):
    """Copy all members from one role to another."""
    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", ephemeral=True, delete_after=10)
        return

    await ctx.respond("Adding players from " + rolefrom.mention + " to " + roleto.mention)

    for member in rolefrom.members:
        await member.add_roles(roleto)

    await ctx.edit("Players added to " + roleto.mention)

ANSICOLORCODES = {
        "FORMAT" : {"BOLD" : "1", "UNDER" : "4"},
        "TEXT" : {
            "BLACK"     : "30",
            "RED"       : "31",
            "GREEN"     : "32",
            "YELLOW"    : "33",
            "BLUE"      : "34",
            "MAGENTA"   : "35",
            "CYAN"      : "36",
            "WHITE"     : "37",
            },
        "BACKGROUND" : {
            "AQUA"      : "40",
            "ORANGE"    : "41",
            "DARKGREY"  : "42",
            "BLUEGREY"  : "43",
            "GREY"      : "44",
            "INDIGO"    : "45",
            "LIGHTGREY" : "46",
            "WHITE"     : "47",
            },
        "RESET" : "0",
        }

def genANSICOLORCODE(form=0, textColor=0, bkgColor=0):
    return f"\u001b[{form};{textColor};{bkgColor}m"

def progress_bar(progress:float, value:int=None, size:int=None) -> str:
    resetColor = genANSICOLORCODE(form = ANSICOLORCODES["RESET"])
    filledColor = genANSICOLORCODE(textColor = ANSICOLORCODES["TEXT"]["WHITE"],bkgColor = ANSICOLORCODES["BACKGROUND"]["ORANGE"])
    emptyColor = genANSICOLORCODE(bkgColor = ANSICOLORCODES["BACKGROUND"]["AQUA"])
    bookends = genANSICOLORCODE(textColor = ANSICOLORCODES["TEXT"]["YELLOW"], bkgColor = ANSICOLORCODES["RESET"]) + "|" + resetColor

    filled = f"{filledColor}☐{resetColor}"
    empty = f"{emptyColor}⠀{resetColor}"
    num_bricks = 10 if size<10 else (0 if size<0 else size)
    filled_num = round(progress * num_bricks)
    empty_num = num_bricks - filled_num
    ansi_progress_str = filled * filled_num
    ansi_progress_str += empty * empty_num 

    if value:
        value = str(value) + "%"
        digits = list(str(value))
        ansi_progress_str = list(ansi_progress_str)

        for i,digit in enumerate(digits):
            ansi_progress_str[i].replace("☐", digit)
            ansi_progress_str[i].replace("⠀", digit)
        ansi_progress_str = "".join(ansi_progress_str)

    ansi_progress_str = "```ANSI\n" + bookends + ansi_progress_str + bookends +"\n```"

    return ansi_progress_str


@admin.command(name="add_members_to_role_by_csv")
async def addAllToRole(ctx: discord.ApplicationContext, file: Option(discord.Attachment, ".csv file formatted as 2 columns: \"username#1234 , role\"")):
    guild = ctx.guild

    byte_content = await file.read()
    content = byte_content.decode()
    content = content.replace("\t", ",").replace("﻿", "")
    if(content[0]==" "):
        content = content[1:]
    csvfile = StringIO(content)
    csv_data = csv.reader(csvfile, dialect="excel")

    totalNum = sum(1 for row in csv_data)
    pbSize = 20
    updateOn = int(totalNum/20)
    if(updateOn<1): 
        updateOn = 1

    emb = discord.Embed(color=discord.Color.gold())
    emb.add_field(name="Processing...", value=progress_bar(progress=0, value=0, size=pbSize))
    await ctx.respond(content=f"Adding users to roles using {file.filename}.", embed=emb)

    notfoundList = []
    missingrole = set()
    count = 1

    csvfile = StringIO(content)
    csv_data = csv.reader(csvfile, delimiter=",")

    for row in csv_data:
        fullnameplate = row[0]
        splituser = fullnameplate.split("#")
        if(len(splituser) < 2):
            username = splituser[0]
            userdis = None
        else:
            username = splituser[0]
            userdis = splituser[1]

        rolename = row[1]

        if(userdis):
            user = get(guild.members, name=username, discriminator=userdis)
        else:
            user = get(guild.members, name=username)

        role = get(guild.roles, name=rolename)
        if(user and role):
            await user.add_roles(role)
        else:
            if(not(user)):
                notfoundList.append(fullnameplate)
            if(not(role)):
                missingrole.add(rolename)

        if(count%updateOn==0):
            progress = count / totalNum
            upProgress = progress_bar(progress=progress, value=int(progress*100), size=pbSize)
            emb.clear_fields()
            emb.add_field(name="Processing...", value=upProgress)
            await ctx.edit(embed=emb)

        count = count+1

    finProgress = progress_bar(progress=1, value=100, size=pbSize)
    emb.clear_fields()
    emb.add_field(name="Finished!", value=finProgress)
    await ctx.edit(content=f"Finished adding users from {file.filename}.", embed=emb)
    if(len(notfoundList) or len(missingrole)):
        erMsg = "I encountered the following issues:\n\n"
        if(len(missingrole)):
            if(len(missingrole)>1):
                erMsg += "ROLES NOT FOUND:\n"
            else:
                erMsg += "ROLE NOT FOUND:\n"

            for role in missingrole:
                erMsg += f"\t{role}\n"
            erMsg += "\n"

        if(len(notfoundList)):
            if(len(notfoundList)>1):
                erMsg += "USERS NOT FOUND:\n"
            else:
                erMsg += "USER NOT FOUND:\n"

            for user in notfoundList:
                erMsg += f"\t{user}\n"
            erMsg += "\n"

        await ctx.respond(content=erMsg)

class ConfirmButton(discord.ui.Button):
    def __init__(self, ogUser, targetUser, timeframe, secLevel):
        encodeString = ""
        encodeString = encodeString + "OG|" + str(ogUser.id) + "_"
        encodeString = encodeString + "TARGET|" + str(targetUser.id) + "_"
        encodeString = encodeString + "TIME|" + str(timeframe) + "_"
        encodeString = encodeString + "SEC|" + str(secLevel)

        super().__init__(label="Confirm?", style=discord.enums.ButtonStyle.green, custom_id=str(encodeString))

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        reschannel = interaction.channel

        aparms = self.custom_id.split("_")
        cmdInfo = {}
        for pair in aparms:
            items = pair.split("|")
            cmdInfo[items[0]] = items[1]

        if(user.id != int(cmdInfo["OG"]) or user.name == "wekker"):
            secLevel = int(cmdInfo["SEC"])
            member = get(guild.members, id=user.id)
            secCheck = False
            if(secLevel == 3):
                secCheck = member.guild_permissions.administrator
            elif(secLevel == 2):
                secCheck = member.guild_permissions.ban_members
            elif(secLevel == 1):
                secCheck = member.guild_permissions.manage_channels
            else:
                secCheck = True

            if(secCheck):
                ogUser = get(bot.users, id=int(cmdInfo["OG"]))
                print(ogUser)
                print(user)
                if(ogUser):
                    approvernames = [str(user.name), str(ogUser.name)]
                else:
                    approvernames = [user.name, "username not found"]

                targetUser = get(bot.users, id=int(cmdInfo["TARGET"]))
                timeframe = float(cmdInfo["TIME"])
                currentTime = datetime.now(timezone.utc)
                limitTime = currentTime - timedelta(hours=timeframe)

                if(targetUser):
                    def matchTarget(m):
                        return m.author.id == targetUser.id

                    await interaction.message.edit(content="Now deleting messages, ordered by " + approvernames[0] + " and " + approvernames[1] + ".", view=None)

                    for channel in guild.text_channels:
                        await channel.purge(check=matchTarget, after=limitTime, reason="Mass delete by " + approvernames[0] + " and " + approvernames[1] + ".")

                    await reschannel.send(content="Finished deleting messages.")
                else:
                    await interaction.response.send_message(content="Sorry, I cannot find the targeted user.")
        else:
            await interaction.response.send_message(content="A user different from the one who started this command must be the one to confirm it.", ephemeral=True, delete_after=20)

class ConfirmView(discord.ui.View):
    def __init__(self, timeout):
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)


@admin.command(name="delete_users_messages")
async def massDelete(ctx: discord.ApplicationContext, targetuser: Option(discord.User, "User to target."), timeframe: Option(float, "How many hours of messages to delete.")):
    guild = ctx.guild
    adminUser = ctx.user

    warnMsg = adminUser.name + " is trying to delete the last " + str(timeframe) + " hours of " + targetuser.name + "'s messages in this guild.\n\nFor security reasons this action must be verified by another Administrator, please click below to confim.\nIf not confirmed within 20 minutes, this command will be disabled."

    view = ConfirmView(timeout=1200)
    view.add_item(ConfirmButton(adminUser, targetuser, timeframe, 3))

    await ctx.respond(warnMsg, view=view)


@admin.command(name="savemembersinrole")
async def addToRole(ctx: discord.ApplicationContext, role: Option(discord.Role, "The Role")):
    """Save members in a role to the pickle"""
    guild = ctx.guild

    await recreatePickleRole(guild, role)

    await ctx.respond(content="Role written to pickle")

class RoleButton(discord.ui.Button):
    def __init__(self, commandName, commandNum):
        if commandNum % 2 == 0:
            butStyle = discord.enums.ButtonStyle.green
        else:
            butStyle = discord.enums.ButtonStyle.red

        super().__init__(label=commandName, style=butStyle, custom_id=str(commandNum))

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        commandInd = int(self.custom_id)
        adminRole = get(guild.roles, id=GMRoles[guild.id])
        errorStr=""
        if(adminRole):
            errorStr = "Contact a " + adminRole.mention + "."

        if(commandInd == 4):
            mroles = member.roles
            for mrole in mroles:
                if mrole.id in roleListByGuild[guild.id]:
                    caprole = get(guild.roles, name=mrole.name + " Captain")
                    if not(caprole):
                        caprole = await guild.create_role(name=mrole.name + " Captain", mentionable=True, hoist=True, reason=mrole.name + " Captain role not found, so created.")
                        await caprole.edit(position=mrole.position+1)

                    await member.add_roles(caprole)
                    await interaction.response.send_message(content="You have been added to the " + caprole.mention + " role.", ephemeral=True, delete_after=10)
                    return

            await interaction.response.send_message(content="I cannot find a Captain role for any roles you are in. " + errorStr, ephemeral=True, delete_after=10)

        elif(commandInd == 5):
            mroles = member.roles
            for mrole in mroles:
                if mrole.name.endswith("Captain"):
                    await member.remove_roles(mrole)
                    await interaction.response.send_message(content="You have been removed from the " + mrole.mention + " role.", ephemeral=True, delete_after=10)
                    return True
            await interaction.response.send_message(content="Sorry, I can't find a captain role assigned to you. " + errorStr, ephemeral=True, delete_after=10)

        elif(commandInd == 6):
            playRoleID = playerRoleFromGuild[guild.id]
            playerRole = get(guild.roles, id=playRoleID)
            if(playerRole):
                await member.add_roles(playerRole)
                await interaction.response.send_message(content="You have been added as a " + playerRole.mention + " player!", ephemeral=True, delete_after=10)
            else:
                print("No Player Role found")
                await interaction.response.send_message(content="Sorry, I can't find a player role for this Discord. " + errorStr, ephemeral=True, delete_after=10)

        elif(commandInd == 7):
            playRoleID = playerRoleFromGuild[guild.id]
            playerRole = get(guild.roles, id=playRoleID)
            if(playerRole):
                await member.remove_roles(playerRole)
                await interaction.response.send_message(content="You have been removed from the " + playerRole.mention + " role!", ephemeral=True, delete_after=10)
            else:
                print("No Player Role found")
                await interaction.response.send_message(content="Sorry, I can't find a player role for this Discord. " + errorStr, ephemeral=True, delete_after=10)

        elif(commandInd == 8):
            mroles = member.roles
            for mrole in mroles:
                if mrole.id in roleListByGuild[guild.id]:
                    atrole = get(guild.roles, name=mrole.name + " Ping")
                    if not(atrole):
                        atrole = await guild.create_role(name=mrole.name + " Ping", mentionable=True, hoist=False, reason=mrole.name + " Ping role not found, so created.")
                        await atrole.edit(position=mrole.position+1)

                    await member.add_roles(atrole)
                    await interaction.response.send_message(content="You have been added to the " + atrole.mention + " role.", ephemeral=True, delete_after=10)
                    return

            await interaction.response.send_message(content="I cannot find a Ping role for any roles you are in. " + errorStr, ephemeral=True, delete_after=10)

        elif(commandInd == 9):
            mroles = member.roles
            for mrole in mroles:
                if mrole.name.endswith("Ping"):
                    await member.remove_roles(mrole)
                    await interaction.response.send_message(content="You have been removed from the " + mrole.mention + " role.", ephemeral=True, delete_after=10)
                    return
            await interaction.response.send_message(content="Sorry, I can't find a ping role assigned to you. " + errorStr, ephemeral=True, delete_after=10)
        else:
            print("Invalid Button ID Detected.")

        return True

@admin.command(name="genextraroles")
async def generateRoles(ctx: discord.ApplicationContext, inccaprole: Option(bool, "Include a team captain role?", required=False, default=True), incpingrole: Option(bool, "Include a team ping role?", required=False, default=False)):
    teamList = roleListByGuild[ctx.guild.id]
    roleList = []
    for team in teamList:
        roleList.append(get(ctx.guild.roles, id=team))

    for role in roleList:
        rname = role.name

        if(inccaprole and get(ctx.guild.roles, name=rname + " Captain") == None):
            await ctx.guild.create_role(name = rname + " Captain", mentionable=True)

        if(inccaprole and get(ctx.guild.roles, name=rname + " Ping") == None):
            await ctx.guild.create_role(name = rname + " Ping", mentionable=True)

    await ctx.respond("Did the thing :)")

@misc.command(name="report_team_stats", guild_ids=commPlaysIDs)
async def reportStats(ctx: discord.ApplicationContext):
    """Later consider adding action tracking and other data"""
    guild = ctx.guild
    teamTotals = await getTeamPop(guild)

    outString = ""
    for team in teamTotals:
        teamRole = get(guild.roles, id=team)
        teamRolesList = {}
        for role in guild.roles:
            if role.name.startswith(teamRole.name) and role.name != teamRole.name:
                teamRolesList[role.name] = len(role.members)

        outString = outString + teamRole.name + " has " + str(teamTotals[team]) + " total members, "

        for role in teamRolesList:
            if(teamRolesList[role] > 1):
                outString = outString + "and " + str(teamRolesList[role]) + " " + role + "s, "
            else:
                outString = outString + "and " + str(teamRolesList[role]) + " " + role + ", "

        outString = outString[0:-2] + ".\n"
    outString = outString[0:-1]
    await ctx.respond(outString)

def create_overwrites(guild, objects):
    """This is just a helper function that creates the overwrites for the
    voice/text channels.
    A `discord.PermissionOverwrite` allows you to determine the permissions
    of an object, whether it be a `discord.Role` or a `discord.Member`.
    In this case, the `view_channel` permission is being used to hide the channel
    From being viewed by whoever does not meet the criteria, thus creating a
    secret channel.
    """

    # A dict comprehension is being utilised here to set the same permission overwrites
    # For each `discord.Role` or `discord.Member`.
    overwrites = {obj: discord.PermissionOverwrite(view_channel=True) for obj in objects}

    # Prevents the default role (@everyone) from viewing the channel
    # if it isn't already allowed to view the channel.
    overwrites.setdefault(guild.default_role, discord.PermissionOverwrite(view_channel=False))

    # Makes sure the client is always allowed to view the channel.
    overwrites[guild.me] = discord.PermissionOverwrite(view_channel=True)

    return overwrites

@admin.command(name="rename_team")
async def renameTeams(ctx: discord.ApplicationContext, role: Option(discord.Role, "Role to change"), newname: Option(str, "New name for role")):
    """Renames all channeles with Role in name, also renames Role"""
    guild = ctx.guild
    await ctx.respond(content="Processing ... ")
    await updateTeamChannels(guild, {role.name : newname})
    await ctx.respond(content="Teams are Setup :)")

factions = [
        "Arborec", "Argent", "Barony", "Cabal",
        "Empyrean", "Ghosts", "Hacan", "Jol-Nar", 
        "Keleres [Argent]", "Keleres [Mentak]", "Keleres [Xxcha]",
        "L1Z1X", "Mahact", "Mentak", "Muaat",
        "Naalu", "Naaz-Rokha", "Nekro", "Nomad",
        "Saar", "Sardakk", "Sol", "Titans",
        "Winnu", "Xxcha", "Yin", "Yssaril",
        ]

@admin.command(name="toggle_map_ban")
async def banMap(ctx: discord.ApplicationContext, mapname: Option(str, "Map name to be restricted.")):
    """Bans/Unbans a specific map name from the /misc map function."""

    adm = adminObj()

    adminDict = await pickleLoadMemberData(adm)

    bFlag = True
    if mapname in adminDict["Banned Maps"]:
        adminDict["Banned Maps"].remove(mapname)
        bFlag = False
    else:
        adminDict["Banned Maps"].append(mapname)
        bFlag = True

    await pickleWrite(adminDict, adm)

    if bFlag:
        await ctx.respond(content = mapname + " added to the banned map names list.")
    else:
        await ctx.respond(content = mapname + " removed from the banned map names list.")


@arcs.command(name="roll")
async def rollArcsDice(ctx: discord.ApplicationContext, numskirmish: Option(int, "Number of skirmish dice to roll.", required=False, default=0, max_value=6, min_value=0), numassault: Option(int, "Number of assault dice to roll.", required=False, default=0, max_value=6, min_value=0), numraid: Option(int, "Number of raid dice to roll.", required=False, default=0, max_value=6, min_value=0),
                       numnumber: Option(int, "Number of number dice to roll.", required=False, default=0, max_value=1, min_value=0), numevent: Option(int, "Number of event dice to roll.", required=False, default=0, max_value=1, min_value=0)):
    """Rolls Arcs Dice with fun animation"""
    if(numskirmish + numassault + numraid + numevent + numnumber == 0):
        await ctx.respond("That isn't any dice!")
        return

    RollingMessage = "Rolling dice...\n"
    emojiList = ctx.guild.emojis
    skirmishEmoji   = get(emojiList, id = emojiID["SkirmishRolling"])
    assaultEmoji    = get(emojiList, id = emojiID["AssaultRolling"])
    raidEmoji       = get(emojiList, id = emojiID["RaidRolling"])
    numberEmoji     = get(emojiList, id = emojiID["NumberDie"])
    eventEmoji      = get(emojiList, id = emojiID["EventDie"])
    RollingMessage += (("<a:" + skirmishEmoji.name + ":" + str(skirmishEmoji.id) + ">")*numskirmish + "\n"*(numskirmish>0) +
                       ("<a:" + assaultEmoji.name + ":" + str(assaultEmoji.id) + ">")*numassault + "\n"*(numassault>0) +
                       ("<a:" + raidEmoji.name + ":" + str(raidEmoji.id) + ">")*numraid + "\n"*(numraid>0) +
                       ("<:" + numberEmoji.name + ":" + str(numberEmoji.id) + ">")*numnumber + "\n"*(numnumber>0) +
                       ("<:" + eventEmoji.name + ":" + str(eventEmoji.id) + ">")*numevent + "\n"*(numevent>0))

    message = await ctx.respond(RollingMessage) 
    await asyncio.sleep(3)
    skirmishList = list(np.random.randint(1,6,numskirmish))
    assaultList  = list(np.random.randint(1,6,numassault))
    raidList     = list(np.random.randint(1,6,numraid))
    numberList   = list(np.random.randint(1,6,numnumber))
    eventList    = list(np.random.randint(1,6,numevent))

    skirmishStaticEmoji   = get(emojiList, id = emojiID["SkirmishDie"])
    assaultStaticEmoji    = get(emojiList, id = emojiID["AssaultDie"])
    raidStaticEmoji       = get(emojiList, id = emojiID["RaidDie"])

    resultMessage = "## Your rolls:\n"
    for roll in skirmishList:
        resultMessage += "### * <:" + skirmishStaticEmoji.name + ":" + str(skirmishStaticEmoji.id) + ">:  "
        resultList = dieLookup["Skirmish"][roll]
        for result in resultList:
            resEmoji = get(emojiList, id = emojiID[result])
            resultMessage += "<:" + resEmoji.name + ":" + str(resEmoji.id) + "> "
        resultMessage += "\n"
    resultMessage += "\n"

    for roll in assaultList:
        resultMessage += "### * <:" + assaultStaticEmoji.name + ":" + str(assaultStaticEmoji.id) + ">:  "
        resultList = dieLookup["Assualt"][roll]
        for result in resultList:
            resEmoji = get(emojiList, id = emojiID[result])
            resultMessage += "<:" + resEmoji.name + ":" + str(resEmoji.id) + "> "
        resultMessage += "\n"
    resultMessage += "\n"

    for roll in raidList:
        resultMessage += "### * <:" + raidStaticEmoji.name + ":" + str(raidStaticEmoji.id) + ">:  "
        resultList = dieLookup["Raid"][roll]
        for result in resultList:
            resEmoji = get(emojiList, id = emojiID[result])
            resultMessage += "<:" + resEmoji.name + ":" + str(resEmoji.id) + "> "
        resultMessage += "\n"
    resultMessage += "\n"

    for roll in numberList:
        resultMessage += "### * <:" + numberEmoji.name + ":" + str(numberEmoji.id) + ">:  "
        resultList = dieLookup["Number"][roll]
        for result in resultList:
            resultMessage += result
        resultMessage += "\n"
    resultMessage += "\n"

    for roll in eventList:
        resultMessage += "### * <:" + eventEmoji.name + ":" + str(eventEmoji.id) + ">:  "
        resultList = dieLookup["Event"][roll]
        for result in resultList:
            resultMessage += result
        resultMessage += "\n"

    await ctx.edit(content=resultMessage)

actionCardList = [
        "agression",
        "mobilization",
        "administration",
        "construction",
        "event",
        "faithful_zeal",
        "faithful_wisdom",
        ]

actionCardRanges = {
        "agression" : [1,7],
        "mobilization" : [1,7],
        "administration" : [1,7],
        "construction" : [1,7],
        "event" : [1,3],
        "faithful_zeal" : [1,9],
        "faithful_wisdom" : [1,9],
        }

@arcs.command(name="action_card")
async def showActionCard(ctx: discord.ApplicationContext, actioncardname: Option(str, "Name of the action card to summon.", required=True, choices=actionCardList), actioncardnumber: Option(int, "Number of the action card to summon.", required=True, min_value=1, max_value=9)):
    if actioncardnumber < actionCardRanges[actioncardname][0] or actioncardnumber > actionCardRanges[actioncardname][1]:
        await ctx.respond("Sorry, the " + str(actioncardnumber) + " of " + actioncardname + " is not a real card dude :I")

    actionCard = discord.File("./assets/arcs/Individual Action/" + actioncardname + "_" + str(actioncardnumber) + ".jpg", filename = actioncardname + "_" + str(actioncardnumber) + ".jpg", description = "The " + str(actioncardnumber) + " of " + actioncardname + ".")

    await ctx.respond(content="Woah look at this cool action card:", file=actionCard)

courtCardList = [
        "admin_union",
        "arms_union",
        "call_to_action",
        "construction_union",
        "court_enforcers",
        "elder_broker",
        "farseers",
        "fuel_cartel",
        "galactic_bards",
        "gatekeepers",
        "guild_struggle",
        "lattice_spies",
        "loyal_empaths",
        "loyal_engineers",
        "loyal_keepers",
        "loyal_marines",
        "loyal_pilots",
        "mass_uprising",
        "material_cartel",
        "mining_interest",
        "outrage_spreads",
        "populist_demands",
        "prison_wardens",
        "relic_fence",
        "secret_order",
        "shipping_interest",
        "silver_tongues",
        "skirmishers",
        "song_of_freedom",
        "spacing_union",
        "sworn_guardians",
        ]

async def courtAutocomplete(ctx: discord.AutocompleteContext):
    cards = [card for card in courtCardList if card.startswith(ctx.value.lower())]
    return cards[:25]

@arcs.command(name="court_card")
async def showCourtCard(ctx: discord.ApplicationContext, courtcardname: Option(str, "Name of the court card to summon.", required=False, autocomplete=courtAutocomplete, default=None)):    
    courtCard = discord.File("./assets/arcs/Individual Court/" + courtcardname + ".jpg", filename = courtcardname + ".jpg", description = courtcardname)

    await ctx.respond(content="Woah look at this cool court card:", file=courtCard)

@misc.command(name="map", guild_ids=commPlaysIDs)
async def showMap(ctx: discord.ApplicationContext, mapstring: Option(str, "The Map String"), name: Option(str, "The Map's Name", required=False, default="tempMap"), forceregen: Option(bool, "Force Froggy to regenerate the map.", required=False, default=False), inclspikes: Option(bool, "Include Mallice and Creuss", required=False, default=False)):
    """Generates a map image from a string of numbers"""
    guild = ctx.guild
    if name == "tempMap":
        forceregen = True

    adminDict = await pickleLoadMemberData(adminObj())

    if name in adminDict["Banned Maps"]:
        await ctx.respond(content = "Sorry, " + name + " is a reserved map name, please use a different name.")
        return

    await ctx.respond(content = "Generating Map", delete_after=30)

    mapImageFile = await loadMap(mapstring, name, forceregen, inclspikes)

    if name:
        fn = name + ".png"
    else:
        fn = "Map.png"
    mapFile = discord.File(mapImageFile, filename=fn, description="A Twilight Imperium Map")

    await ctx.respond(content = "Here is your map:", file=mapFile)

@misc.command(name="listrole")
async def listRole(ctx: discord.ApplicationContext, role: discord.Role):
    outstr = ""

    for member in role.members:
        if(member.nick):
            outstr = outstr + member.nick + " (" + member.name + ")\n"
        else:
            outstr = outstr + member.name + "\n"


    outstr = outstr[:-1]
    fileOut = discord.File(io.StringIO(outstr), filename="roleList.txt", description="A list of users in " + role.name + ".")

    await ctx.respond(content = "Here is the list of members in " + role.name, file=fileOut)

@bot.message_command(name="pin_message")
async def toggleMessagePin(ctx: discord.ApplicationContext, message: discord.Message):
    status = message.pinned
    outMessage = ""
    if(status):
        await message.unpin()
        outMessage = "Message unpinned."
    else:
        await message.pin()
        outMessage = "Message pinned."

    await ctx.respond(content = outMessage, ephemeral = True, delete_after = 60)

class messageModal(Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.reservations = {}

        super().__init__(*args, **kwargs)
                
        self.add_item(InputText(label="What should the message be?", style=discord.InputTextStyle.long))

    def setReservedValues(self, ReservedDict):
        self.reservations = ReservedDict

    async def callback(self, interaction: discord.Interaction):
        replyTo = self.reservations["reply"]
        print(replyTo)
        if(replyTo):
            await replyTo.reply(content=self.children[0].value)
            await interaction.respond(content = "Sent reply.", ephemeral=True, delete_after=5)
        else:
            await interaction.respond(content = "No message found.", ephemeral=True, delete_after=20)

@bot.message_command(name="reply")
async def replyAsFroggy(ctx: discord.ApplicationContext, message: discord.Message):
    guild = ctx.guild
    adminID = GMRoles[guild.id]
    userAdmin = get(ctx.author.roles, id=adminID)
    if(not(userAdmin)):
        ctx.respond(content = "You do not have permission to use this command.", ephemeral=True, delete_after=10)
        return;

    mModal = messageModal(title="Reply message")
    mModal.setReservedValues({'reply': message})
    await ctx.send_modal(mModal)


@bot.message_command(name="add_poll_to_role")
async def addPollUsers(ctx: discord.ApplicationContext, message: discord.Message):
    poll = message.poll
    guild = ctx.guild
    gameRole = get(guild.roles, id=1441493469968470176)
    voters = []

    await ctx.respond(content = "Adding users from this poll to the player role. . .")

    for answer in poll.answers:
        voters.extend(await answer.voters().flatten())
        
    voters = list(set(voters))

    for user in voters:
        if not(user in gameRole.members):
            await user.add_roles(gameRole)

    await ctx.edit(content = "Finished adding users from this poll to the player role.")

class genDropdown(discord.ui.Select):
    def __init__(self, name, options):
        super().__init__(placeholder=name, min_values=1, max_values=1, options=options, custom_id="frogtestID")

    async def callback(self, interaction: discord.Interaction):
        gameName = interaction.message.content.split("**")[1]

        choice = self.values[0]
        mapAddress = saveAddress+gameName+"_"+choice+"_gameState.png"
        if choice == "Full Map":
            mapAddress = saveAddress+gameName+".png"

        mapFile = discord.File(mapAddress, filename=gameName+"_"+choice+"_gameState.png", description="A Frogged Map")
        await interaction.message.edit(files=[mapFile])
        await interaction.response.defer()


hsIDFromFaction = {
        "Arborec" : "5", 
        "Argent" : "58", 
        "Barony" : "10", 
        "Cabal" : "54",
        "Empyrean" : "56", 
        "Ghosts" : "17", 
        "Hacan" : "16", 
        "Jol-Nar" : "12", 
        "Keleres [Argent]" : "58k", 
        "Keleres [Mentak]" : "2k", 
        "Keleres [Xxcha]" : "14k",
        "L1Z1X" : "6", 
        "Mahact" : "52", 
        "Mentak" : "2",
        "Muaat" : "4",
        "Naalu" : "9", 
        "Naaz-Rokha" : "57", 
        "Nekro" : "8", 
        "Nomad" : "53",
        "Saar" : "11", 
        "Sardakk" : "13", 
        "Sol" : "1", 
        "Titans" : "55",
        "Winnu" : "7", 
        "Xxcha" : "14", 
        "Yin" : "3", 
        "Yssaril" : "15",
        }

@frog.command(name="initfroggame")
async def inFrog(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), mapstring: Option(str, "The Map String")):
    await ctx.respond(content = "Generating a new Frog wow~!")
    mapObj = mapStringToTilePosSet(mapstring)
    print("Map imported")

    factionlist = []

    for sys in mapObj:
        if mapObj[sys] in hsIDFromFaction.values():
            factionlist.append(list(hsIDFromFaction.keys())[list(hsIDFromFaction.values()).index(mapObj[sys])])

    print("Factions defined")

    gameFrog = await testDarkMap(mapObj, factionlist, gamename)

    print("Frog instantiated")

    colors = []
    for team in gameFrog.teams:
        colors.append(team.teamColor)
    strOptions = ["Full Map"]
    strOptions.extend(colors)

    print("Colors assigned")

    ddOptions = []
    for sop in strOptions:
        ddOptions.append(discord.SelectOption(label=sop))

    vw = discord.ui.View(timeout=None)
    sel = genDropdown(name="Choose one option:", options = ddOptions)
    vw.add_item(sel)
    newMessage = "**"+gamename+"**\nFrog generated!\nThe colors in this game are:"+str(colors)+"\n\nChoose a team's map to view:"
    await ctx.edit(content=newMessage, view=vw)

class teamColorPrompt(Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(InputText(label="Colors, as HUE numbers, separated by ','", style=discord.InputTextStyle.long, custom_id="colorInput"))
        self.reservations = {}

    def edit_prompt(self, label="", value=""):
        prompt = get(self.children, custom_id="colorInput")
        prompt.label=label
        prompt.value=value

    def setReservedValues(self, ReservedDict):
        self.reservations = ReservedDict
        if("preset" in ReservedDict.keys() and ReservedDict["preset"]):
            gameFrog = self.reservations["gf"]
            teamDict = readTeamData(gameFrog.gameName)
            valmsg = ""
            for team in teamDict.keys():
                valmsg = valmsg + team + ": \n"
            self.edit_prompt(label="Colors, as HUE numbers, for each team.", value=valmsg)

    async def setPresetColors(self, interaction: discord.Interaction):
        gameFrog = self.reservations["gf"]
        teamDict = readTeamData(gameFrog.gameName)
        response = get(self.children, custom_id="colorInput").value

        teams = response.split("\n")

        colorMatchDict = {}
        outmsg = ""

        for team in teams:
            val = team.split(":")
            teamname = val[0]
            color = val[1].strip()

            if(color == "w"):
                colorMatchDict[teamDict[teamname]["teamHSID"]] = "white"
                color = "white"
                team = val[0] + ": White"
            elif(color == "b"):
                colorMatchDict[teamDict[teamname]["teamHSID"]] = "black"
                color = "black"
                team = val[0] + ": Black"
            elif(color == "y"):
                colorMatchDict[teamDict[teamname]["teamHSID"]] = "yellow"
                color = "yellow"
                team = val[0] + ": Yellow"
            elif(color == "g"):
                colorMatchDict[teamDict[teamname]["teamHSID"]] = "grey"
                color = "grey"
                team = val[0] + ": Grey"
            else:
                colorMatchDict[teamDict[teamname]["teamHSID"]] = color

            teamDict[teamname]["teamcolor"] = color
            writeTeamData(teamDict[teamname])

            outmsg = outmsg + "* " + team + "\n"

        gameFrog.reconcilePresetColors(colorMatchDict)
        writeMapData(gameFrog)
        await interaction.response.send_message("Set preset team colors to the following:\n" + outmsg[:-1])

    async def callback(self, interaction: discord.Interaction):
        if(self.reservations["preset"]):
            await self.setPresetColors(interaction)
            return
        target = self.reservations["tarID"]
        iedit = await interaction.response.send_message("Generating map of system " + str(target) + "~~")
        teamList = self.reservations["tl"]
        gameFrog = self.reservations["gf"]
        response = get(self.children, custom_id="colorInput").value
        colors = response.split(",")
        pflag = False
        if len(colors) == 1 and colors[0] == "D":
            if("preset" in gameFrog.gameState.keys() and len(gameFrog.gameState["preset"]) > 0):
                pflag = True
            colors = []
            for i in range(len(teamList)):
                colors.append(i*100)
        if len(colors) < len(teamList):
            await iedit.edit_original_response(content="Please enter the requested number of colors.")
            return
        colorMatchDict = {}
        for i in range(len(teamList)):
            if(colors[i] == "w"):
                colorMatchDict[teamList[i]] = "white"
            elif(colors[i] == "b"):
                colorMatchDict[teamList[i]] = "black"
            elif(colors[i] == "y"):
                colorMatchDict[teamList[i]] = "yellow"
            elif(colors[i] == "g"):
                colorMatchDict[teamList[i]] = "grey"
            else:
                colorMatchDict[teamList[i]] = str(int(colors[i]))

            if(pflag and str(teamList[i]) in gameFrog.gameState["preset"]):
                colorMatchDict[teamList[i]] = gameFrog.gameState["preset"][str(teamList[i])]
        mapString = gameFrog.getSingleSystemMapString(target, True)
        systemFrog = gameFrog.determineFrogVisibleFromSystem(target, mapStringToTilePosSet(mapString), colorMatchDict)
        await generateUnitMapFromMapstring(mapString, systemFrog, colors[0])
        mapFile = discord.File("localmap_gameState.png", filename="" + target + "_map.png", description="A map of the systems neighboring " + target)
        await iedit.edit_original_response(content="Here is the map around system " + target, files=[mapFile])

@frog.command(name="initemptygame")
async def initEmptyGame(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), mapstring: Option(str, "The Map String"), numteams: Option(int, "The number of teams on the map.")):
    await ctx.respond(content = "Generating a new Frog wow~!")
    mapObj = mapStringToTilePosSet(mapstring)
    print("Map imported")

    teams = []

    for i in range(numteams):
        t = Team(str(i), str(i), str(i))
        teams.append(t)

    print("Empty factions defined")

    gameFrog = initGameMap(gamename, mapObj, teams)
    gameFrog.initEmpty()

    writeMapData(gameFrog)

    print("Frog instantiated")

    mapFile = discord.File(saveAddress+gamename+".png", filename=saveAddress+gamename+".png", description="A Frogged Map")

    await ctx.edit(content=gamename + " frog created.", file=mapFile)

@frog.command(name="setteamcolors")
async def setPColors(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game.")):
    gameFrog = readMapData(gamename)
    colorModal = teamColorPrompt(title ="Please provide a list of colors for each team")
    colorModal.setReservedValues({"gf" : gameFrog, "preset" : True})
    await ctx.send_modal(colorModal)

@admin.command(name="getunitmap")
async def fullUnitMap(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), usepresetcolors: Option(bool, "Use preset colors (True) or team id as color (False)", default=False, required=False)):
    await ctx.respond("Generating the full map of units in " + gamename + "~~")
    gameFrog = readMapData(gamename)
    colorMatchDict = {}
    if usepresetcolors:
        colorMatchDict = gameFrog.gameState["preset"]
    overlayAddress = await overlayUnitsOnFullMap(gameFrog, 0, colorMatchDict)
    mapFile = discord.File(overlayAddress, filename=overlayAddress, description="A full map of units in " + gamename)
    await ctx.edit(content="Here is the full map of units in " + gamename, files=[mapFile])

@frog.command(name="getsystemmap")
async def sysMap(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), system: Option(str, "Tile ID")):
    gameFrog = readMapData(gamename)
    teamList = gameFrog.determineTeamsVisibleFromSystem(system, True)
    colorModal = teamColorPrompt(title = "Please provide a priority list of " + str(len(teamList)) + " colors.")
    colorModal.setReservedValues({"gf" : gameFrog, "tl" : teamList, "tarID": system, "preset" : False})
    await ctx.send_modal(colorModal)

@frog.command(name="edit_space_token")
async def editSpaceToken(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), system: Option(str, "Tile ID"), tokencode: Option(int, "Int id of token.")):
    gameFrog = readMapData(gamename)
    systemPos = gameFrog.getPosFromTileNum(system)
    token = spaceToken[tokencode]
    if token["image"] in gameFrog.gameState[systemPos]["spTokens"]:
        gameFrog.gameState[systemPos]["spTokens"].remove(token["image"])
    else:   
        gameFrog.gameState[systemPos]["spTokens"].append(token["image"])

    if(token["wormhole"] != "none"):
        if systemPos in gameFrog.gameState["systemsWithWormholes"][token["wormhole"]]:
            gameFrog.gameState["systemsWithWormholes"][token["wormhole"]].remove(systemPos)
        else:
            gameFrog.gameState["systemsWithWormholes"][token["wormhole"]].append(systemPos)

    writeMapData(gameFrog)
    await ctx.respond(token["name"] + " Updated")

@frog.command(name="edit_planet_token")
async def editPlanetToken(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), system: Option(str, "Tile ID"), tokencode: Option(int, "Int id of token."), planet: Option(str, "The exact name of the planet.")):
    gameFrog = readMapData(gamename)
    systemPos = gameFrog.getPosFromTileNum(system)
    token = attachments[tokencode]
    flag = False
    if not(type(gameFrog.gameState[systemPos]["planets"][planet]["attachments"]) is list):
        gameFrog.gameState[systemPos]["planets"][planet]["attachments"] = []
    for attachment in gameFrog.gameState[systemPos]["planets"][planet]["attachments"]:
        if attachment["name"] == token["name"]:
            gameFrog.gameState[systemPos]["planets"][planet]["attachments"].remove(attachment)
            flag = True
    if not(flag):
        gameFrog.gameState[systemPos]["planets"][planet]["attachments"].append(token)

    print(gameFrog.gameState[systemPos]["planets"])
    print(gameFrog.gameState[systemPos]["planets"][planet]["attachments"])
    print(token)
    writeMapData(gameFrog)
    await ctx.respond(token["name"] + " Updated")

@frog.command(name="edit_team")
async def editTeam(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name"), teamhsid: Option(str, "Team HS ID", required=False, default=None), newteamname: Option(str, "Team Name", default=None, required=False)):
    teamDict = readTeamData(gamename)
    team = empty_team
    team['gamename'] = gamename
    if(teamname in teamDict.keys()):
        team = teamDict[teamname]
        if teamhsid:
            team["teamHSID"] = teamhsid 
        if newteamname:
            team["teamname"] = newteamname
            teamDict[newteamname] = team
            del teamDict[teamname]
        else:
            teamDict[teamname] = team
    else:
        if teamhsid:
            team["teamHSID"] = teamhsid 
        team["teamname"] = teamname
        teamDict[teamname] = team
    writeTeamData(team)
    await ctx.respond(content = team["teamname"] + " has been saved :).")

@frog.command(name="add_members_to_team")
async def addToTeam(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name"), memberone: Option(discord.User, "Member to add to team."), membertwo: Option(discord.User, "Member to add to team.", required=False, default=None), memberthree: Option(discord.User, "Member to add to team.", required=False, default=None)):
    team = readTeamData(gamename)[teamname]
    memberList = team['team']
    if not(memberone.id in memberList):
        memberList.append(memberone.id)
    if membertwo and not(membertwo.id in memberList):
        memberList.append(membertwo.id)
    if memberthree and not(memberthree.id in memberList):
        memberList.append(memberthree.id)
    team['team'] = memberList
    writeTeamData(team)
    await ctx.respond(content = "Added members to " + team["teamname"])

@frog.command(name="remove_members_from_team")
async def removeFromTeam(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name"), memberone: Option(discord.User, "Member to add to team.", required=False, default=None), membertwo: Option(discord.User, "Member to add to team.", required=False, default=None), memberthree: Option(discord.User, "Member to add to team.", required=False, default=None)):
    team = readTeamData(gamename)[teamname]
    memberList = team['team']
    delFlag = False
    if not(memberone):
        deleteTeam(team)
        memberList = []
        delFlag = True
    elif memberone.id in memberList:
        memberList.remove(memberone.id)
    if membertwo and (membertwo.id in memberList):
        memberList.remove(membertwo.id)
    if memberthree and (memberthree.id in memberList):
        memberList.remove(memberthree.id)
    team['team'] = memberList
    writeTeamData(team)
    memberListUsers = []
    for m in memberList:
        memberListUsers.append(get(ctx.guild.members, id=m))
    if len(memberListUsers) < 1:
        deleteTeam(team)
        delFlag = True
    if delFlag:
        await ctx.respond(content = "Deleted " + team["teamname"])
    else:
        await ctx.respond(content = "Removed members from " + team["teamname"])

@frog.command(name="list_team_members")
async def listTeam(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name", required=False, default=None)):
    if(teamname):
        team = readTeamData(gamename)[teamname]
        memberList = team['team']
        memberListUsers = []
        for m in memberList:
            memberListUsers.append(get(ctx.guild.members, id=m))

        outmsglist = ""
        k = 0
        for m in memberListUsers:
            if m:
                outmsglist = outmsglist + m.display_name + ", "
            k = k + 1
            if k > 4:
                k = 0
                outmsglist = outmsglist + "\n"

        outmsglist = outmsglist[:-2]
        if(k == 0):
            outmsglist = outmsglist[:-1]

        await ctx.respond(content = teamname + " has " + str(len(memberList)) + " members:\n" + outmsglist)
    else:
        teams = readTeamData(gamename)
        teamListOut = "### Here is a list of each team in " + gamename + ":"
        teamListOutNoMembers = "### Here is a list of each team in " + gamename + ":"
        for team in teams.keys():
            teamListOut = teamListOut + "\n* ** " + team + ": **  "
            teamListOutNoMembers = teamListOutNoMembers + "\n* ** " + team + " **"
            memberList = teams[team]['team']
            memberListUsers = []
            membersInDiscord = False
            for m in memberList:
                member = get(ctx.guild.members, id=m)
                if(member):
                    teamListOut = teamListOut + member.display_name + ", "
                    membersInDiscord = True
            if not(membersInDiscord):
                deleteTeam(teams[team])
                iteam = 10+len(team)
                teamListOut = teamListOut[:-iteam]
            teamListOut = teamListOut[:-2]

        fileOut = discord.File(io.StringIO(teamListOut), filename="TeamList.txt", description="A list of teams and their members.")

        await ctx.respond(content = teamListOutNoMembers, file=fileOut)

async def generatePingMessage(ctx, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name"), listFlag: bool):
    team = readTeamData(gamename)[teamname]
    memberList = team['team']
    memberListUsers = []
    for m in memberList:
        memberListUsers.append(get(ctx.guild.members, id=m))

    pingMessage = ""
    pingMessageList = []

    for m in memberListUsers:
        if m:
            if len(pingMessage) < 1800:
                pingMessage = pingMessage + " " + m.mention
            else:
                pingMessageList.append(pingMessage)
                pingMessage = m.mention

    pingMessageList.append(pingMessage)
    if listFlag:
        return pingMessageList
    else:
        return pingMessage

@frog.command(name="ping_team")
async def pingTeam(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name")):
    pingMessage = await generatePingMessage(gamename, teamname)
    await ctx.respond(content = "Pinging" + pingMessage)


@frog.command(name="sync_team_threads")
async def syncTeamThreads(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name"), channel: Option(discord.TextChannel, "Channel containing threads to sync.")):
    team = readTeamData(gamename)[teamname]
    memberList = team['team']
    memberListUsers = []

    await ctx.respond(content="Syncing threads for members of " + team['teamname'])

    for m in memberList:
        mem = get(ctx.guild.members, id=m)
        if mem:
            memberListUsers.append(mem)

    threads = channel.threads
    bannedThreads = await loadBannedThreads(ctx.guild)
    cthr = 0
    for thread in threads:
        if thread.id in bannedThreads:
            continue

        mIDs = []
        tmem = await thread.fetch_members()
        for m in tmem:
            mIDs.append(m.id)

        if(set(memberList).intersection(mIDs)):
            cthr = cthr + 1
            for u in memberListUsers:
                if u and not(u.id in mIDs):
                    await thread.add_user(u)

    archivedThreads = channel.archived_threads(private=True, limit=None)
    async for thread in archivedThreads:
        if thread.id in bannedThreads:
            continue

        mIDs = []
        await thread.edit(archived=False)
        tmem = await thread.fetch_members()
        for m in tmem:
            mIDs.append(m.id)

        if(set(memberList).intersection(mIDs)):
            cthr = cthr + 1
            for u in memberListUsers:
                if u and not(u.id in mIDs):
                    await thread.add_user(u)

    print("Finished long command")
    await ctx.edit(content= "Finished syncing " + str(cthr) + " threads for " + team['teamname'])

@frog.command(name="remove_team_from_thread")
async def removeTeamThreads(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), teamname: Option(str, "Team Name")):
    team = readTeamData(gamename)[teamname]
    memberList = team['team']
    memberListUsers = []

    await ctx.respond(content="Removing members of " + team['teamname'] + " from this thread.")

    for m in memberList:
        memberListUsers.append(get(ctx.guild.members, id=m))

    thread = ctx.channel
    if not(thread):
        await ctx.edit(content= "Error: could not discern thread.")
        return

    mIDs = []
    tmem = await thread.fetch_members()
    for m in tmem:
        mIDs.append(m.id)

    if(set(memberList).intersection(mIDs)):
        for u in memberListUsers:
            if (u.id in mIDs):
                await thread.remove_user(u)

    await ctx.edit(content="Finished removing " + team['teamname'] + " from this thread. :)")

    await ctx.send_followup(content="Finished removing " + team['teamname'] + " from this thread. :)")

@admin.command(name="reset_ban_phrase_dict")
async def resetBanPhraseGuild(ctx: discord.ApplicationContext):
    await writeBannedPhrases(ctx.guild, {})
    await ctx.respond("Reset banned phrase list in this guild.")

@admin.command(name="report_banned_phrases")
async def reportBanPhraseGuild(ctx: discord.ApplicationContext):
    bannedPhrases = await loadBannedPhrases(ctx.guild)
    outmsg = ""
    for key in bannedPhrases.keys():
        needLink = bannedPhrases[key]
        if needLink:
            outmsg += "* " + key + " as a part of a link.\n"
        else:
            outmsg += "* " + key + " as a part of any message.\n"
    await ctx.respond("The following phrases are banned in this guild:\n" + outmsg)

@admin.command(name="ban_phrase_from_messages")
async def banPhraseFromGuild(ctx: discord.ApplicationContext, phrase: Option(str, "The phrase to be restricted from new messages."), link: Option(bool, "Only restrict phrase if part of a link?", required=False, default=False)):
    bannedPhrases = await loadBannedPhrases(ctx.guild)
    tFlag = False
    if not(phrase.lower() in bannedPhrases.keys()):
        bannedPhrases[phrase.lower()] = link
        tFlag = True
    elif thread.id in bannedPhrases:
        try:
            del bannedPhrases[phrase.lower()]
        except:
            pass
        tFlag = False

    await writeBannedPhrases(ctx.guild, bannedPhrases)
    omsg=""
    if(tFlag):
        omsg = " added to "
    else:
        omsg = " removed from "
    await ctx.respond(content = phrase + omsg + "the banned phrases list.")

class systemFleetPrompt(Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.reservations = {}
        self.reservations["tileID"] = kwargs.get('tileID', -1)
        del kwargs['tileID']
        self.reservations["gameFrog"] = kwargs.get('gameFrog', None)
        del kwargs['gameFrog']
        self.reservations["teamCC"] = kwargs.get('teamCC', None)
        del kwargs['teamCC']

        super().__init__(*args, **kwargs)

        gf = self.reservations["gameFrog"]
        state = gf.getSystemState(str(self.reservations["tileID"]))

        # Construct space fleet prompt, use existing units if they are there
        spaceFleet = state["fleet"]["list"]
        spacePrompt = modalSpaceFleetTemplate
        testPrompt = spacePrompt.lower()
        for unit in spaceFleet:
            if spaceFleet[unit] > 0 and unit in testPrompt:
                spacePrompt = spacePrompt[:testPrompt.find(unit)+len(unit)+3] + str(spaceFleet[unit]) + spacePrompt[testPrompt.find(unit)+len(unit)+4:]
        scolor = state["fleet"]["color"]
        if type(scolor) is int:
            spacePrompt = spacePrompt[:spacePrompt.find("TeamHSID")+len("TeamHSID")+3] + str(scolor) + spacePrompt[spacePrompt.find("TeamHSID")+len("TeamHSID")+4:]

        self.add_item(InputText(label="Space Fleet [only change numbers]", style=discord.InputTextStyle.long, value=spacePrompt))

        if self.reservations["tileID"] in systems.keys():
            for p in systems[self.reservations["tileID"]]:
                planetPrompt = modalPlanetFleetTemplate.replace("[PLANETNAME]", p)
                planetFleet = state["planets"][p]["fleet"]["list"]
                testPrompt = planetPrompt.lower()
                for unit in planetFleet:
                    if planetFleet[unit] > 0 and unit in testPrompt:
                        planetPrompt = planetPrompt[:testPrompt.find(unit)+len(unit)+3] + str(planetFleet[unit]) + planetPrompt[testPrompt.find(unit)+len(unit)+4:]
                pcolor = state["planets"][p]["fleet"]["color"]
                if type(pcolor) is int:
                    planetPrompt = planetPrompt[:planetPrompt.find("TeamHSID")+len("TeamHSID")+3] + str(pcolor) + planetPrompt[planetPrompt.find("TeamHSID")+len("TeamHSID")+4:]
                self.add_item(InputText(label=p + " Fleet [only change numbers]", style=discord.InputTextStyle.long, value=planetPrompt))

        if "Mirage" in state["planets"]:
            planetPrompt = modalPlanetFleetTemplate.replace("[PLANETNAME]", "Mirage")
            planetFleet = state["planets"]["Mirage"]["fleet"]["list"]
            for unit in planetFleet:
                if planetFleet[unit] > 0:
                    planetPrompt = planetPrompt[:planetPrompt.find(unit)+len(unit)+3] + str(planetFleet[unit]) + planetPrompt[:planetPrompt.find(unit)+len(unit)+3:]
            self.add_item(InputText(label="Mirage" + " Fleet [only change numbers]", style=discord.InputTextStyle.long, value=planetPrompt))

    def setReservedValues(self, ReservedDict):
        self.reservations = ReservedDict

    async def callback(self, interaction: discord.Interaction):
        tileID = self.reservations["tileID"]
        gameFrog = self.reservations["gameFrog"]
        teamDict = readTeamData(gameFrog.gameName)
        teamname = self.reservations["teamCC"]
        iedit = await interaction.response.send_message("Updating system " + str(tileID) + "~~")
        numPlanets = len(self.children) - 1
        rawSpaceFleet = self.children[0].value
        rawPlanetFleets = []
        for n in range(numPlanets):
            rawPlanetFleets.append(self.children[n+1].value)

        #Parse Space Fleet
        spaceMessage = ""
        rawSpaceUnits = rawSpaceFleet.split("\n")
        spaceUnits = {}
        for unit in rawSpaceUnits:
            if ":" in unit:
                u = unit.replace(" ", "").split(":")
                spaceUnits[u[0]] = int(u[1])
                if(int(u[1]) > 0):
                    spaceMessage = spaceMessage + "\n* " + u[0] + " : " + u[1]

        #Parse Planet Fleets
        planetMessage = ""
        planetsUnits = {}
        for rawplanet in rawPlanetFleets:
            splanetMessage = ""
            planetName = ""
            unitDict = {}
            for unit in rawplanet.split("\n"):
                if ":" in unit:
                    u = unit.split(":")
                    for v in range(len(u)):
                        u[v] = u[v].strip()
                    if(u[0] == "Planet"):
                        planetName = u[1]
                        splanetMessage = splanetMessage + "\n# " + u[1]
                    else:
                        unitDict[u[0]] = int(u[1])
                        if(int(u[1]) > 0):
                            splanetMessage = splanetMessage + "\n* " + u[0] + " : " + u[1]
            planetsUnits[planetName] = unitDict

            if(not(":" in splanetMessage)):
                splanetMessage = splanetMessage + "\n* NONE"

            planetMessage = planetMessage + splanetMessage

        #Convert fleet dicts to system state
        stid = str(tileID)
        systemState = gameFrog.getSystemState(stid)
        for unit in spaceUnits:
            if "team" in unit.lower():
                if spaceUnits[unit] >= 0:
                    systemState["fleet"]["color"] = spaceUnits[unit]
                else:
                    systemState["fleet"]["color"] = tileID
            else:
                systemState["fleet"]["list"][unit.lower()] = spaceUnits[unit]
        for planet in planetsUnits:
            for unit in planetsUnits[planet]:
                if "team" in unit.lower():
                    if planetsUnits[planet][unit] >= 0:
                        systemState["planets"][planet]["fleet"]["color"] = planetsUnits[planet][unit]
                    else:
                        systemState["planets"][planet]["fleet"]["color"] = tileID
                else:
                    systemState["planets"][planet]["fleet"]["list"][unit.lower()] = planetsUnits[planet][unit]

        gameFrog.setSystemState(stid, systemState)
        if(teamname in teamDict.keys()):
            gameFrog.toggleCommandTokenInSystem(stid, teamDict[teamname])
        writeMapData(gameFrog)
        systemState = gameFrog.getSystemState(stid)
        CCMsg = ""
        if("commandtokens" in systemState and len(systemState["commandtokens"]) > 0):
            CCMsg = "\n# Command Tokens:\n"
            for teamID in systemState["commandtokens"].keys():
                for team in teamDict.keys():
                    if not(teamDict[team]["teamHSID"] == teamID):
                        continue
                    if("teamColor" in teamDict[team]):
                        CCMsg = CCMsg + "* " + team + " (" + teamDict[team]["teamcolor"] + ")\n"
                    else:
                        CCMsg = CCMsg + "* " + team + "\n"

        await iedit.edit_original_response(content="Updated the units in system " + str(tileID) + ":\n" + CCMsg + "# Space:" + spaceMessage + "\n" + planetMessage)

"""@frog.command(name="updatesystemunits")
async def sysMap(ctx: discord.ApplicationContext, gamename: Option(str, "Name of the game."), systemid: Option(int, "Tile ID"), toggleteamcc: Option(str, "Team Name", require=False, default="")):
    gameFrogMap = readMapData(gamename)

    fleetModal = systemFleetPrompt(title = "Fill out the units in system " + str(systemid) + ".", tileID = systemid, gameFrog = gameFrogMap, teamCC = toggleteamcc)

    await ctx.send_modal(fleetModal)
"""

@admin.command(name="deletefrogsaves")
async def delFrog(ctx: discord.ApplicationContext):
    clearMapDataPickle()

#--------------------------------------------------------------------------------#
#-------------------------------USER PIC STUFF-----------------------------------#

async def getUserPic(user):
    tempSave = "tempPic.png"

    with open(tempSave, 'wb') as f:
        await user.display_avatar.with_format("png").save(f)

    userPic = cv2.imread(tempSave, cv2.IMREAD_UNCHANGED)
    if userPic.shape[2] != 4:
        userPic = cv2.cvtColor(userPic, cv2.COLOR_RGB2RGBA)
    userPic = cv2.resize(userPic, (100,100), interpolation=cv2.INTER_LINEAR)
    userPic = await circularizePic(userPic)
    cv2.imwrite(tempSave, userPic)
    return [tempSave, userPic]

async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)

async def genUserGraphGif(ctx, uAct, oldHour, newHour, height=600, width=600, skipblanks=False):
    filename = "activity.gif"
    fileoutname = "activityOut.gif"
    gif = []
    uAccum = {}
    tItemList = [val for lis in uAct.values() for val in lis]
    vals = list(set(tItemList))
    mode = tItemList.count(max(set(tItemList), key = tItemList.count))
    leng = len(vals)
    print("Number of users:")
    print(leng)
    stepHeight = int((height-100)/mode)
    stepWidth = int((width-100)/leng) 
    basePos=(height-50,50)

    longResponse = False
    if(newHour - oldHour > 300):
        longResponse = True

    uPicLookup = {}
    uPosLookup = {}
    uinc = 0
    for user in vals:
        uTup = await getUserPic(user)
        uPic = cv2.imread(uTup[0], cv2.IMREAD_UNCHANGED)
        uPic = cv2.cvtColor(uPic, cv2.COLOR_BGRA2RGBA)
        uPicLookup[user] = uPic
        uPosLookup[user] = (basePos[0], basePos[1]+stepWidth*uinc)
        uAccum[user] = 0
        uinc = uinc+1

    k = 0
    k2 = 0
    saveFrame = np.ones((height, width, 4), np.uint8)*255
    for interval in range(oldHour, newHour+1):
        frame = np.ones((height, width, 4), np.uint8)*255
        incFlag = False
        for user in vals:
            if interval in uAct.keys():
                if user in uAct[interval]:
                    uAccum[user] = uAccum[user] + 1

                uPos = (uPosLookup[user][0]-uAccum[user]*stepHeight, uPosLookup[user][1])

                frame = await run_blocking(superimpose, frame, uPicLookup[user], uPos, True)
                saveFrame=frame
                inc = 0
            else:
                incFlag = True
                frame = saveFrame

        if incFlag:
            inc=inc+1

        if not(inc > 0 and skipblanks) and inc < 10:     
            gif.append(frame)

        percent = ((interval-oldHour)/(newHour-oldHour))*100
        L = (int)((percent*30)/100)
        L2 = (int)(percent)
        if L2 > k2:
            print()
            print("%.2f" % percent)
            print(sys.getsizeof(gif))
        if L > k:
            if not(longResponse):
                upProgress = progress_bar(progress=percent/100.0, value=int(percent), size=30)
                emb = discord.Embed(color=discord.Color.gold())
                emb.add_field(name="Processing...", value=upProgress)
                await ctx.edit(embed=emb)
        k = L
        k2 = L2 

    fps = int((newHour - oldHour)/60)
    if fps < 8:
        fps = 8
    if fps > 30:
        fps = 30
    for i in range(fps):
        gif.append(saveFrame)

    imageio.mimsave(filename, gif, 'GIF', fps=fps)
    subprocess.call(['ffmpeg', '-y', '-i', filename, '-vf', 'palettegen', 'palette.png'])
    subprocess.call(['ffmpeg', '-y', '-i', filename, '-i', 'palette.png', '-filter_complex', 'paletteuse', fileoutname])
    return [fileoutname, gif]

@misc.command(name="activitystats", description="Stats of channel activity over time. Froggy will halt during this process.", guild_ids=commPlaysIDs)
async def chnlstats(ctx: discord.ApplicationContext, sel1: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot."), sel2: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot."), 
                    sel3: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot."), sel4: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot."), 
                    sel5: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot."), sel6: Option(Union[discord.TextChannel, discord.Thread], required=False, description="A channel to plot.")):
    channelList = []
    if sel1:
        channelList.append(sel1)
    if sel2:
        channelList.append(sel2)
    if sel3:
        channelList.append(sel3)
    if sel4:
        channelList.append(sel4)
    if sel5:
        channelList.append(sel5)
    if sel6:
        channelList.append(sel6)

    coolGuy = ctx.author
    await ctx.defer()

    stats = {}
    baseStats = {
            "Total Users (sent at least 1 message)" : "0",
            "Active Users" : "0",
            "Total Messages" : "0",
            "Average Messages / Day" : "0",
            "Average User Activity" : "0",
            "Best User" : "No one somehow",
            "Coolness Factor": "0",
            }
    for channel in channelList:
        print(channel.name)
        memList = {}
        msgCount = 0
        coolFactor = 0
        lastMessage = await channel.fetch_message(channel.last_message_id)
        firstMessage = None
        async for msg in channel.history(limit=None):
            await asyncio.sleep(0)
            if (msg.author == coolGuy):
                coolFactor = coolFactor + 1
            firstMessage = msg
            if not(msg.author in memList.keys()):
                memList[msg.author] = 1
            else:
                memList[msg.author] = memList[msg.author] + 1
            msgCount = msgCount+1
        channelStats = baseStats.copy()
        channelStats["Total Messages"] = "%d"%msgCount
        start = firstMessage.created_at
        end = lastMessage.created_at
        delta = end-start
        days = delta.days + 1
        if(days == 0):
            channelStats["Average Messages / Day"] = "ERROR"
        else:
            channelStats["Average Messages / Day"] = "{:.2f}".format(float(msgCount) / days)
        channelStats["Total Users (sent at least 1 message)"] = "%d"%len(memList)
        userActivity = 0
        for val in memList.values():
            userActivity = userActivity + val
        userActivity = userActivity / len(memList)
        channelStats["Average User Activity"] = "%0.2f"%userActivity
        activeUsers = []
        bestUser = None
        for member in memList.keys():
            if memList[member] > userActivity:
                activeUsers.append(memList[member])
            if bestUser:
                if memList[member] > memList[bestUser]:
                    bestUser = member
            else:
                bestUser = member
        channelStats["Active Users"] = "%d"%len(activeUsers)
        channelStats["Best User"] = bestUser.name
        channelStats["Coolness Factor"] = "%d"%coolFactor
        stats[channel.name] = channelStats.copy()

    embedList = []
    for channel in stats.keys():
        channelEmbed = discord.Embed(title=channel)
        for stat in stats[channel].keys():
            channelEmbed.add_field(name=stat, value=stats[channel][stat])
        embedList.append(channelEmbed)

    await ctx.respond(content = "Here's some cool stats:",embeds = embedList)

@misc.command(name="usergraph", description="Graphs user actrivity in a channel over time. Froggy will halt during this process.", guild_ids=commPlaysIDs)
async def usergraphsh(ctx: discord.ApplicationContext, sel: Option(discord.TextChannel, required=False, description="The channel to plot."), duration: Option(float, required=False, default=7.0, description="Number of days to look back for messages, can be fractional."), timdiv: Option(float, required=False, default=1, description="Hours per frame"), skipblanks: Option(bool, required=False, default=False, description="Skip time divisions where there is no change.")):
    if duration == -1:
        duration = 14.0

    guild=ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        limit = 4000
    else:
        print("admin user")
        limit = None

    print(limit)

    if sel:
        channel = sel
    else:
        channel = ctx.channel

    if ((duration*24)/timdiv) > 300:
        if(not(gmRole in ctx.interaction.user.roles)):
            await ctx.respond(content="Sorry, that's just too many frames for me to handle, try using a larger time division or a shorter duration :)")

    targetDateTime = datetime.now(timezone.utc) - timedelta(days=duration)

    emb = discord.Embed(color=discord.Color.gold())
    emb.add_field(name="Processing...", value=progress_bar(progress=0, value=0, size=30))
    await ctx.respond(content="Generating User Activity Graph", embed=emb)
    emb.add_field(name="This operation will last longer than this message can be edited.", value="```ANSI\n" + genANSICOLORCODE(textColor = ANSICOLORCODES["TEXT"]["YELLOW"], bkgColor = ANSICOLORCODES["RESET"]) + "|" + genANSICOLORCODE(form = ANSICOLORCODES["RESET"]) + genANSICOLORCODE(textColor = ANSICOLORCODES["TEXT"]["RED"],bkgColor = ANSICOLORCODES["BACKGROUND"]["DARKGREY"]) + "??????????????????????????????" + genANSICOLORCODE(textColor = ANSICOLORCODES["TEXT"]["YELLOW"], bkgColor = ANSICOLORCODES["RESET"]) + "|" + genANSICOLORCODE(form = ANSICOLORCODES["RESET"]) +"\n```")
    await ctx.edit(content="Generating User Activity Graph", embed=emb)

    gifTuple = await genUserGraphGif(ctx, userActivity, oldest, newest, skipblanks=skipblanks)
    gifout = discord.File(gifTuple[0], filename="ActivityGif.gif", description=f"A gif of activity in {channel.name}")

    await ctx.send_followup(content="User Graphic:", file=gifout)
    print("Finished Graph Gen")

monthLookup = {
        "1" : 1,
        "jan" : 1,
        "january" : 1,
        "2" : 2,
        "feb" : 2,
        "february" : 2,
        "febuary" : 2,
        "3" : 3,
        "mar" : 3,
        "march" : 3,
        "4" : 4,
        "apr" : 4,
        "april" : 4,
        "5" : 5,
        "may" : 5,
        "6" : 6,
        "jun" : 6,
        "june" : 6,
        "7" : 7,
        "jul" : 7,
        "july" : 7,
        "8" : 8,
        "aug" : 8,
        "august" : 8,
        "9" : 9,
        "sep" : 9,
        "sept" : 9,
        "september" : 9,
        "10" : 10,
        "oct" : 10,
        "october" : 10,
        "11" : 11,
        "nov" : 11,
        "november" : 11,
        "12" : 12,
        "dec" : 12,
        "decemeber" : 12,
        }

@bot.command(name="timestamp", description="Generates universal timestamp UTC time. Month as number or full or standard 3 letter form in English")
async def usergraphsh(ctx: discord.ApplicationContext, year: Option(str, required=True, name="year", description="Year of date"), month: Option(str, required=True, name="month", description="Month of the year, as number, name, or 3 letter form"), day: Option(str, required=True, name="day", description="Day of the month"), time: Option(str, required=True, name="time", description="Time in 24hour format hh:mm"), tmzone: Option(str, required=False, name="timezone_abbr", description="Abbreviation of the timezone used", default="UTC")):
    try:
        yearn = int(year)
        monthn = monthLookup[month.lower()]
        dayn = int(day)
        timen = time.split(":")
        hourn = int(timen[0])
        minuten = int(timen[1])
    except Exception as err:
        logging.error(traceback.format_exc())
        await ctx.respond("Invalid parameters, please make each parameter was input correctly.", ephemeral = True)
        return

    UTCoffsetHR = 0
    UTCoffsetMN = 0
    if(tmzone in timezones):
        UTCoffsetHR = int(timezones[tmzone].split(":")[0])
        UTCoffsetMN = int(timezones[tmzone].split(":")[1])


    date = datetime(year = yearn, month = monthn, day = dayn, hour = hourn, minute = minuten, tzinfo=timezone.utc) - timedelta(hours=UTCoffsetHR, minutes=UTCoffsetMN)

    utimestamp = int(date.timestamp())

    await ctx.respond("Your timestamp is: <t:" + str(utimestamp) + ":f> and here is the code to copy that: `<t:" + str(utimestamp) + ":f>`")

@bot.event
async def on_error(ctx, error):
    print("ERROR: " + str(error))


if __name__=="__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
