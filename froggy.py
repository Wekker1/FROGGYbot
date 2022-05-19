import discord
import logging
from discord.ext import commands
from discord.utils import get
from discord.commands import Option
from discord.commands import permissions
import pickle
import random
import os
import io
import pandas
from os.path import exists
import mysql.connector
from dotenv import load_dotenv
import mapRender
from mapRender import *
import frontend
from frontend import *
# Robodane import stuff
import asyncio
import sys, getopt
import math
import time
from datetime import datetime
import csv
import re
from Levenshtein import distance
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
from discord_slash.utils import manage_components
from discord_slash.model import ButtonStyle

# robodane vars
levDistMin = 2
fuzzDistMin = 80
botColor = 0x2b006b
delete_response = False
time_to_delete_response = 300
# gm power role
power_user_roles = [951230650680225863]

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

backUps = {
856341009218666506 : 'testAss.pickle',
847560709730730064 : 'restoreList.txt',
}

dataFile = "staticInfo.xlsx"
dataTabs = ["tiles", "planets", "factions", "attachments", "technologies"]
dataTitles = {
    'tiles': ['Tile Number', 'Planets (comma separated)', 'anomalies', 'wormholes (comma separated)', 'frontier (no planets)', 
        'hyperlane', 'faction', 'Special'],
           
    'planets': ['Planet Name', 'Tile Number', 'Resources', 'Influence', 'Trait', 'Tech Specialties', 'Legendary', 'Start Readied', 
        'Faction', 'Pseudonyms'],
           
    'factions': ['lookup name', 'full name', 'starting tech', 'starting units', 'home system tile number', 
        'faction ability names (comma separated)', 'faction ability text (comma separated)', 'flagship name', 'mech name',
        'mech ability text', 'faction tech 1 name', 'faction tech 1 unit replaced', 'replaced unit stats (cost,combat,move,capacity)',
        'faction tech 2 name', 'faction tech 2 unit replaced', 'replaced unit stats (cost,combat,move,capacity).1', 'agent name',
        'agent ability', 'commander name', 'commander condition', 'commander ability', 'hero locked name', 'hero unlocked name',
        'hero ability', 'promissory note name', 'promissory note text'],
           
    'attachments': ['lookup name (idk yet)', 'attachment name', 'resources', 'influence', 'trait', 'techspec', 
        'legendary (true or false)', 'abilities ie DMZ (true or false)', 'alt lookup name (for attachments with alternative effects)', 'text'],
           
    'technologies': ['name', 'color (blank if unit)', 'requirements', 'unit', 'text','pseudonyms (comma separated)'],
}
defaults = {
    'tiles': {
        'Tile Number' : -1, 
        'Planets (comma separated)' : "", 
        'anomalies' : "", 
        'wormholes (comma separated)' : "", 
        'frontier (no planets)' : False, 
        'hyperlane' : False, 
        'faction' : "", 
        'Special' : False,
    },

    'planets' : {
        'Planet Name' : "", 
        'Tile Number' : -1, 
        'Resources' : 0, 
        'Influence' : 0, 
        'Trait' : "", 
        'Tech Specialties' : "", 
        'Legendary' : False, 
        'Start Readied' : False, 
        'Faction' : "", 
        'Pseudonyms' : "",
    },

    'factions' : {
        'lookup name' : "", 
        'full name' : "", 
        'starting tech' : "", 
        'starting units' : "", 
        'home system tile number' : -1, 
        'faction ability names (comma separated)' : "", 
        'faction ability text (comma separated)' : "", 
        'flagship name' : "", 
        'mech name' : "",
        'mech ability text' : "", 
        'faction tech 1 name' : "", 
        'faction tech 1 unit replaced' : "", 
        'replaced unit stats (cost,combat,move,capacity)' : "",
        'faction tech 2 name' : "", 
        'faction tech 2 unit replaced' : "", 
        'replaced unit stats (cost,combat,move,capacity).1' : "", 
        'agent name' : "",
        'agent ability' : "", 
        'commander name' : "", 
        'commander condition' : "", 
        'commander ability' : "", 
        'hero locked name' : "", 
        'hero unlocked name' : "",
        'hero ability' : "", 
        'promissory note name' : "", 
        'promissory note text' : "",
    },

    'attachments' : {
        'lookup name (idk yet)' : "", 
        'attachment name' : "", 
        'resources' : 0, 
        'influence' : 0, 
        'trait' : "", 
        'techspec' : "", 
        'legendary (true or false)' : False, 
        'abilities ie DMZ (true or false)' : False, 
        'alt lookup name (for attachments with alternative effects)' : "", 
        'text' : "",
    },

    'technologies' : {
        'name' : "", 
        'color (blank if unit)' : "", 
        'requirements' : "", 
        'unit' : "", 
        'text' : "",
        'pseudonyms (comma separated)' : "",
    },
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
964306086955999264,
874051960372883467,
951970331386585121,
953386946749681757,
964311549466517534,


# Users
951230650680225863, # GM
951999879637516418, # Spectator

# Test Users
964333967807500310,
]

