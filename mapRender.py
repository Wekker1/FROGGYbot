import cv2
import pickle
import random
import os
import re
import io
import math
import numpy as np
from numpy import array
from os.path import exists
from dotenv import load_dotenv
from math import sqrt,cos,sin,radians
import dataLookup
from dataLookup import *
import asyncio

assetAddress = "assets/"
subAddresses = {
	"unit" : "units/smUnit/",
	"tiles": "systems/clean/tiles/",
	"attachments" : "tokens/",
		"space" : "space/",
		"planet": "planet/",
	"tokens" : "tokens/"
}

saveAddress = "saves/"

baseTileSize = (260,300)
a1step = (-1, 0)
a2step = (0.5, sqrt(3)/2)
a3step = (0.5, -sqrt(3)/2)

unitsAddresses = {
	"i" : "infantry.png",
	"m" : "mech.png",
	"f" : "fighter.png",
	"p" : "PDS.png",
	"s" : "spacedock.png",
	"d" : "destroyer.png",
	"c" : "cruiser.png",
	"C" : "carrier.png",
	"D" : "dreadnought.png",
	"w" : "WarSun.png",
	"F" : "flagship.png",
}

tileType = {
	 '1' : 1,	 '2' : 1,	 '3' : 1,	 '4' : 1,	 '5' : 1,	 '6' : 1,	 '7' : 1,	 '8' : 1,	 '9' : 2,	'10' : 2,
	'11' : 2,	'12' : 2,	'13' : 2,	'14' : 2,	'15' : 2,	'16' : 3,	'17' : 0,	'18' : -1,	'19' : 1,	'20' : 1,	
	'21' : 1,	'22' : 1,	'23' : 1,	'24' : 1,	'25' : 2,	'26' : 2,	'27' : 2,	'28' : 2,	'29' : 2,	'30' : 2,	
	'31' : 2,	'32' : 2,	'33' : 2,	'34' : 2,	'35' : 2,	'36' : 2,	'37' : 2,	'38' : 2,	'39' : 0,	'39m': 2,
	'40' : 0,	'40m': 2,	'41' : 0,	'42' : 0,	'43' : 0,	'44' : 0,	'45' : 0,	'46' : 0,	'47' : 0,	'48' : 0,	
	'49' : 0,	'50' : 0,	'51' : 2,	'52' : 1,	'53' : 1,	'54' : 1,	'55' : -1,	'56' : 2,	'57' : 2,	'58' : 3,	
	'59' : 1,	'60' : 1,	'61' : 1,	'62' : 1,	'63' : 1,	'64' : 2,	'65' : -1,	'66' : -1,	'67' : 2,	'68' : 2,	
	'69' : 2,	'70' : 2,	'71' : 2,	'72' : 2,	'73' : 2,	'74' : 2,	'75' : 3,	'76' : 3,	'77' : 0,	'78' : 0,	
	'79' : 0,	'79m': 2,	'80' : 0,	'81' : 0, 	'82': 2,	'82a': 2,	'82b': 2,	'999' : -1,	'-1' : 0,
	'83a0' : 0, '83a1' : 0, '83a2' : 0, '83a3' : 0, '83a4' : 0, '83a5' : 0, '83b0' : 0, '83b1' : 0, '83b2' : 0, '83b3' : 0, '83b4' : 0, '83b5' : 0,
	'84a0' : 0, '84a1' : 0, '84a2' : 0, '84a3' : 0, '84a4' : 0, '84a5' : 0, '84b0' : 0, '84b1' : 0, '84b2' : 0, '84b3' : 0, '84b4' : 0, '84b5' : 0,
	'85a0' : 0, '85a1' : 0, '85a2' : 0, '85a3' : 0, '85a4' : 0, '85a5' : 0, '85b0' : 0, '85b1' : 0, '85b2' : 0, '85b3' : 0, '85b4' : 0, '85b5' : 0,
	'86a0' : 0, '86a1' : 0, '86a2' : 0, '86a3' : 0, '86a4' : 0, '86a5' : 0, '86b0' : 0, '86b1' : 0, '86b2' : 0, '86b3' : 0, '86b4' : 0, '86b5' : 0,
	'87a0' : 0, '87a1' : 0, '87a2' : 0, '87a3' : 0, '87a4' : 0, '87a5' : 0, '87b0' : 0, '87b1' : 0, '87b2' : 0, '87b3' : 0, '87b4' : 0, '87b5' : 0,
	'88a0' : 0, '88a1' : 0, '88a2' : 0, '88a3' : 0, '88a4' : 0, '88a5' : 0, '88b0' : 0, '88b1' : 0, '88b2' : 0, '88b3' : 0, '88b4' : 0, '88b5' : 0,
	'89a0' : 0, '89a1' : 0, '89a2' : 0, '89a3' : 0, '89a4' : 0, '89a5' : 0, '89b0' : 0, '89b1' : 0, '89b2' : 0, '89b3' : 0, '89b4' : 0, '89b5' : 0,
	'90a0' : 0, '90a1' : 0, '90a2' : 0, '90a3' : 0, '90a4' : 0, '90a5' : 0, '90b0' : 0, '90b1' : 0, '90b2' : 0, '90b3' : 0, '90b4' : 0, '90b5' : 0,
	'91a0' : 0, '91a1' : 0, '91a2' : 0, '91a3' : 0, '91a4' : 0, '91a5' : 0, '91b0' : 0, '91b1' : 0, '91b2' : 0, '91b3' : 0, '91b4' : 0, '91b5' : 0,
	'420'  : 0,
}

