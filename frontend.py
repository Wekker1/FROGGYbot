import typing
import discord
from discord.utils import get
import re
import pickle
import os
import io
from os.path import exists

fullFactions = {
	"Arborec" : "The Arborec", 
	"Argent" : "The Argent Flight", 
	"Barony" : "The Barony of Letnev", 
	"Cabal" : "The Vuil'raith Cabal",
    "Empyrean" : "The Empyrean", 
    "Ghosts" : "The Ghosts of Creuss", 
    "Hacan" : "The Emirates of Hacan", 
    "Jol-Nar" : "The Universities of Jol-Nar", 
    "Keleres [Argent]" : "The Council Keleres", 
    "Keleres [Mentak]" : "The Council Keleres", 
    "Keleres [Xxcha]" : "The Council Keleres",
    "L1Z1X" : "The L1Z1X Mindnet", 
    "Mahact" : "The Mahact Gene-Sorcerers", 
    "Mentak" : "The Mentak Coalition", 
    "Muaat" : "The Embers of Muaat",
    "Naalu" : "The Naalu Collective", 
    "Naaz-Rokha" : "The Naaz-Rokha Alliance", 
    "Nekro" : "The Nekro Virus", 
    "Nomad" : "The Nomad",
    "Saar" : "The Clan of Saar", 
    "Sardakk" : "Sardakk N'orr", 
    "Sol" : "The Federation of Sol", 
    "Titans" : "The Titans of Ul",
    "Winnu" : "The Winnu", 
    "Xxcha" : "The Kingdom of Xxcha", 
    "Yin" : "The Yin Brotherhood", 
    "Yssaril" : "The Yssaril Tribes",
}

votesPickle = 'votes.pickle'

class memPoll():
	def __init__(self, pollID, public):
		self.pollID = pollID
		self.public = public

class memVote():
	def __init__(self, pollID, member, vote):
		self.pollID = pollID
		self.member = member
		self.vote = vote


async def isVotePickleEmpty():
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			if len(pickle.load(f)) > 0:
				return False
	return True

async def clearVotes(clearList={"POLLS": {}, "VOTES": []}):
	pickleFile = votesPickle

	with open(pickleFile, 'wb') as f:
		pickle.dump(clearList, f, pickle.HIGHEST_PROTOCOL)


async def registerPoll(memPoll):
	data={}
	pickleFile = votesPickle
	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)

	pollList = data["POLLS"]
	if memPoll.pollID in pollList.keys():
		return -1
	else:
		pollList[memPoll.pollID] = memPoll

	data["POLLS"] = pollList

	with open(pickleFile, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

	return 1

async def unregisterPoll(pollID):
	data={}
	pickleFile = votesPickle
	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)

	pollList = data["POLLS"]
	if pollID in pollList.keys():
		del pollList[pollID]

	data["POLLS"] = pollList

	with open(pickleFile, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

async def updateVote(memVoteObj):
	data={}
	votes = []
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)

	votes = data["VOTES"]
	changedVote = False
	for v in votes:
		if v.pollID == memVoteObj.pollID and v.member == memVoteObj.member:
			v.vote = memVoteObj.vote
			changedVote = True

	if not(changedVote):
		votes.append(memVoteObj)

	count = 0
	voteCounts = {}
	for vote in votes:
		if vote.pollID == memVoteObj.pollID:
			count = count+1
			if vote.vote in voteCounts:
				voteCounts[vote.vote] = voteCounts[vote.vote] + 1
			else:
				voteCounts[vote.vote] = 1

	data["VOTES"] = votes
	with open(pickleFile, 'wb') as f:
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

	return count

async def getVotes():
	data = {}
	votes = []
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)

	votes = data["VOTES"]
	voteTotals = {}
	for vote in votes:
		if vote.pollID in voteTotals.keys():
			if vote.vote in voteTotals[vote.pollID].keys():
				voteTotals[vote.pollID][vote.vote] = voteTotals[vote.pollID][vote.vote]+1
			else:
				voteTotals[vote.pollID][vote.vote] = 1
		else:
			voteTotals[vote.pollID] = {vote.vote : 1}

	return voteTotals

async def genVoteResults(pollID=None):
    votes = await getVotes()

    message = ""
    for key in votes.keys():
        if not(pollID) or pollID == key:
            for votekey in votes[key].keys():
                message = message + "o " + str(votekey) + " has " + str(votes[key][votekey]) + " votes.\n"
            message = message + "\n"

    message = message[:-1]
    return message