GMRoles = {
847560709730730064 : 951230650680225863, # Community
856341009218666506 : 964333967807500310, # Test
}

GMRolesList = [
951230650680225863, # Community
964333967807500310, # Test
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

newMemberFlag = "pFlagNewMembers"

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


async def assignRandomTeams(memberList, guild):
    teamList = roleListByGuild[guild.id]
    selector = await generateSelectorList(len(teamList))
    assignMemory = await pickleLoadMemberData(guild)
    teamPop = await getTeamPop(guild)

    if len(assignMemory) < 1:
        assignMemory[newMemberFlag] = False

    for member in memberList:
        if member.id in assignMemory:
            assignment = assignMemory[member.id]
            role = get(member.guild.roles, id=assignment)
            print(member.name + " readded to team " + role.name)
            await member.add_roles(role)
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
                    if teamPop[team] > tMax:
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
    roleList = roleListByGuild[guild.id]

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
                conString = conString + str(idn) + str(assignedList[idn]) + "\n"
        conString = conString[0:-1]
    else:
        conString = 'Pickle Empty'
    return conString

@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))

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

    view = factionDecisionRequest(get(bot.guilds, id=guildIDs[1]), factions)
    bot.add_view(view)


@bot.event
async def on_message(message):
    if(not(message.content.startswith('!'))):
        return

    #if message.content.startswith('!!!TESTJOIN'):
    #    await on_member_join(message.author)

    gmRole = get(message.guild.roles, id=GMRoles[message.guild.id])
    if(not(gmRole in message.author.roles)):
        return
    print("** Command Initiated **")
    guild = message.guild

    if message.content.startswith('!toggleSpectator'):
        member = message.author
        print(member.name)

    if message.content.startswith('!getEligibleMembers'):
        memberList = await PCmembers(guild)
        for member in memberList:
            print(member.name + " : " + str(member.id))

    if message.content.startswith('!assignTeams'):
        await simpleAssignTeams(guild)

    if message.content.startswith('!clearAllTeams'):
        await simpleClearAllTeams(guild)

    if message.content.startswith('!printPickle'):
        print(await simpleGetMemberAssignments(guild))

    if message.content.startswith('!restoreRoles'):
        print("Starting restore...")
        await loadBackupList(guild)
        print("Roles restored.")

    if message.content.startswith("!reportUnassignedMembers"):
        unassignedList = await reportUnassignedMembers(guild)
        attachOut = ""
        for member in unassignedList:
            attachOut = attachOut + member.name + "\n"
        attachOut = attachOut[0:-1]
        fileOut = discord.File(io.StringIO(attachOut), filename="UnassignedList.txt", description="A list of members with no role.")
        await message.reply(content = "Here's a list of members with no role:", file=fileOut)

    if message.content.startswith("!fixPickle"):
        await recreatePickle(guild)

    print("** Command Finalized **")

@bot.event
async def on_member_join(member):
    print(member.name + " joined!")
    guild = member.guild
    if(not(await reassignMemberTeam(member, guild))):
        if(not(await isPickleEmpty(guild))):
            assignMemory = await pickleLoadMemberData(guild)
            if newMemberFlag in assignMemory and assignMemory[newMemberFlag]:
                await simpleAddSingleMemberToTeam(member, guild)


@bot.slash_command(name="backup_pickle")
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
        if(not(gmRole in interaction.user.roles)):
            await interaction.response.send_message("You do not have permission to use this command.", delete_after=10, ephemeral=True)
            return
        commandInd = int(self.custom_id)
        print(commandInd)

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


@bot.slash_command(name="command_message")
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

@bot.slash_command(name="clear_members_from_role")
async def clearRole(ctx: discord.ApplicationContext, role: Option(discord.Role, "The Role to Clear")):
    """Clear all members from a role"""
    guild = ctx.guild
    gmRole = get(guild.roles, id=GMRoles[guild.id])
    if(not(gmRole in ctx.interaction.user.roles)):
        await ctx.respond("You do not have permission to use this command.", ephemeral=True, delete_after=10)
        return

    print(role)
    await ctx.respond(role.mention + " is being cleared.")
    data = await pickleLoadMemberData(guild)

    if len(data) < 1:
        return None


    memberList = await PCmembers(guild)
    print("test")

    for member in memberList:
        if role in member.roles:
            await member.remove_roles(role)
            if member.id in data:
                if data[member.id] == role.id:
                    del data[member.id]
    
    print("test")
    await pickleWrite(data, guild)
    print(role.mention)
    await ctx.respond(role.mention + " has been cleared.", delete_after=10)
    print("test")