imageOnPlanetCoords = {
	"attachment"	: [60,-25],
	"spacedock" 	: [[-40,-38],[-41,-65]],
	"pds" 			: [[-13,-37],[-14,-65]],
	"infantry" 		: [[ 14,-37],[ 13,-65]],
	"mech" 			: [[-44,-41],[ 40,-65]],
}

attachmentOffset = 28
bigPlanetOffset = 14
fontScale = 0.4
font = cv2.FONT_HERSHEY_SIMPLEX
fontColor = (0,0,0,255)
fontColorTokens = (255,255,255,255)
labelCharWidth = 8
labelCharHeight = 9


colorHueLookup = {
	"red" 		: 0,
	"orange" 	: -30,
	"yellow" 	: -55,
	"green" 	: -80,
	"blue" 		: 180,
	"purple" 	: 62,
	"pink"		: 38,
	"black"		: 0,
	"white"		: 0,
	"grey"		: 0,
	""			: 0,
}

hardColorValues = [0, 100, 200, 300, 40, 140, 240, 340, 80, 180, 280, 20, 120, 220, 320, 60, 160]

def clamp(v):
	if v < 0:
		return 0
	if v > 255:
		return 255
	return int(v + 0.5)

class RGBRotate(object):
	def __init__(self):
		self.matrix = [[1,0,0],[0,1,0],[0,0,1]]

	def set_hue_rotation(self, degrees):
		cosA = cos(radians(degrees))
		sinA = sin(radians(degrees))
		self.matrix[0][0] = cosA + (1.0 - cosA) / 3.0
		self.matrix[0][1] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
		self.matrix[0][2] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
		self.matrix[1][0] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
		self.matrix[1][1] = cosA + 1./3.*(1.0 - cosA)
		self.matrix[1][2] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
		self.matrix[2][0] = 1./3. * (1.0 - cosA) - sqrt(1./3.) * sinA
		self.matrix[2][1] = 1./3. * (1.0 - cosA) + sqrt(1./3.) * sinA
		self.matrix[2][2] = cosA + 1./3. * (1.0 - cosA)

	def apply(self, r, g, b):
		rx = r * self.matrix[0][0] + g * self.matrix[0][1] + b * self.matrix[0][2]
		gx = r * self.matrix[1][0] + g * self.matrix[1][1] + b * self.matrix[1][2]
		bx = r * self.matrix[2][0] + g * self.matrix[2][1] + b * self.matrix[2][2]
		return clamp(rx), clamp(gx), clamp(bx)

	def applyMatrix(self, inMat):
		outMat = np.zeros(inMat.shape, np.uint8)
		for x in range(inMat.shape[0]):
			for y in range(inMat.shape[1]):
				outMat[x, y] = self.apply(inMat[x, y, 0], inMat[x, y, 1], inMat[x, y, 2])
		return outMat

	def applyMatrixwithAlpha(self, inMat):
		outMat = np.zeros(inMat.shape, np.uint8)
		outMat[:,:,3] = inMat[:,:,3]
		outMat[:,:,0:3] = self.applyMatrix(inMat[:,:,0:3])
		return outMat

async def superimpose(underImage, overImage, centerpos, ignore_weight=False):
	overImageTL = (int(centerpos[0]-overImage.shape[0]/2),int(centerpos[1]-overImage.shape[1]/2))
	underImageTL = (0,0)
	overImageBR = (overImageTL[0] + overImage.shape[0],overImageTL[1] + overImage.shape[1])
	underImageBR = (underImage.shape[0],underImage.shape[1])
	finalTL = (min(overImageTL[0],underImageTL[0]),min(overImageTL[1],underImageTL[1]))
	finalBR = (max(overImageBR[0],underImageBR[0]),max(overImageBR[1],underImageBR[1]))

	finalImageShape = (finalBR[0]-finalTL[0],finalBR[1]-finalTL[1],4)
	finImage = np.zeros(finalImageShape, np.uint8)

	finImage[(0-finalTL[0]):(underImage.shape[0]-finalTL[0]),0-finalTL[1]:underImage.shape[1]-finalTL[1],:] = underImage

	for py in range(overImage.shape[0]):
		await asyncio.sleep(0)
		for px in range(overImage.shape[1]):
			localp = (int(py+centerpos[0]-int(overImage.shape[0]/2)-finalTL[0]), int(px+centerpos[1]-int(overImage.shape[1]/2)-finalTL[1]))
			if overImage[py,px,3] > 10 and overImage[py,px,3] < 200:
				weight = overImage[py,px,3] / 255.0
				if ignore_weight:
					weight = 1
				for i in range(3):
					finImage[localp[0],localp[1],i] = int(overImage[py,px,i]*weight) + int(finImage[localp[0],localp[1],i]*(1-weight))

			elif overImage[py,px,3] > 10:
				for i in range(3):
					finImage[localp[0],localp[1],i] = overImage[py,px,i]


	return finImage

