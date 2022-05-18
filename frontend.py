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

	with open(pickleFile, 'wb') as f:
		pickle.dump(votes, f, pickle.HIGHEST_PROTOCOL)

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

memVarDefaut = "test"

class factionDropdown(discord.ui.Select):
	memVar = memVarDefaut

	def __init__(self, placeholder, options):
		super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, custom_id=placeholder)

	async def callback(self, interaction: discord.Interaction):
		self.memVar = self.values[0]
		await interaction.response.defer()

class confirmButton(discord.ui.Button):
	def __init__(self, commandName, dropdown):
		self.dropdown = dropdown
		super().__init__(label=commandName, style=discord.enums.ButtonStyle.primary, custom_id=commandName)

	async def callback(self, interaction: discord.Interaction):
		print(self.dropdown.memVar)
		print(str(interaction.user))
		if self.dropdown.memVar == memVarDefaut:
			await interaction.response.send_message(content=f"You must select an option.", delete_after=10, ephemeral=True)
		else:
			team = "None"
			for role in interaction.user.roles:
				if role.name.startswith("Team"):
					team = role.name
			newVote = memVote(interaction.user.id, interaction.channel.name, self.dropdown.memVar)
			await updateVote(newVote)
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