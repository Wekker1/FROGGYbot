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

backUps = {
856341009218666506 : 'testAss.pickle',
847560709730730064 : 'restoreList.txt',
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

async def assignRandomTeams(memberList, guild):
    teamList = roleListByGuild[guild.id]
    selector = await generateSelectorList(len(teamList))
    assignMemory = await pickleLoadMemberData(guild)

    if len(assignMemory) < 1:
        return None

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
            del selector[it]

            assignment = teamList[ind]

            assignMemory[member.id] = assignment
            role = get(member.guild.roles, id=assignment)
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
    # Make sure to set the guild ID here to whatever server you want the buttons in!
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
        await ctx.respond("You do not have permission to use this command.", delete_after=10)
        return

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


bot.run(os.getenv("DISCORD_TOKEN"))

factions = [
    "Arborec", "Argent", "Barony", "Cabal",
    "Empyrean", "Ghosts", "Hacan", "Jol-Nar",
    "L1Z1X", "Mahact", "Mentak", "Muaat",
    "Naalu", "Naaz Rokha", "Nekro", "Nomad",
    "Saar", "Sardakk", "Sol", "Titans",
    "Winnu", "Xxcha", "Yin", "Yssaril",
]

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
    def __init__(self, tileNum, planets=[], anomalies=[], wormholes=[], frontier=False, hyperlane=False, homeSystem=False, adjacentTiles=[], containedThings={}):
        self.tileNum        = tileNum
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
    def __init__(self, name, resources=0, influence=0, Ptype=["None",], techspec="", attachments=[], legendary=False, readied=False, containedThings={}):
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

galaxy = {}

async def generateMap(mapString):
    if len(mapString) > 1:
        splmap = mapString.split(',')
        if len(splmap) < 2:
            splmap = mapString.split(',')
        if len(splmap) < 2:
            return {18 : System(18, Planet("Mecatol Rex", 1, 6))}
    else:
        return None