def rotateImage(image, angle):
	image_center = tuple(np.array(image.shape[1::-1]) / 2)
	rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
	result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
	return result

def processHyperlane(tile):
	tileAddress=assetAddress+subAddresses["tiles"]
	side = re.search(r"[A-Za-z]", tile).group().lower()
	nums = re.split(r"[A-Za-z]", tile)
	tilenm = int(nums[0])
	rot = 0
	rot = int(nums[1])
	angle = rot*-60
	baseTile = cv2.imread(tileAddress+f"{tilenm:03d}"+side+str(rot)+".png", cv2.IMREAD_UNCHANGED)
	#rotTile = rotateImage(baseTile, angle)
	return baseTile

def seqGenerator(lenseq):
	d6 = int(lenseq/6)
	oseq = [0]*lenseq
	for i in range(lenseq):
		x=i+1
		oseq[i] = math.floor(abs(((x-2*d6)/d6)%(-3))+1)
	return oseq

def mapStringToTilePosSet(mapString):
	cleanedString = None
	## clean up
	if mapString.startswith("http:"):
		mapString=mapString[mapString.find("?")+1:]
	if mapString.find("&") > -1:
		stringList = mapString.split("&")
		for s in stringList:
			if s.startswith("tiles="):
				cleanedString = s[6:]
	else:
		if not(re.search(r"[^0-9\s,{}A-Za-z\-]", mapString)):
			cleanedString = mapString

	if not(cleanedString):
		return None

	tile_list = re.sub(r",|\s+", " ", cleanedString.strip()).split(" ")

	ringList = {}
	if tile_list[0][0] == "{":
		ringList["[0, 0, 0]"] = re.sub(r"[{}]", "", tile_list[0])
		tile_list.remove(tile_list[0])
	else:
		ringList["[0, 0, 0]"] = '18'

	numTiles = len(tile_list)
	thresh = 6
	ringPos = [1,0,0]
	cdir = 1
	cmax = 1
	trig = 1
	seq = seqGenerator(thresh)
	itr = 0

	for i in range(numTiles):
		if itr >= thresh:
			thresh = thresh+6
			ringPos[0] = ringPos[0] + 1
			itr=0
			seq = seqGenerator(thresh)
			cmax = cmax+1

		ringList[str(ringPos)] = tile_list[i]
		if ringPos[seq[itr]-1]==trig:
			cdir = -cdir
			trig = cmax-trig

		ringPos[seq[itr]-1]=ringPos[seq[itr]-1]+cdir 

		itr=itr+1

	return ringList

def getNumRingsFromRingList(ringList):
	maxVal = 0
	for testPos in range(3):
		for posstr in ringList.keys():
			tstr = re.sub(r"\s","",posstr[1:len(posstr)-1])
			tstr = tstr.split(',')
			pos = [0]*len(tstr)
			for t in range(len(tstr)):
				pos[t] = int(tstr[t])
			if pos[testPos] > maxVal:
				maxVal = pos[testPos]

	return maxVal+1

def getRealCoordsFromPos(posStr, center):
	tstr = re.sub(r"\s","",posStr[1:len(posStr)-1])
	tstr = tstr.split(',')
	pos = [0]*len(tstr)
	for t in range(len(tstr)):
		pos[t] = int(tstr[t])
	hexposheight = pos[0]*a1step[0]+pos[1]*a2step[0]+pos[2]*a3step[0]
	hexposwidth = pos[0]*a1step[1]+pos[1]*a2step[1]+pos[2]*a3step[1]
	realCoords = (center[0]+hexposheight*baseTileSize[0], center[1]+hexposwidth*baseTileSize[0])
	return realCoords