@bot.slash_command(name="report_team_stats")
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

factions = [
    "Arborec", "Argent", "Barony", "Cabal",
    "Empyrean", "Ghosts", "Hacan", "Jol-Nar", 
    "Keleres [Argent]", "Keleres [Mentak]", "Keleres [Xxcha]",
    "L1Z1X", "Mahact", "Mentak", "Muaat",
    "Naalu", "Naaz-Rokha", "Nekro", "Nomad",
    "Saar", "Sardakk", "Sol", "Titans",
    "Winnu", "Xxcha", "Yin", "Yssaril",
]

@bot.slash_command(name="map")
async def showMap(ctx: discord.ApplicationContext, mapstring: Option(str, "The Map String"), name: Option(str, "The Map's Name", required=False)):
    guild = ctx.guild

    await ctx.respond(content = "Generating Map", delete_after=30)

    mapImageFile = loadMap(mapstring, name)
    print(mapImageFile)
    if name:
        fn = name + ".png"
    else:
        fn = "Map.png"
    mapFile = discord.File(mapImageFile, filename=fn, description="A Twilight Imperium Map")

    await ctx.respond(content = "Here is your map:", file=mapFile)

@bot.slash_command(name="dropdowntest")
async def dropdownTest(ctx: discord.ApplicationContext):
    vw = factionDecisionRequest(ctx.guild, factions)
    await ctx.respond(content = "Here is your test:", view=vw)

@bot.slash_command(name="clearvotes")
async def clearVoteFile(ctx: discord.ApplicationContext):
    await clearVotes()
    await ctx.respond(content = "Vote savefile cleared.", delete_after=10)

async def genVoteResults(team="all"):
    votes = await getVotes()

    search = None
    if team in votes.keys():
        search=team

    message = ""
    for key in votes.keys():
        if not(search) or search == key:
            message = message + key + ":\n"
            for votekey in votes[key].keys():
                message = message + "\t" + votekey + " has " + str(votes[key][votekey]) + " votes.\n"
            message = message + "\n"

    message = message[:-1]
    return message

@bot.slash_command(name="getvotes")
async def getVotesDD(ctx: discord.ApplicationContext):
    message = await genVoteResults()

    await ctx.respond(content = message)

@bot.message_command(name="Close Faction Poll")
async def closeFacPoll(ctx, message: discord.Message):
    print("Test")
    if message.author.id == bot.user.id and len(message.components) == 2 and message.components[1].children[0].label == "Vote":
        view = discord.ui.View()
        team = message.channel.name
        print(team)
        out = await genVoteResults(team)
        await message.edit(content="The results of this vote:\n" + out, view=None)
    
    await ctx.respond(content="Command finished.", delete_after=5)

defaultUnitPool = {
    "Mech" : 0,
    "Infantry" : 0,
    "Fighter" : 0,
    "Space Dock" : 0,
    "PDS" : 0,
    "Carrier" : 0,
    "Destroyer" : 0,
    "Cruiser" : 0,
    "Dreadnought" : 0,
    "Flagship" : 0,
    "War Sun" : 0,
    "Control Token" : 0,
    "Command Token" : 0,
}

class System:
    def __init__(self, tileNum, pos, planets={}, anomalies=[], wormholes=[], frontier=False, hyperlane=False, homeSystem=False, adjacentTiles=[], containedThings={}):
        self.tileNum        = tileNum
        self.pos            = pos
        self.planets        = planets
        self.anomalies      = anomalies
        self.wormholes      = wormholes
        self.frontier       = frontier
        self.hyperlane      = hyperlane
        self.adjacentTiles  = adjacentTiles
        self.contains       = containedThings

    def add_adjacency(adjSystem):
        if adjSystem in adjacentTiles:
            return False
        else:
            adjacentTiles.append(adjSystem)
            return True

class Planet:
    def __init__(self, name, resources=0, influence=0, Ptype=["None",], techspec="", legendary=False, readied=False, attachments=[], containedThings={}):
        self.name           = name
        self.resources      = resources
        self.influence      = influence
        self.techspecs      = techspecs
        self.attachments    = attachments
        self.legendary      = legendary
        self.readied        = readied
        self.Ptype          = Ptype
        self.containedThings= containedThings
        self.system         = None

    def set_system(system):
        self.system = system

    def ready():
        readied = True

    def exhaust():
        readied = False

    def add_attachment(self, attachment):
        if "resources" in attachment:
            self.resources = self.resources + attachment["resources"]

        if "influence" in attachment:
            self.influence = self.influence + attachment["influence"]

        if "type" in attachment:
            if "None" in Ptype:
                return False
            for ntype in attachment["type"]:
                if not(ntype in Ptype):
                    Ptype.append(ntype)

        if "techspec" in attachment:
            if len(techspec < 1):
                techspec = attachment["techspec"]
            else:
                self.add_attachment(attachment["Alt"])

        if "legendary" in attachment:
            if not(legendary):
                legendary = attachment["legendary"]

        attachments.append(attachment["name"])
        return True

