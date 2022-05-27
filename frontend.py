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

class memVote():
	def __init__(self, member, team, vote):
		self.member = member
		self.team = team
		self.vote = vote

async def isVotePickleEmpty():
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			if len(pickle.load(f)) > 0:
				return False
	return True

async def clearVotes(clearList=[]):
	pickleFile = votesPickle

	with open(pickleFile, 'wb') as f:
		pickle.dump(clearList, f, pickle.HIGHEST_PROTOCOL)


async def updateVote(memVote):
	votes = []
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			votes = pickle.load(f)

	ldVote = get(votes, member=memVote.member)
	if(ldVote):
		votes[votes.index(ldVote)] = memVote
	else:
		votes.append(memVote)

	count = 0
	for vote in votes:
		if vote.team == memVote.team:
			count = count+1

	with open(pickleFile, 'wb') as f:
		pickle.dump(votes, f, pickle.HIGHEST_PROTOCOL)

	return count

async def getVotes():
	votes = []
	pickleFile = votesPickle

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			votes = pickle.load(f)

	voteTotals = {}
	for vote in votes:
		if vote.team in voteTotals.keys():
			if vote.vote in voteTotals[vote.team].keys():
				voteTotals[vote.team][vote.vote] = voteTotals[vote.team][vote.vote]+1
			else:
				voteTotals[vote.team][vote.vote] = 1
		else:
			voteTotals[vote.team] = {vote.vote : 1}

	return voteTotals

async def clearTeamVotes(team):
	pickleFile = votesPickle
	votes = []

	if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
		with open(pickleFile, 'rb') as f:
			votes = pickle.load(f)

	for mv in votes:
		if mv.team == team:
			votes.remove(mv)

	await clearVotes(votes)

memVarDefault = {-1 : "MEMVARDEFAULT"}
memVar = memVarDefault

class factionDropdown(discord.ui.Select):
	def __init__(self, placeholder, options):
		super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, custom_id="pollID")

	async def callback(self, interaction: discord.Interaction):
		self.memVar[interaction.user.id] = self.values[0]
		await interaction.response.defer()

class confirmButton(discord.ui.Button):
	def __init__(self, commandName, dropdown):
		self.dropdown = dropdown
		super().__init__(label=commandName, style=discord.enums.ButtonStyle.primary, custom_id=commandName)

	async def callback(self, interaction: discord.Interaction):
		print(self.dropdown.memVar)
		print(str(interaction.user))
		uid = interaction.user.id
		if self.dropdown.memVar == memVarDefault or not(uid in self.dropdown.memVar.keys()):
			await interaction.response.send_message(content=f"You must select an option.", delete_after=10, ephemeral=True)
		else:
			if memVar[uid] != dropdown.values[0]:
				await interaction.response.send_message(content=f"Error processing vote, please select your option in the dropdown again.", delete_after=30, ephemeral=True)
			else:
				newVote = memVote(interaction.user.id, interaction.channel.name, self.dropdown.memVar)
				totalVoteCount = await updateVote(newVote)
				await interaction.message.edit(content=interaction.message.content.split("\n")[0] + f"\n\n{totalVoteCount} users have voted.")
				await interaction.response.send_message(content=f"You have voted/updated your vote to: {self.dropdown.memVar}", delete_after=10, ephemeral=True)

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