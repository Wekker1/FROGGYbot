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

assetAddress = "assets\\"
subAddresses = {
	"unit" : "units\\smUnit\\",
	"tiles": "systems\\clean\\tiles\\",
	"attachments" : "tokens\\",
		"space" : "space\\",
		"planet": "planet\\",
	"tokens" : "tokens\\"
}

saveAddress = "saves\\"

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
	"c" : "cruiser.png",
	"C" : "carrier.png",
	"D" : "dreadnought.png",
	"w" : "WarSun.png",
	"F" : "flagship.png",
}

colorHueLookup = {
	"red" 		: 0,
	"orange" 	: -30,
	"yellow" 	: -55,
	"green" 	: -80,
	"blue" 		: -170,
	"purple" 	: 62,
	"pink"		: 38,
	"black"		: 0,
	"white"		: 0,
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