async def compositeMap(ringPosList):
	tileAddress="./" + assetAddress+subAddresses["tiles"]
	numRings = getNumRingsFromRingList(ringPosList)
	buffer = (numRings*2-2)*20

	totalwidth = int((((numRings*2)-2)*sqrt(3)/2)*baseTileSize[0]+baseTileSize[1] + buffer)
	totalheight = int((((numRings*2)-2)+1)*baseTileSize[0] + buffer)
	center = (int(totalheight/2), int(totalwidth/2))

	baseMap = np.ones((totalheight,totalwidth,4), np.uint8)
	baseMap = baseMap*255

	for posstr in ringPosList.keys():
		await asyncio.sleep(0)
		realCoords = getRealCoordsFromPos(posstr, center)
		if(re.search(r"[A-Za-z]", ringPosList[posstr])):
			nums = re.split(r"[A-Za-z]", ringPosList[posstr])
			fracture = False
			if nums[0] == "":
				tileNum = int(nums[1])
				fracture = True
			else:
				tileNum = int(nums[0])

			if tileNum < 92 and tileNum > 82:
				tileimg = processHyperlane(ringPosList[posstr])
			else:
				if not(fracture):
					side = re.search(r"[A-Za-z]", ringPosList[posstr]).group().lower()
					fStr = ""
				else:
					side = ""
					fStr = "F"
				tileNumString = f"{tileNum:03d}"
				tileimg = cv2.imread(tileAddress+fStr+tileNumString+side+".png", cv2.IMREAD_UNCHANGED)
		else:
			tileNum = int(ringPosList[posstr])
			if(tileNum < 0):
				tileNumString = "null"
			else:
				tileNumString = f"{tileNum:03d}"
			tileimg = cv2.imread(tileAddress+tileNumString+".png", cv2.IMREAD_UNCHANGED)
		usedimg = cv2.resize(tileimg, (int(baseTileSize[1]*0.95), int(baseTileSize[0]*0.95)), interpolation=cv2.INTER_LINEAR)
		await asyncio.sleep(0)
		baseMap = await superimpose(baseMap, usedimg, realCoords)

	await asyncio.sleep(0)
	mask = cv2.imread(tileAddress+'mask.png', cv2.IMREAD_UNCHANGED)
	await asyncio.sleep(0)
	maskR = cv2.resize(mask, (baseMap.shape[1], baseMap.shape[0]), interpolation=cv2.INTER_LINEAR)
	await asyncio.sleep(0)
	maskG = cv2.cvtColor(maskR, cv2.COLOR_RGBA2GRAY)
	for y in range(baseMap.shape[0]):
		await asyncio.sleep(0)
		for x in range(baseMap.shape[1]):
			if(maskG[y][x] < 128):
				baseMap[y][x][:]=0

	return baseMap

def ringListToTxt(ringList, filename):
	address = saveAddress + filename + ".txt"
	outLines = []

	with open(address, 'w') as f:
		for ring in ringList:
			for pos in ring:
				if(re.search(r"[A-Za-z]", ring[pos])):
					side = re.search(r"[A-Za-z]", ring[pos]).group().lower()
					nums = re.split(r"[A-Za-z]", ring[pos])
					tile = int(nums[0])
					outText = str(pos) + "=" + f"{tile:03d}" + side + nums[1]
				else:
					tile = int(ring[pos])
					outText = str(pos) + "=" + f"{tile:03d}"
				outLines.append(outText)
		f.write('\n'.join(outLines))

def readRingListSave(filename):
	address = saveAddress + filename + ".txt"
	output = {}

	with open(address, 'w') as f:
		line = f.readline()
		parameters = line.split(';')
		if(len(parameters) < 2):
			pos = line[:9]
			output[pos] = {}
			output[pos][tile] = line[10:13]
		else:
			pos = parameters[0][:9]
			output[pos] = {}
			output[pos][tile] = parameters[0][10:13]
			output[pos][attach] = re.sub(r"'|\s+", "", parameters[1][1:len(parameters[1])-1]).split(",")
			output[pos][fleet] = parameters[2]

	return output

def addAttachments(map, attachmentLinks):
	return None

async def renderMap(mapString, name, attachmentLinks=None):
	ringList = mapStringToTilePosSet(mapString)
	mapRender = await compositeMap(ringList)
	if name:
		cv2.imwrite(saveAddress+name+".png", mapRender)
	return mapRender

async def getTileIslandPos(ringList, mirror=False):
	maxVal = 0
	testPos = (1 if mirror else 2)
	for posstr in ringList.keys():
		tstr = re.sub(r"\s","",posstr[1:len(posstr)-1])
		tstr = tstr.split(',')
		pos = [0]*len(tstr)
		for t in range(len(tstr)):
			pos[t] = int(tstr[t])
		if pos[testPos] > maxVal:
			maxVal = pos[testPos]

	outPos = [0, 0, 0]
	oVal = int((int((maxVal - 1) / 2) + 2) * 2)
	hval = int(((maxVal - 1) / 2) + 2)
	if not(mirror):
		outPos = [hval, oVal, 0]
	else:
		outPos = [hval, 0, oVal]

	return str(outPos)

