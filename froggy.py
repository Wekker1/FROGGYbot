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
976947018612224020,
976947145464741909,
976947358736740412,
976947273223258122,
976947530485092362,
976947665453580298]
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

DataSheet = pandas.ExcelFile(dataFile)
bot.run(os.getenv("DISCORD_TOKEN"))