async def getMessageFromPollID(guild, pollID):
	channels = guild.text_channels
	for ch in channels:
		try:
			message = await ch.fetch_message(pollID)
			return message
		except:
			y = 0


async def genPollReport(guild, verbose=False):
	pickleFile = votesPickle
	data = {}
	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)

	out = ""

	polls = data["POLLS"]
	for pollID in polls:
		message = await getMessageFromPollID(guild, pollID)
		title = message.content.split("\n")[0]
		out = out + title + " in channel: " + message.channel.name + "\n"
		if verbose:
			votes = await genVoteResults(pollID)
			out = out + votes + "\n"

	out = out[:-1]
	return out

async def clearPollVotes(pollID):
	pickleFile = votesPickle
	data = {}
	votes = []

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)
	votes = data["VOTES"]

	for mv in votes:
		if mv.pollID == pollID:
			votes.remove(mv)

	data["VOTES"] = votes

	await unregisterPoll(pollID)

	await clearVotes(data)

async def checkPollPublic(messageID):
	pickleFile = votesPickle
	data = {}

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			data = pickle.load(f)
	
	polls = data["POLLS"]
	if messageID in polls:
		poll = polls[messageID]
	else:
		return False
	if poll:
		return poll.public
	else:
		return False

memVarDefault = {-1 : "MEMVARDEFAULT"}
memVar = memVarDefault.copy()

class factionDropdown(discord.ui.Select):
	def __init__(self, placeholder, options):
		super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, custom_id="pollID")

	async def callback(self, interaction: discord.Interaction):
		memVar[interaction.user.id] = self.values[0]
		await interaction.response.defer()

class confirmButton(discord.ui.Button):
	def __init__(self, commandName, dropdown):
		self.dropdown = dropdown
		super().__init__(label=commandName, style=discord.enums.ButtonStyle.primary, custom_id=commandName)

	async def callback(self, interaction: discord.Interaction):
		pollID = interaction.message.id
		uid = interaction.user.id
		if memVar == memVarDefault or not(uid in memVar.keys()):
			await interaction.response.send_message(content=f"You must select an option.", delete_after=10, ephemeral=True)
		else:
			if memVar[uid] != self.dropdown.values[0]:
				await interaction.response.send_message(content=f"Error processing vote, please select your option in the dropdown again.", delete_after=30, ephemeral=True)
			else:
				newVote = memVote(pollID, interaction.user.id, memVar[uid])
				print(interaction.user.name + " " + newVote.vote)
				totalVoteCount = await updateVote(newVote)
				if await checkPollPublic(interaction.message.id):
					totalVoteCount = await genVoteResults(pollID) + "\n" + str(totalVoteCount)
				await interaction.message.edit(content=interaction.message.content.split("\n")[0] + f"\n\n{totalVoteCount} users have voted.")
				await interaction.response.send_message(content=f"You have voted/updated your vote to: {memVar[uid]}", delete_after=10, ephemeral=True)

def factionDecisionRequest(guild, factionOptions):
	dropOptions = []

	keleresFlag = False
	for faction in factionOptions:
		shortName = re.sub(r"[-']", "", faction)
		longName = ""
		emoji = ""
		if faction.startswith("Keleres"):
			if not(keleresFlag):
				shortName = "Keleres"
				longName = fullFactions[faction]
				emoji = get(guild.emojis, name=shortName)
				dropOptions.append(discord.SelectOption(label=shortName, description=longName, emoji=emoji))
				keleresFlag = True
		else:
			longName = fullFactions[faction]
			emoji = get(guild.emojis, name=shortName)
			dropOptions.append(discord.SelectOption(label=shortName, description=longName, emoji=emoji))

	vw = discord.ui.View(timeout=None)
	sel = factionDropdown(placeholder="Faction Name", options = dropOptions)
	but = confirmButton("Vote", sel)
	vw.add_item(sel)
	vw.add_item(but)
	return vw

def decisionRequest(optionList):
	dropOptions = []
	for option in optionList:
		dropOptions.append(discord.SelectOption(label=option))
	vw = discord.ui.View(timeout=None)
	sel = factionDropdown(placeholder="Choose one option:", options = dropOptions)
	but = confirmButton("Vote", sel)
	vw.add_item(sel)
	vw.add_item(but)
	return vw