async def renderFullMap(mapString, name, attachmentLinks=None):
	ringList = mapStringToTilePosSet(mapString)

	mallicePos = await getTileIslandPos(ringList)

	if 17 in ringList or "17" in ringList.values():
		creussPos = await getTileIslandPos(ringList, True)
		ringList[creussPos] = "51"

	ringList[mallicePos] = "82a"

	mapRender = await compositeMap(ringList)
	if name:
		cv2.imwrite(saveAddress+name+".png", mapRender)
	return mapRender

async def renderMapFromObj(mapObj, name, forceRegen=False, fullMap = False, attachmentLinks = None):
	ringList = mapObj.copy()
	if not(exists(saveAddress+name+".png")) or forceRegen:

		if fullMap:
			mallicePos = await getTileIslandPos(ringList)
			ringList[mallicePos] = "82a"

		mapRender = await compositeMap(ringList)
		cv2.imwrite(saveAddress+name+".png", mapRender)
		
	return saveAddress+name+".png"

async def overlayGameStateOnMap(mapAddress, gameFrog, team, globalMap=False, useHardColors=False, colorExchange = {}):
	newAddress = mapAddress[:-4] + "_gameState.png"
	useHardColors
	teamMap = gameFrog.globalmap
	if not(globalMap):
		teamMap = gameFrog.getTeamMap(team)

	tilesMap = cv2.imread(mapAddress, cv2.IMREAD_UNCHANGED)
	dims = array(tilesMap).shape
	center = (int(dims[0]/2), int(dims[1]/2))
	hueRotator = RGBRotate()
	coloriterator = 0

	teamtocolormap = colorExchange

	for pos in teamMap.keys():
		await asyncio.sleep(0)
		if teamMap[pos] != '999':
			systemCoords = getRealCoordsFromPos(pos, center)
			tileNum = teamMap[pos]
			ntileType = tileType[str(tileNum).lower()]
			if(not(pos in gameFrog.gameState.keys())):
				continue
			systemState = gameFrog.gameState[pos]
			bigPlanet = False
			labels = {}

			if ntileType < 0:
				bigPlanet = True
				ntileType = 1

			systemCoordsLookup = systemOverlayLookup[ntileType]
			
			for i in range(len(systemState["spTokens"])):
				if(systemState["spTokens"][i] == "mirage"):
					tokenName = systemState["spTokens"][i]
					mirageCoords = getMiragePos[ntileType]
					tokenCoords = [0, 0]
					tokenCoords[0] = mirageCoords[0] + systemCoords[0]
					tokenCoords[1] = mirageCoords[1] + systemCoords[1]
					tokenImage = cv2.imread(assetAddress + subAddresses["tiles"] + subAddresses["tokens"] + subAddresses["space"] + tokenName + ".png", cv2.IMREAD_UNCHANGED)
					tilesMap = await superimpose(tilesMap, tokenImage, tokenCoords)
				else:
					tNum = i % len(systemCoordsLookup["sptoken"])
					tokenName = systemState["spTokens"][i]
					tokenCoords = [0,0]
					tokenCoords[0] = systemCoords[0] + systemCoordsLookup["sptoken"][tNum][1]
					tokenCoords[1] = systemCoords[1] + systemCoordsLookup["sptoken"][tNum][0]
					tokenImage = cv2.imread(assetAddress + subAddresses["tiles"] + subAddresses["tokens"] + subAddresses["space"] + tokenName + ".png", cv2.IMREAD_UNCHANGED)
					tilesMap = await superimpose(tilesMap, tokenImage, tokenCoords)


			if(len(systemState["planets"]) > 0):
				planetLookup = systemCoordsLookup["planets"]
				for i in range(len(systemState["planets"])):
					await asyncio.sleep(0)
					planet = systemState["planets"][list(systemState["planets"].keys())[i]]
					planetidtr = "planet" + str(i)
					labels[planetidtr] = {}

					planetOffset = planetLookup["basecoords"][i]
					if list(systemState["planets"].keys())[i] == "Mirage":
						planetOffset = getMiragePos[ntileType]

					tokennum = 0
					for k in range(len(planet["attachments"])):
						attachment = planet["attachments"][k]
						for j in range(len(attachment["tokens"])):
							tokenName = attachment["tokens"][j]["image"]
							tokenText = ""
							if(tokenName.startswith("Res") or tokenName.startswith("Inf")):
								tokenText = "+" + str(attachment["tokens"][j]["value"])

							extra = 0
							if(bigPlanet):
								extra = 20

							offset = [0, 0]
							offset[0] = planetLookup["attachments"][0][0] - (planetLookup["attachments"][1][0] * (tokennum%2)) + extra
							offset[1] = planetLookup["attachments"][0][1] - (planetLookup["attachments"][1][1] * math.floor(tokennum/2))
							tokennum = tokennum + 1

							for s in tokenExceptions.keys():
								if(tokenName.startswith(s)):
									if tokenExceptions[s] == "spacedock":
										offset = planetLookup["gdunit"]["spacedock"]["unit"]
									elif tokenExceptions[s] == "pds":
										offset = planetLookup["gdunit"]["pds"]["unit"]
									elif tokenExceptions[s] == "cover":
										offset = [0,0]

							tokenCoords = [0,0]
							tokenCoords[0] = systemCoords[0] + planetOffset[0] + offset[1]
							tokenCoords[1] = systemCoords[1] + planetOffset[1] + offset[0]

							tokenImage = cv2.imread(assetAddress + subAddresses["tiles"] + subAddresses["tokens"] + subAddresses["planet"] + tokenName + ".png", cv2.IMREAD_UNCHANGED)
							tilesMap = await superimpose(tilesMap, tokenImage, tokenCoords)

							if len(tokenText) > 0:
								tilesMap = cv2.putText(tilesMap, tokenText, (int(tokenCoords[1] - labelCharWidth - 4), int(tokenCoords[0] + labelCharHeight/2)), font, fontScale, fontColorTokens)

					planetFleet = planet["fleet"]
					color = planetFleet["color"]
					if useHardColors:
						if(str(color) in teamtocolormap.keys()):
							color = teamtocolormap[str(color)]
						else:
							teamtocolormap[str(color)] = hardColorValues[coloriterator]
							coloriterator = (coloriterator+1)%len(hardColorValues)
							color = teamtocolormap[str(color)]
					try:
						hueRotator.set_hue_rotation(int(color))
					except:
						hueRotator.set_hue_rotation(colorHueLookup[color])
					for unit in planetFleet["list"].keys():
						if unit == "pllabel":
							continue
						await asyncio.sleep(0)
						if planetFleet["list"][unit] > 0:
							if planetFleet["list"][unit] > 1 and unit != "control token":
								labels[planetidtr][unit] = planetFleet["list"][unit]
							if unit == "control token":
								unit = "pllabel"

							unitImage = []
							if(color == "white"):
								unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "white" + unit + ".png", cv2.IMREAD_UNCHANGED)
							elif (color == "grey"):
								unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "grey" + unit + ".png", cv2.IMREAD_UNCHANGED)
							elif (color == "black"):
								unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "white" + unit + ".png", cv2.IMREAD_UNCHANGED)
								unitImage[:,:,0] = 255-unitImage[:,:,0]
								unitImage[:,:,1] = 255-unitImage[:,:,1]
								unitImage[:,:,2] = 255-unitImage[:,:,2]
							elif (color == "yellow"):
								unitImage = cv2.imread(assetAddress + subAddresses["unit"] + unit + ".png", cv2.IMREAD_UNCHANGED)
								unitImage = hueRotator.applyMatrixwithAlpha(unitImage)
								a = unitImage[:,:,3]
								hsv = cv2.cvtColor(unitImage, cv2.COLOR_BGR2HSV)
								s = hsv[:,:,1]
								v = hsv[:,:,2]
								s = cv2.add(s, 41)
								v = cv2.add(v, 42)
								hsv = cv2.merge([hsv[:,:,0], s, v])
								unitImage = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
								unitImage = cv2.cvtColor(unitImage, cv2.COLOR_BGR2BGRA)
								unitImage[:,:,3] = a
							else:
								unitImage = cv2.imread(assetAddress + subAddresses["unit"] + unit + ".png", cv2.IMREAD_UNCHANGED)
								unitImage = hueRotator.applyMatrixwithAlpha(unitImage)

							offset = planetLookup["gdunit"][unit]["unit"]
							unitCoords = [0,0]
							unitCoords[0] = systemCoords[0] + planetOffset[0] + offset[1] + bigPlanet*bigPlanetOffset
							unitCoords[1] = systemCoords[1] + planetOffset[1] + offset[0]

							tilesMap = await superimpose(tilesMap, unitImage, unitCoords)

			systemFleet = systemState["fleet"]
			color = systemFleet["color"]
			if useHardColors:
				if(str(color) in teamtocolormap.keys()):
					color = teamtocolormap[str(color)]
				else:
					teamtocolormap[str(color)] = hardColorValues[coloriterator]
					coloriterator = (coloriterator+1)%len(hardColorValues)
					color = teamtocolormap[str(color)]
			try:
				hueRotator.set_hue_rotation(int(color))
			except:
				hueRotator.set_hue_rotation(colorHueLookup[color])
			for unit in systemFleet["list"].keys():
				await asyncio.sleep(0)
				if systemFleet["list"][unit] > 0:
					if systemFleet["list"][unit] > 1:
						labels[unit] = systemFleet["list"][unit]

					unitImage = []
					if(color == "white"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "white" + unit + ".png", cv2.IMREAD_UNCHANGED)
					elif (color == "grey"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "grey" + unit + ".png", cv2.IMREAD_UNCHANGED)
					elif (color == "black"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "white" + unit + ".png", cv2.IMREAD_UNCHANGED)
						unitImage[:,:,0] = 255-unitImage[:,:,0]
						unitImage[:,:,1] = 255-unitImage[:,:,1]
						unitImage[:,:,2] = 255-unitImage[:,:,2]
					elif (color == "yellow"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + unit + ".png", cv2.IMREAD_UNCHANGED)
						unitImage = hueRotator.applyMatrixwithAlpha(unitImage)
						a = unitImage[:,:,3]
						hsv = cv2.cvtColor(unitImage, cv2.COLOR_BGR2HSV)
						s = hsv[:,:,1]
						v = hsv[:,:,2]
						s = cv2.add(s, 41)
						v = cv2.add(v, 42)
						hsv = cv2.merge([hsv[:,:,0], s, v])
						unitImage = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
						unitImage = cv2.cvtColor(unitImage, cv2.COLOR_BGR2BGRA)
						unitImage[:,:,3] = a
					else:
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + unit + ".png", cv2.IMREAD_UNCHANGED)
						unitImage = hueRotator.applyMatrixwithAlpha(unitImage)

					offset = systemCoordsLookup["spunit"][unit]["unit"]
					unitCoords = [0,0]
					unitCoords[0] = systemCoords[0] + offset[1]
					unitCoords[1] = systemCoords[1] + offset[0]

					tilesMap = await superimpose(tilesMap, unitImage, unitCoords)

			labelImage = cv2.imread(assetAddress + subAddresses["unit"] + "label.png", cv2.IMREAD_UNCHANGED)
			for lkey in labels.keys():
				await asyncio.sleep(0)
				if(lkey.startswith("planet")):
					for pkey in labels[lkey].keys():
						await asyncio.sleep(0)
						colorTag = False
						if(labels[lkey][pkey] in colorHueLookup.keys()):
							colorTag = True
							offset = systemCoordsLookup["planets"]["pllabel"]
							color = labels[lkey][pkey]
							try:
								hueRotator.set_hue_rotation(int(color))
							except:
								hueRotator.set_hue_rotation(colorHueLookup[color])
							if(color == "white"):
								cv2.imread(assetAddress + subAddresses["unit"] + "whitepllabel.png", cv2.IMREAD_UNCHANGED)
							elif (color == "black"):
								cv2.imread(assetAddress + subAddresses["unit"] + "pllabel.png", cv2.IMREAD_UNCHANGED)
								grey = cv2.cvtColor(labelImage, cv2.COLOR_RGBA2GRAY)
								labelImage[:,:,0] = grey
								labelImage[:,:,1] = grey
								labelImage[:,:,2] = grey
							else:
								labelImage = cv2.imread(assetAddress + subAddresses["unit"] + "pllabel.png", cv2.IMREAD_UNCHANGED)
								labelImage = hueRotator.applyMatrixwithAlpha(labelImage)
						else:
							offset = systemCoordsLookup["planets"]["gdunit"][pkey]["label"]
						planetOffset = systemCoordsLookup["planets"]["basecoords"][int(lkey[-1])]

						labelCoords = [0,0]
						labelCoords[0] = systemCoords[0] + planetOffset[0] + offset[1] + bigPlanet*bigPlanetOffset
						labelCoords[1] = systemCoords[1] + planetOffset[1] + offset[0]

						tilesMap = await superimpose(tilesMap, labelImage, labelCoords)

						if(not(colorTag)):
							labelValue = str(labels[lkey][pkey])
							numChar = len(labelValue)

							labelValueOffsetW = labelCharWidth*(numChar-0.5)+1
							labelValueOffsetH = int(labelCharHeight/2)+1
							labelValueOffset = [-labelValueOffsetW, labelValueOffsetH]

							labelValueCoords = [0,0]
							labelValueCoords[0] = int(labelCoords[1] - labelValueOffset[1]) + 1
							labelValueCoords[1] = int(labelCoords[0] - labelValueOffset[0]) - 2
							org = (labelValueCoords[0], labelValueCoords[1])

							tilesMap = cv2.putText(tilesMap, str(labelValue), org, font, fontScale, fontColor)
				else:
					offset = systemCoordsLookup["spunit"][lkey]["label"]

					labelCoords = [0,0]
					labelCoords[0] = systemCoords[0] + offset[1]
					labelCoords[1] = systemCoords[1] + offset[0]

					tilesMap = await superimpose(tilesMap, labelImage, labelCoords)

					labelValue = str(labels[lkey])
					numChar = len(labelValue)

					labelValueOffsetW = labelCharWidth*(numChar-0.5)+1
					labelValueOffsetH = int(labelCharHeight/2)+1
					labelValueOffset = [-labelValueOffsetW, labelValueOffsetH]

					labelValueCoords = [0,0]
					labelValueCoords[0] = labelCoords[1] - labelValueOffset[1] + 1
					labelValueCoords[1] = labelCoords[0] - labelValueOffset[0] - 2

					tilesMap = cv2.putText(tilesMap, labelValue, (int(labelValueCoords[0]), int(labelValueCoords[1])), font, fontScale, fontColor)

			if "commandtokens" in systemState.keys():
				pnoffset = [0,0]
				for teamID in systemState["commandtokens"].keys():
					await asyncio.sleep(0)
					unitImage = []
					color = systemState["commandtokens"][teamID]
					try:
						hueRotator.set_hue_rotation(int(color))
					except:
						hueRotator.set_hue_rotation(colorHueLookup[color])	
					if(color == "white"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "whitepllabel.png", cv2.IMREAD_UNCHANGED)
					elif (color == "grey"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "greypllabel.png", cv2.IMREAD_UNCHANGED)
					elif (color == "black"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "whitepllabel.png", cv2.IMREAD_UNCHANGED)
						unitImage[:,:,0] = 255-unitImage[:,:,0]
						unitImage[:,:,1] = 255-unitImage[:,:,1]
						unitImage[:,:,2] = 255-unitImage[:,:,2]
					elif (color == "yellow"):
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "pllabel.png", cv2.IMREAD_UNCHANGED)
						unitImage = hueRotator.applyMatrixwithAlpha(unitImage)
						a = unitImage[:,:,3]
						hsv = cv2.cvtColor(unitImage, cv2.COLOR_BGR2HSV)
						s = hsv[:,:,1]
						v = hsv[:,:,2]
						s = cv2.add(s, 41)
						v = cv2.add(v, 42)
						hsv = cv2.merge([hsv[:,:,0], s, v])
						unitImage = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
						unitImage = cv2.cvtColor(unitImage, cv2.COLOR_BGR2BGRA)
						unitImage[:,:,3] = a
					else:
						unitImage = cv2.imread(assetAddress + subAddresses["unit"] + "pllabel.png", cv2.IMREAD_UNCHANGED)
						unitImage = hueRotator.applyMatrixwithAlpha(unitImage)

					uoffset = systemCoordsLookup["spunit"]["pllabel"]["unit"]
					unitCoords = [0,0]
					unitCoords[0] = systemCoords[0] + uoffset[1] + pnoffset[1]
					unitCoords[1] = systemCoords[1] + uoffset[0] + pnoffset[0]
					await asyncio.sleep(0)
					pnoffset[0] = pnoffset[0] + systemCoordsLookup["spunit"]["pllabel"]["offset"][0]
					pnoffset[1] = pnoffset[1] + systemCoordsLookup["spunit"]["pllabel"]["offset"][1]
					tilesMap = await superimpose(tilesMap, unitImage, unitCoords)


	cv2.imwrite(newAddress, tilesMap)

	return newAddress