def Merge(listOfDict):
    outDict = {}
    for dic in listOfDict:
        outDict = outDict | dic

    return outDict

def systemInfoLookup(tileNumber):
    dFrame = DataSheet.parse(dataTabs[0])
    tileList = dFrame[dataTitles[dataTabs[0]][0]]
    index = -1
    sysInfoDict = {}
    for i in range(len(tileList)):
        if tileList[i] == tileNumber:
            index = i
    if index >= 0:
        for title in dFrame:
            item = dFrame[title][index]
            if item == item:
                sysInfoDict[title] = item
            else:
                sysInfoDict[title] = defaults[dataTabs[0]][title]

    return sysInfoDict

def planetInfoLookup(planetName):
    dFrame = DataSheet.parse(dataTabs[1])
    planetList = dFrame[dataTitles[dataTabs[1]][0]]
    index = -1
    pntInfoDict = {}
    for i in range(len(planetList)):
        if planetList[i] == planetName:
            index = i
    if index >= 0:
        for title in dFrame:
            item = dFrame[title][index]
            if item == item:
                pntInfoDict[title] = item
            else:
                pntInfoDict[title] = defaults[dataTabs[1]][title]

    return pntInfoDict

def planetsGen(planetString):
    PlanetList = {}
    if(planetString == planetString):
        planets = planetString.split(",")
        for pnt in planets:
            pInfo = planetInfoLookup(pnt)
            sheet = dataTitles[dataTabs[1]]
            pObj = Planet(pnt, pInfo[sheet[2]], pInfo[sheet[3]], pInfo[sheet[4]], pInfo[sheet[5]], pInfo[sheet[6]], pInfo[sheet[7]])
            PlanetList[pnt] = pObj

    return PlanetList

async def ringListToSystemMap(mapString):
    ringList = mapStringToTilePosSet(mapString)
    tileList = Merge(ringList)

    systemMap = {}

    for pos in tileList:
        sysInfo = systemInfoLookup(tileList[pos])
        if len(sysInfo)>0:
            sysLookup = dataTitles[dataTabs[0]]
            planets = planetsGen(sysInfo[sysLookup[1]])
            systemMap[pos] = System(tileList[pos], pos, planets, anomalies, wormholes, frontier, hyperlane, homeSystem)
        else:
            systemMap[pos] = System(tileList[pos], pos)

# robo dane stuff below
# -----------------------------------------------------------------------------------------------------------------------------------------------------
def check_user(user_roles, role_ids):
    user_role_ids = [(role.id) for role in user_roles]
    return len(list(set(user_role_ids) & set(role_ids))) > 0

