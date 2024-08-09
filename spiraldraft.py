from abc import ABC
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

from random import shuffle

import dataLookup
from dataLookup import lookupTileValues

import io
import requests
import math

path = "./temp/"
tempname = "sp"
tempftype = ".jpg"
cropbox = (192,104,1050,957)
cropsize = (858,853)

# Spiral slices are defined as: [Right Neighbor adj, Right Adj, Center Adj, Equidistant, Left Neighbor Mecatol Rex]

class Spiral():
	hands = []

	def __init__(self, numSlices, planetAnomAsBlue):
		self.numSlices = numSlices
		self.planetAnomAsBlue = planetAnomAsBlue
		self.spiral = self.Definition()

	def Definition(self):
		self.tiles = {}
		S = ["37", "76", "75", "69", "35"]
		A = ["27", '28', '29', '30', '34', '38', '66', '72', '74']
		B = ['31', '33', '36', '70', '71', '73']
		C = ['24', '26', '32', '59', '62', '64', '65']
		D = ['19', '25', '61', '63']
		F = ['20', '21', '22', '23', '60']
		Red = ['39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '77', '78', '80', '79']

		if self.planetAnomAsBlue: # Put 67 and 68 (cormund and everra) in the blue system tiers rather than red
			D.extend(['67', '68'])
		else:
			Red.extend(['67', '68'])

		for t in S:
			self.tiles[t] = 0

		for t in A:
			self.tiles[t] = 1

		for t in B:
			self.tiles[t] = 2

		for t in C:
			self.tiles[t] = 3

		for t in D:
			self.tiles[t] = 4

		for t in F:
			self.tiles[t] = 5

		for t in Red:
			self.tiles[t] = 5

		setA = []
		setA.extend(S)
		setA.extend(A)
		setB = []
		setB.extend(B)
		setB.extend(C)
		setC = []
		setC.extend(D)
		setC.extend(F)
		self.hands = []
		self.handVals = []
		for i in range(self.numSlices):
			self.hands.append([0]*5)
			self.handVals.append([10]*5)
		setRed = Red[:]
		self.sets = [setA[:], setB[:], setC[:], setRed, setRed]

	def Generate(self):
		sets = self.sets
		hands = self.hands
		for i in range(len(sets)):
			for hand in hands:
				shuffle(sets[i])
				hand[i] = sets[i].pop()
		self.hands = hands

	def Randomize(self):
		hands = self.hands
		handVals = self.handVals
		tiles = self.tiles
		numSlices = self.numSlices
		for i in range(len(hands)):
			adjSum = tiles[hands[i][1]] + tiles[hands[i][2]]
			adjRes = lookupTileValues[hands[i][1]][0] + lookupTileValues[hands[i][2]][0]
			adjInf = lookupTileValues[hands[i][1]][1] + lookupTileValues[hands[i][2]][1]
			timeout = 100
			while adjSum > 5 or adjRes < 1 or adjInf < 1:
				shuffle(hands[i])
				adjSum = tiles[hands[i][1]] + tiles[hands[i][2]]
				adjRes = lookupTileValues[hands[i][1]][0] + lookupTileValues[hands[i][2]][0]
				adjInf = lookupTileValues[hands[i][1]][1] + lookupTileValues[hands[i][2]][1]
				timeout = timeout - 1
				if timeout == 0:
					return False;

			for j in range(len(hands[i])):
				handVals[i][j] = tiles[hands[i][j]]

		self.hands = hands
		self.handVals = handVals
		return True

	def Verify(self):
		handVals = self.handVals
		tiles = self.tiles
		for i in range(len(handVals)):
			adjSum = handVals[i][1] + handVals[i][2]
			totSum = handVals[i][0] + handVals[i][1] + handVals[i][2] + handVals[i][3] + handVals[i][4]
			print(f"Hand {i+1} has a ranked value of {adjSum} next to home, and {totSum} in total. (Lower is better)")
		worstMatch = 0
		bestMatch = 999
		worstMatchEQ = 0
		bestMatchEQ = 999
		for lefthand in handVals:
			for midhand in handVals:
				if lefthand == midhand:
					continue
				for righthand in handVals:
					if lefthand == righthand or midhand == righthand:
						continue
					handTotal = lefthand[0] + midhand[1] + midhand[2] + righthand[4]
					handTotalEQ = lefthand[0] + midhand[1] + midhand[2] + midhand[3] + righthand[4]
					if handTotal < bestMatch:
						bestMatch = handTotal
					if handTotal > worstMatch:
						worstMatch = handTotal
					if handTotalEQ < bestMatchEQ:
						bestMatchEQ = handTotalEQ
					if handTotalEQ > worstMatchEQ:
						worstMatchEQ = handTotalEQ
		print(f"The worse possible rank value of a slice is {worstMatch} (or {worstMatchEQ} with equidistant included.)")
		print(f"The best possible rank value of a slice is {bestMatch} (or {bestMatchEQ} with equidistant included.)")

	def generate_and_verify(self):
		self.Definition()
		self.Generate()
		if(not(self.Randomize())):
			self.generate_and_verify()
			print("REDO")
		# self.Verify()
		return self.hands

	def concat_coord(self, im1, im2, index):
		xy = [math.ceil((index+2)/2.0)-1, abs(((index+2)%2)-1)]
		newwidth = cropsize[0] * (xy[0]+1)
		newheight = cropsize[1] * (xy[1]+1)
		if im1.width > newwidth:
			newwidth = im1.width
		if im1.height > newheight:
			newheight = im1.height
		dst = Image.new('RGB', (int(newwidth), int(newheight)))
		dst.paste(im1, (0, 0))
		dst.paste(im2, (cropsize[0]*xy[0], cropsize[1]*xy[1]))
		return dst

	def combineHandImages(self):
		outImage = Image.open(path + tempname + str(self.numSlices-1) + tempftype)

		for i in range(self.numSlices-1):
			nImage = Image.open(path + tempname + str(i) + tempftype)
			outImage = self.concat_coord(outImage, nImage, i)

		pstr = path + tempname + "_full" + tempftype
		outImage.save(pstr)
		return pstr

	def generateLabels(self):
		for i in range(self.numSlices):
			sImage = Image.open(path + tempname + str(i) + tempftype)

			font = ImageFont.truetype("./fonts/Handel Gothic Regular.ttf", 32)
			achr = 65
			schr = chr(i+achr+1)
			if(i == self.numSlices-1):
				schr = chr(achr)

			draw = ImageDraw.Draw(sImage)
			name = f"Slice {schr}"
			h = 33
			draw.text((470,int(120-(h/2)+h*0)), name, (0,0,0), font=font)

			localr = 0
			locali = 0
			localEX = []
			fullr = 0
			fulli = 0
			fullEX = []
			hand = self.hands[i]
			for j in range(len(hand)):
				tile = hand[j]
				r, inf, EX = lookupTileValues[tile]
				fullr = fullr + r
				fulli = fulli + inf
				fullEX.extend(EX)
				if(j == 1 or j == 2):
					localr = localr + r
					locali = locali + inf
					localEX.extend(EX)

			skips = ""
			leg = ""
			worms = ""
			for v in localEX:
				if v == "L":
					leg = leg + v
				elif ord(v) < 128:
					skips = v + skips
				else:
					worms = worms + v
			localEXstr = f"{skips} {leg} {worms}"

			skips = ""
			leg = ""
			worms = ""
			for v in fullEX:
				if v == "L":
					leg = leg + v
				elif ord(v) < 128:
					skips = v + skips
				else:
					worms = worms + v
			fullEXstr = f"{skips} {leg} {worms}"

			font = ImageFont.truetype("./fonts/MyriadPro-bold.ttf", 32)

			localstring = f"{localr}/{locali} {localEXstr}"
			draw.text((470,int(120-(h/2)+h*1.5)), localstring, (0,0,0), font=font)

			fullstring = f"{fullr}/{fulli} {fullEXstr}"
			draw.text((470,int(120-(h/2)+h*3)), fullstring, (0,0,0), font=font)

			sImage.save(path + tempname + str(i) + tempftype)

	def generateImages(self):
		for i in range(len(self.hands)):
			hand_string = f"{{{self.hands[i][2]}}},-1,-1,{self.hands[i][1]},0,-1,{self.hands[i][3]},-1,-1,-1,{self.hands[i][0]},-1,-1,-1,-1,-1,-1,-1,{self.hands[i][4]}"
			hand_url = f"http://ti4-map.appspot.com/map?j=true&labels=true&tiles={hand_string}"

			r = requests.get(hand_url, stream=True)
			hand_image = None
			if(r.status_code == 200):
				hand_image = Image.open(io.BytesIO(r.content)).crop(cropbox)
				hand_image.save(path + tempname + str(i) + tempftype)

		self.generateLabels()
		combined_image = self.combineHandImages()
		return combined_image