async def generateMap(gameFrog):
	mapAddress = saveAddress+gameFrog.gameName + ".png"
	mapRender = await compositeMap(gameFrog.globalmap)
	cv2.imwrite(mapAddress, mapRender)
	return mapAddress

async def overlayUnitsOnFullMap(gameFrog, mainColor, colorExchange={}):
	return await overlayGameStateOnMap(await generateMap(gameFrog), gameFrog, mainColor, True, True, colorExchange)

async def generateTeamMap(teamMap, team, gameFrog):
	mapAddress = saveAddress+gameFrog.gameName + "_" + team.teamColor + ".png"
	mapRender = await compositeMap(teamMap)
	cv2.imwrite(mapAddress, mapRender)
	return await overlayGameStateOnMap(mapAddress, gameFrog, team, False, False)

async def generateUnitMapFromMapstring(mapString, systemFrog, mainColor):
	mapAddress = "localmap.png"
	mapRender = await compositeMap(systemFrog.globalmap)
	cv2.imwrite(mapAddress, mapRender)
	return await overlayGameStateOnMap(mapAddress, systemFrog, mainColor, True, False)

async def loadMap(mapString, name=None,  forceRegen=False, fullMap = False):
	print(name + " : " + mapString)
	if name:
		if not(exists(saveAddress+name+".png")) or forceRegen:
			if fullMap:
				await renderFullMap(mapString, name)
			else:
				await renderMap(mapString, name)
			
		return saveAddress+name+".png"

	else:
		cv2.imwrite(saveAddress+"TEMP"+".png", await renderMap(mapString, name))
		return saveAddress+"TEMP"+".png"
