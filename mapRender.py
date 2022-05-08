import cv2
import pickle
import random
import os
import re
import io
from os.path import exists
from dotenv import load_dotenv
from math import sqrt,cos,sin,radians

assetAddress = "assets\\"
subAddresses = {
	"unit" : "units\\ttsrollersnips\\",
	"tiles": "systems\\clean\\tiles\\",
	"attachments" : "tokens\\",
		"space" : "space\\",
		"planet": "planet\\",
	"tokens" : "tokens\\"
}

baseTileSize = (260,300)
a1step = (-1, 0)
a2step = (0.5, sqrt(3)/2)
a3step = (0.5, -sqrt(3)/2)

unitsAddresses = {
	infantry : "infantry.png",
	mech : "mech.png",
	fighter : "fighter.png",
	PDS : "PDS.png",
	spacedock : "spacedock.png",
	destroyer : "destroyer.png",
	cruiser : "cruiser.png",
	carrier : "carrier.png",
	dreadnought : "dreadnought.png",
	warsun : "WarSun.png",
	flagship : "flagship.png",
}

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

def superimpose(underImage, overImage, centerpos):
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
		for px in range(overImage.shape[1]):
			localp = (int(py+centerpos[0]-int(overImage.shape[0]/2)-finalTL[0]), int(px+centerpos[1]-int(overImage.shape[1]/2)-finalTL[1]))
			if overImage[py,px,3] > 10 and overImage[py,px,3] < 200:
				weight = overImage[py,px,3] / 255.0
				for i in range(3):
					finImage[localp[0],localp[1],i] = int(overImage[py,px,i]*weight) + int(finImage[localp[0],localp[1],i]*(1-weight))
			elif overImage[py,px,3] > 10:
				finImage[localp[0],localp[1],:] = overImage[py,px,:]

	return finImage

def queueImageCombine(ImageList, PosList):
	outImage = None
	skipFirst = True
	for imageid in ImageList:
		if skipFirst:
			skipFirst = false
			outImage = ImageList[imageid]
		else:
			outImage = superimpose(outImage, ImageList[imageid], PosList[])

	return outImage

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
		if not(re.search(r"[^0-9\s,{}]", mapString)):
			cleanedString = mapString

	if not(cleanedString):
		return None

	tile_list = re.sub(r",|\s+", " ", cleanedString.strip()).split(" ")

	ringLists = [0]
	if tile_list[0][0] == "{":
		ringLists[0] = {"(0,0,0)" : re.sub(r"[{}]", "", tile_list[0])}
		tile_list.remove(tile_list[0])
	else:
		ringLists[0] = {"(0,0,0)" : 18}

	co = 0
	ca = 2
	rcount = 0
	for i in range(math.ceil(len(tile_list)/6)):
		if i >= co:
			rcount = rcount+1
			co = co + ca
			ca = ca+1

	for i in range(rcount):
		ringLists.append({})

	numTiles = len(tile_list)

	thresh = 6
	cring = 1
	ringPos = [1,0,0]
	cdir = 1
	cmax = 1
	trig = 1
	seq = seqGenerator(thresh)
	itr = 0

	for i in range(numTiles):
		if itr >= thresh:
			thresh = thresh+6
			cring = cring+1
			ringPos[0] = ringPos[0] + 1
			itr=0
			seq = seqGenerator(thresh)
			cmax = cmax+1

		ringLists[cring][str(ringPos)] = tile_list[i]
		if ringPos[seq[itr]-1]==trig:
			cdir = -cdir
			trig = cmax-trig

		ringPos[seq[itr]-1]=ringPos[seq[itr]-1]+cdir 

		itr=itr+1

	return ringLists

def compositeMap(ringPosList, buffer):
	tileAddress=assetAddress+subAddresses["tiles"]

	totalwidth = int((((len(ringPosList)*2)-2)*sqrt(3)/2)*baseTileSize[0]+baseTileSize[1] + buffer)
	totalheight = int((((len(ringPosList)*2)-2)+1)*baseTileSize[0] + buffer)
	center = (int(totalheight/2), int(totalwidth/2))
	print((totalheight,totalwidth))

	baseMap = np.ones((totalheight,totalwidth,4), np.uint8)
	baseMap = baseMap*255

	for ring in ringPosList:
		for posstr in ring:
			tstr = re.sub(r"\s","",posstr[1:len(posstr)-1])
			tstr = tstr.split(',')
			pos = [0]*len(tstr)
			for t in range(len(tstr)):
				pos[t] = int(tstr[t])
			hexposheight = pos[0]*a1step[0]+pos[1]*a2step[0]+pos[2]*a3step[0]
			hexposwidth = pos[0]*a1step[1]+pos[1]*a2step[1]+pos[2]*a3step[1]
			realCoords = (center[0]+hexposheight*baseTileSize[0], center[1]+hexposwidth*baseTileSize[0])
			tileNum = int(ring[posstr])
			print(str(tileNum) + " at " + str(realCoords))
			tileNumString = f"{tileNum:03d}"
			tileimg = cv2.imread(tileAddress+tileNumString+".png", cv2.IMREAD_UNCHANGED)
			usedimg = cv2.resize(tileimg, (int(baseTileSize[1]*0.95), int(baseTileSize[0]*0.95)), interpolation=cv2.INTER_LINEAR)
			baseMap = superimpose(baseMap, usedimg, realCoords)

	baseMapSmall = cv2.resize(baseMap, (int(baseMap.shape[1]*0.20), int(baseMap.shape[0]*0.20)), interpolation=cv2.INTER_LINEAR)

	mask = cv2.imread(tileAddress+'mask.png', cv2.IMREAD_UNCHANGED)
	maskR = cv2.resize(mask, (baseMapSmall.shape[1], baseMapSmall.shape[0]), interpolation=cv2.INTER_LINEAR)
	maskG = cv2.cvtColor(maskR, cv2.COLOR_RGBA2GRAY)
	for y in range(baseMapSmall.shape[0]):
		for x in range(baseMapSmall.shape[1]):
			if(maskG[y][x] < 128):
				baseMapSmall[y][x][:]=0

	return baseMap, baseMapSmall