def search(cardname, filename):
    search_string = cardname.lower()
    suggestions = []
    savedRow = {}
    matchFound = False
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12 = reader.fieldnames
        for row in reader:
            aliasList = list(row[c12].split(", "))
            orig_name_lower = row[c1].lower()
            genAlias = [orig_name_lower[i: i+len(search_string)] for i in range(len(orig_name_lower)-len(search_string)+1)]
            if orig_name_lower == search_string or search_string in aliasList:
                return row, True
            elif search_string in genAlias:
                if savedRow == {}:
                    savedRow =  row.copy()
                    suggestions.append(row[c1])
                    matchFound = True
                else:
                    suggestions.append(row[c1])
                    matchFound = False
            else:
                fuzzDist = fuzz.partial_ratio(search_string,orig_name_lower)
                if fuzzDist >= fuzzDistMin:
                    suggestions.append(row[c1])
                #levDist = distance(search_string,orig_name_lower)
                #if levDist <= levDistMin:
                #    suggestions.append(row[c1])
    if matchFound == True:
        return savedRow, True
    else:
        return suggestions, False

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@slash.slash(
    name="ability",
    guild_ids=guild_ids,
    description="Searches faction abilities by name. Example usage: /ability assimilate /ability entanglement",
    options=[manage_commands.create_option(
        name="ability",
        description="Ability Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpAbility(ctx, ability="None", keep=0):
    cardinfo, match = search(ability, 'abilities.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        separator = "\n"
        embed = discord.Embed(title = cardinfo["Name"], description= cardinfo["Type"] + " Faction Ability", color=botColor)
        embed.add_field(name = "Ability Text", value = separator.join(cardrules), inline = False)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + ability + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="actioncard",
    guild_ids=guild_ids,
    description="Searches action cards by name. Example usage: /actioncard sabotage /actioncard rise",
    options=[manage_commands.create_option(
        name="actioncard",
        description="Action Card Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpActionCard(ctx, actioncard="None", keep=0):
    cardinfo, match = search(actioncard,'actioncards.csv')
    if match:
        cardlore = cardinfo["Flavour Text"].split("|")
        separator = "\n"
        embed=discord.Embed(title = cardinfo["Name"], description= "**" + cardinfo["Type"] + ":**\n" + cardinfo["Rules Text"], color=botColor)
        embed.add_field(name = "*Flavour Text*", value = "*" + separator.join(cardlore) + "*", inline = False)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        embed.add_field(name = "Quantity", value = cardinfo["Quantity"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + actioncard + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="ac",
    guild_ids=guild_ids,
    description="Searches action cards by name. Example usage: /ac sabotage /ac rise",
    options=[manage_commands.create_option(
        name="ac",
        description="Action Card Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def ac(ctx, ac="None", keep=0):
    await lookUpActionCard.invoke(ctx, ac, keep)

@slash.slash(
    name="agenda",
    guild_ids=guild_ids,
    description="Searches agenda cards by name. Example usage: /agenda mutiny /agenda ixthian",
    options=[manage_commands.create_option(
        name="agenda",
        description="Agenda Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpAgenda(ctx, agenda="None", keep=0):
    cardinfo, match = search(agenda,'agendas.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        separator = "\n"
        embed=discord.Embed(title = cardinfo["Name"], description= "**" + cardinfo["Type"] + ":**\n\n" + separator.join(cardrules), color=botColor)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + agenda + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="exploration",
    guild_ids=guild_ids,
    description="Searches exploration cards by name. Example usage: /exploration freelancers /exploration fabricators",
    options=[manage_commands.create_option(
        name="explorationcard",
        description="Exploration Card Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpExplore(ctx, explorationcard="None", keep=0):
    cardinfo, match = search(explorationcard,'exploration.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        cardlore = cardinfo["Flavour Text"].split("|")
        separator = "\n"
        embed=discord.Embed(title = cardinfo["Name"], description= "*" + cardinfo["Type"] + " Exploration Card*\n\n" + separator.join(cardrules), color=botColor)
        if cardinfo["Flavour Text"] != "":
            embed.add_field(name = "*Flavour Text*", value = "*" + separator.join(cardlore) + "*", inline = False)
        embed.add_field(name = "Quantity", value = cardinfo["Quantity"], inline = True)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + explorationcard + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="exp",
    guild_ids=guild_ids,
    description="Searches exploration cards by name. Example usage: /exp freelancers /exp fabricators",
    options=[manage_commands.create_option(
        name="explorationcard",
        description="Exploration Card Name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def exp(ctx, explorationcard="None", keep=0):
    await lookUpExplore.invoke(ctx, explorationcard, keep)

@slash.slash(
    name="leader",
    guild_ids=guild_ids,
    description="Searches leaders by name or faction. Example usage: /leader ta zern /leader nekro agent",
    options=[manage_commands.create_option(
        name="leader",
        description="Leader Name/Faction name and leader type",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpLeader(ctx, leader="None", keep=0):
    cardinfo, match = search(leader,'leaders.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        cardlore = cardinfo["Flavour Text"].split("|")
        separator = "\n"
        embed=discord.Embed(title = "__**" + cardinfo["Name"] + "**__", description= "***" + cardinfo["Type"] + " " + cardinfo["Classification"] + "***\n" + cardinfo["Subtitle"] + "\n" + separator.join(cardrules), color=botColor)
        embed.add_field(name = "*Flavour Text*", value = "*" + separator.join(cardlore) + "*", inline = False)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + leader + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="objective",
    guild_ids=guild_ids,
    description="Searches public and secret objectives. Example usage: /objective become a legend /objective monument",
    options=[manage_commands.create_option(
        name="objective",
        description="Objective name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpObjective(ctx, objective="None", keep=0):
    cardinfo, match = search(objective,'objectives.csv')
    if match:
        embed=discord.Embed(title = cardinfo["Name"], description= "*" + cardinfo["Type"] + " Objective - " + cardinfo["Classification"] + " Phase*\n\n" + cardinfo["Rules Text"], color=botColor)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + objective + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="obj",
    guild_ids=guild_ids,
    description="Searches public and secret objectives. Example usage: /obj become a legend /obj monument",
    options=[manage_commands.create_option(
        name="objective",
        description="Objective name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def obj(ctx, objective="None", keep=0):
    await lookUpObjective.invoke(ctx, objective, keep)

@slash.slash(
    name="planet",
    guild_ids=guild_ids,
    description="Searches planet cards. Example usage: /planet bereg /planet elysium",
    options=[manage_commands.create_option(
        name="planet",
        description="Planet name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpPlanet(ctx, planet="None", keep=0):
    cardinfo, match = search(planet,'planets.csv')
    if match:
        techSkip = "\n" + cardinfo["Classification"] + " Technology Specialty" if cardinfo["Classification"] else ""
        embed=discord.Embed(title = cardinfo["Name"], description= cardinfo["Type"] + " - " + cardinfo["Res_Inf"] + " " + techSkip, color=botColor)
        embed.add_field(name = "*Flavour Text*", value = "*" + cardinfo["Flavour Text"] + "*", inline = False)
        if cardinfo["Rules Text"] != "":
            legend = cardinfo["Rules Text"].split("|")
            embed.add_field(name = "Legendary Ability", value = "\n".join(legend), inline = False)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + planet + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="promissory",
    guild_ids=guild_ids,
    description="Searches generic and faction promissories. Example usage: /promissory spy net /promissory ceasefire",
    options=[manage_commands.create_option(
        name="promissorynote",
        description="Promissory note",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpProm(ctx, promissorynote="None", keep=0):
    cardinfo, match = search(promissorynote,'promissories.csv')
    if match:
        separator = "\n"
        rulesText = cardinfo["Rules Text"].split("|")
        embed=discord.Embed(title = cardinfo["Name"], description = "*" + cardinfo["Type"] + " Promissory Note*\n\n" + separator.join(rulesText), color=botColor)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + promissorynote + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="prom",
    guild_ids=guild_ids,
    description="Searches generic and faction promissories. Example usage: /prom spy net /prom ceasefire",
    options=[manage_commands.create_option(
        name="promissorynote",
        description="Promissory note",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def prom(ctx, promissorynote="None", keep=0):
    await lookUpProm.invoke(ctx, promissorynote, keep)

@slash.slash(
    name="relic",
    guild_ids=guild_ids,
    description="Searches relics for the name or partial match. Example usage: /relic the obsidian /relic emphidia",
    options=[manage_commands.create_option(
        name="relic",
        description="Relic name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpRelic(ctx, relic="None", keep=0):
    cardinfo, match = search(relic,'relics.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        separator = "\n"
        embed=discord.Embed(title = cardinfo["Name"], description = separator.join(cardrules), color=botColor)
        embed.add_field(name = "*Flavour Text*", value = "*" + cardinfo["Flavour Text"] + "*", inline = False)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + relic + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="tech",
    guild_ids=guild_ids,
    description="Searches generic and faction technologies. Example usage: /tech dreadnought 2 /tech magen",
    options=[manage_commands.create_option(
        name="technology",
        description="Technology name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpTech(ctx, technology="None", keep=0):
    cardinfo, match = search(technology,'techs.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        separator = "\n"
        prereqs = ", Requires - " + cardinfo["Prerequisites"] if cardinfo["Prerequisites"] else ""
        embed=discord.Embed(title = cardinfo["Name"], description = "*" + cardinfo["Type"] + " Technology" + prereqs + "*\n\n" + separator.join(cardrules), color=botColor)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + technology + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="unit",
    guild_ids=guild_ids,
    description="Searches generic and faction units. Example usage: /unit strike wing alpha /unit saturn engine",
    options=[manage_commands.create_option(
        name="unit",
        description="Unit name",
        option_type=3,
        required=True
    ),
    manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def lookUpUnit(ctx, unit="None", keep=0):
    cardinfo, match = search(unit,'units.csv')
    if match:
        cardrules = cardinfo["Rules Text"].split("|")
        separator = "\n"
        prereqs = "\nUpgrade requires " + cardinfo["Prerequisites"] if cardinfo["Prerequisites"] else ""
        embed=discord.Embed(title = cardinfo["Name"], description = "*" + cardinfo["Type"] + " - " + cardinfo["Classification"] + "*\n\n" + separator.join(cardrules) + prereqs, color=botColor)
        embed.add_field(name = "Source", value = cardinfo["Source"], inline = True)
        if cardinfo["Notes"] != "":
            embed.add_field(name = "Notes", value = cardinfo["Notes"], inline = False)
    else:
        if cardinfo == []:
            embed = discord.Embed(title = "No matches found.", description = "No results for \"" + unit + "\" were found. Please try another search.")
        else:
            embed = discord.Embed(title = "No matches found.", description = "Suggested searches: " + ", ".join(cardinfo))
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="l1hero",
    guild_ids=guild_ids,
    description="Returns information about using the L1Z1X hero. Example usage: /l1hero",
    options=[manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def l1hero(ctx, keep=0):
    embed=discord.Embed(title = "L1Z1X Hero - Dark Space Navigation", description = "This is a \"teleport\". The move value of your dreads/flagship is irrelevant.\nYou must legally be able to move into the chosen system, so no supernovas and no asteroid fields without Antimass Deflectors.\nYou can move dreads & flagship out of systems containing your command tokens.\nThey can transport units from their origin system.", color=botColor)
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="titanstiming",
    guild_ids=guild_ids,
    description="Returns information about timing windows for the titans abilities. Example usage: /titanstiming",
    options=[manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def titanstiming(ctx, keep=0):
    embed=discord.Embed(title = "Titans Timing Windows - Terragenesis, Awaken, Ouranos, and Hecatonchires", description = "Activating a system\nis not the same as\nActivating a system that contains X\n\nIf you activate a system that has sleeper tokens on all the planets, no PDS but does have a unit on at least one planet, the first thing you do is use Scanlink Drone Network (SDN).\nAfter exploring you cannot add an additional sleeper token since all sleepers are still present and have not been replaced or moved yet.\nYou can trigger AWAKEN to turn sleeper tokens into PDS, however you cannot use those PDS to DEPLOY their flagship, since you did not \"activate a system that contains 1 or more of your PDS.\"\nLikewise, you cannot activate a system that contains no sleeper tokens, explore using SDN, add a sleeper token and then AWAKEN it since you did not \"activate a system that contains 1 or more of your sleeper tokens.\"\nEven if you had a multi-planet system where one planet has a sleeper token and the explored planet doesn't, AWAKEN specifies \"those tokens\", referring to the tokens present at the time of activation as being able to be replaced.\nIn order to use the mech's Deploy ability, you must have a PDS unit in your reinforcements.", color=botColor)
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

@slash.slash(
    name="sardakkcommander",
    guild_ids=guild_ids,
    description="Returns information about using the Sardakk N\'orr commander. Example usage: /sardakkcommander",
    options=[manage_commands.create_option(
        name="keep",
        description="Keep output (1 for keep, 0 for delete), only moderators can keep",
        option_type=4,
        required=False
    )])
async def sardakkcommander(ctx, keep=0):
    embed=discord.Embed(title = "Sardakk Commander - G\'hom Sek\'kus", description = "The Sardakk N\'orr commander/alliance does not care about:\n1) The space area of the active system\n2) The space area of the systems containing planets being committed from\n3) Whether the planets being committed to are friendly, enemy, or uncontrolled.\n\nThe Sardakk Norr commander/alliance does care about:\n1) Being the active player\n2) Effects that prevent movement, including being a structure and ground force, Ceasefire and Enforced Travel Ban. Committing is moving.\n3) Anomaly movement rules\n4) Effects that end your turn, such as Nullification Field or Minister of Peace\n5) Parley. Your ground forces will be removed if you have no capacity in the space area of the active system.\n6) The DMZ (Demilitarized Zone Planet Attachment)\n7) Your command tokens in the systems containing the planets being committed from", color=botColor)
    newMessage = await ctx.send(embed=embed)
    if (delete_response and (keep == 0 or (keep == 1 and not check_user(ctx.author.roles, power_user_roles)))):
        await newMessage.delete(delay = time_to_delete_response)

async def changepage(ctx, pageincrement):
    # Title string
    titlestring = "RoboDane Help Page "

    # Strings that will be used for help page descriptions
    help_pages = ["**/ability <arg>**\nSearches faction abilities by name.\nExample usage: /ability assimilate /ability entanglement\n\n/**actioncard <arg>** or **/ac <arg>**\nSearches action cards by name.\nExample usage: /actioncard sabotage /actioncard rise\n/ac sabotage /ac rise\n\n**/agenda <arg>**\nSearches agenda cards by name.\nExample usage: /agenda mutiny /agenda ixthian\n\n**/exploration <arg>** or **/exp <arg>**\nSearches exploration cards by name.\nExample usage: /exploration freelancers /exploration fabricators\n/exp freelancers /exp fabricators\n\n**/leaders <arg>**\nSearches leaders by name or faction.\nExample usage: /leader ta zern /leader nekro agent","**/objective <arg>** or **/obj <arg>**\nSearches public and secret objectives.\nExample usage: /objective become a legend /objective monument\n/obj become a legend /obj monument\n\n**/planet <arg>**\nSearches planet cards.\nExample usage: /planet bereg /planet elysium\n\n**/promissory <arg>** or **/prom <arg>**\nSearches generic and faction promissories.\nExample usage: /promissory spy net /promissory ceasefire\n/prom spy net /prom ceasefire\n\n**/relic <arg>**\nSearches relics for the name or partial match.\nExample usage: /relic the obsidian /relic emphidia\n\n**/tech <arg>**\nSearches generic and faction technologies.\nExample usage: /tech dreadnought 2 /tech magen","**/unit <arg>**\nSearches generic and faction units.\nExample usage: /unit strike wing alpha /unit saturn engine\n\n**/l1hero**\nReturns information about using the L1Z1X hero.\nExample usage: /l1hero\n\n**/titanstiming**\nReturns information about timing windows for the titans abilities.\nExample usage: /titanstiming\n\n**/sardakkcommander**\nReturns information about using the Sardakk N\'orr commander.\nExample usage: /sardakkcommander\n\n**/help**\nReturns information about using RoboDane.\nExample usage: /help"]

    # Scraping the current embed to get old page number
    oldembed = ctx.origin_message.embeds[0]
    oldtitle = oldembed.title

    # Determining the current page number
    numtext = oldtitle[19:].split('/')
    currentpage = int(numtext[0])
    oldtotalpage = int(numtext[1])

    # Check that currentpage + pageincrement is [1,len(help_pages)]
    if (currentpage + pageincrement) < 1 or (currentpage + pageincrement) > len(help_pages):
        return

    # Create new embed with next page contents and buttons corresponding to page number
    new_page = currentpage + pageincrement
    embed = discord.Embed(title = "RoboDane Help Page " + str(new_page) + "/" + str(len(help_pages)), description = help_pages[new_page-1])
    buttons = []
    if new_page == 1:
        buttons = [
            manage_components.create_button(style=ButtonStyle.blurple, label="Next Page ->", custom_id="buttonforward"),
        ]
    elif new_page == len(help_pages):
        buttons = [
            manage_components.create_button(style=ButtonStyle.blurple, label="<- Previous Page", custom_id="buttonbackward"),
        ]
    else:
        buttons = [
            manage_components.create_button(style=ButtonStyle.blurple, label="<- Previous Page", custom_id="buttonbackward"),
            manage_components.create_button(style=ButtonStyle.blurple, label="Next Page ->", custom_id="buttonforward"),
        ]
    action_row = manage_components.create_actionrow(*buttons)

    #Editing the message
    await ctx.edit_origin(embed=embed, components=[action_row])

# Help forward button
@slash.component_callback()
async def buttonforward(ctx):
    await changepage(ctx, 1)

# Help backward button
@slash.component_callback()
async def buttonbackward(ctx):
    await changepage(ctx, -1)

@slash.slash(
    name="help",
    guild_ids=guild_ids,
    description="Returns information about using RoboDane. Example usage: /help",
)
async def helprobodane(ctx):
    embed=discord.Embed(title = "RoboDane Help Page 1/3", description = "**/ability <arg>**\nSearches faction abilities by name.\nExample usage: /ability assimilate /ability entanglement\n\n/**actioncard <arg>** or **/ac <arg>**\nSearches action cards by name.\nExample usage: /actioncard sabotage /actioncard rise\n/ac sabotage /ac rise\n\n**/agenda <arg>**\nSearches agenda cards by name.\nExample usage: /agenda mutiny /agenda ixthian\n\n**/exploration <arg>** or **/exp <arg>**\nSearches exploration cards by name.\nExample usage: /exploration freelancers /exploration fabricators\n/exp freelancers /exp fabricators\n\n**/leaders <arg>**\nSearches leaders by name or faction.\nExample usage: /leader ta zern /leader nekro agent", color=botColor)
    #embed2=discord.Embed(title = "RoboDane Help Page 2/3", description = "**/objective <arg>** or **/obj <arg>**\nSearches public and secret objectives.\nExample usage: /objective become a legend /objective monument\n/obj become a legend /obj monument\n\n**/planet <arg>**\nSearches planet cards.\nExample usage: /planet bereg /planet elysium\n\n**/promissory <arg>** or **/prom <arg>**\nSearches generic and faction promissories.\nExample usage: /promissory spy net /promissory ceasefire\n/prom spy net /prom ceasefire\n\n**/relic <arg>**\nSearches relics for the name or partial match.\nExample usage: /relic the obsidian /relic emphidia\n\n**/tech <arg>**\nSearches generic and faction technologies.\nExample usage: /tech dreadnought 2 /tech magen", color=botColor)
    #embed3=discord.Embed(title = "RoboDane Help Page 3/3", description = "**/unit <arg>**\nSearches generic and faction units.\nExample usage: /unit strike wing alpha /unit saturn engine\n\n**/l1hero**\nReturns information about using the L1Z1X hero.\nExample usage: /l1hero\n\n**/titanstiming**\nReturns information about timing windows for the titans abilities.\nExample usage: /titanstiming\n\n**/sardakkcommander**\nReturns information about using the Sardakk N\'orr commander.\nExample usage: /sardakkcommander\n\n**/help**\nReturns information about using RoboDane.\nExample usage: /help", color=botColor)
    buttons = [
        manage_components.create_button(style=ButtonStyle.blurple, label="Next Page ->", custom_id="buttonforward"),
    ]
    action_row = manage_components.create_actionrow(*buttons)
    await ctx.send(embed=embed, components=[action_row])

#--------------------------------------------------------------------------------------------------------------------------------------------------
# robo dane stuff above

DataSheet = pandas.ExcelFile(dataFile)
bot.run(os.getenv("DISCORD_TOKEN"))