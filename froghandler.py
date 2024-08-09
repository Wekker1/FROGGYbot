import cv2
import pickle
import random
import os
import re
import io
import math
import numpy as np
from os.path import exists
from dotenv import load_dotenv
from math import sqrt,cos,sin,radians
import mapRender
from mapRender import *
import dataLookup
from dataLookup import *

mapsFile = "FrogMaps.pickle"
teamsFile = "teams.pickle"

#Maps structured along 3 axis along the inverted-Y directions. Tiles are defined by a 3-coordinate on those axis, see mapreference.png
#Teams are structured as dicts like the following default:
empty_team = {
    'gamename' : 'none',
    'teamname' : 'none',
    'team' : [],
    'teamHSID' : "-1",
    'teamcolor': "0",
}

hsIDFromFaction = {
    "Arborec" : "5", 
    "Argent" : "58", 
    "Barony" : "10", 
    "Cabal" : "54",
    "Empyrean" : "56", 
    "Ghosts" : "17", 
    "Hacan" : "16", 
    "Jol-Nar" : "12", 
    "Keleres [Argent]" : "58k", 
    "Keleres [Mentak]" : "2k", 
    "Keleres [Xxcha]" : "14k",
    "L1Z1X" : "6", 
    "Mahact" : "52", 
    "Mentak" : "2",
    "Muaat" : "4",
    "Naalu" : "9", 
    "Naaz-Rokha" : "57", 
    "Nekro" : "8", 
    "Nomad" : "53",
    "Saar" : "11", 
    "Sardakk" : "13", 
    "Sol" : "1", 
    "Titans" : "55",
    "Winnu" : "7", 
    "Xxcha" : "14", 
    "Yin" : "3", 
    "Yssaril" : "15",
}

defaultStats = {
    "points" : 0,
    "maxComm" : 0,
    "comm" : 0,
    "tg" : 0,
    "tacticTokens" : 3,
    "fleetTokens" : 3,
    "stratTokens" : 2,
    "reinforcements" : {
        "units" : {
            "list" :{
                "spacedock"     : 3, 
                "pds"           : 6, 
                "infantry"      : 12, 
                "cruiser"       : 8, 
                "destroyer"     : 8, 
                "fighter"       : 10, 
                "flagship"      : 1, 
                "warsun"        : 2, 
                "dreadnought"   : 5, 
                "carrier"       : 4, 
                "mech"          : 4}, 
            "color"         : ""}, 
        "commandtokens" : 8, 
        "controltokens" : 17},
    "technology" : [],
    "planets" : [],
    "relicFragments" : {},
    "promissoryNotes" : [], #Must be filled during initialization as depends on color
    "relics" : [],
    "playarea" : [], #Promissory notes, agendas, misc.
    "leaders" : {},
    "secrets" : [],
    "actioncards" : [],
    "strategycard" : "",
    "additionalcomponents" : {}, #For creuss, naalu, cabal, and other factions with extra components
}

promNotes = ["Support for the Throne", "Ceasefire", "Trade Agreement", "Political Secret", "Alliance"]

allDefaultWormholes = {
    "alpha" : ['26', '39', '79', '82b'],
    "beta" : ['25', '40', '64', '82b'],
    "delta" : ['17', '51'],
    "gamma" : ['82a', '82b'],
}

# FrogObjs are structured as follows:
'''
frogMap ->
    gameName
    globalmap ->
        {pos : tileid}
    teams ->
        [Team ... Team] -> {}
            name
            faction
            discord id
            color
            stats ->
                points
                maxComm
                comm
                tg
                tactic tokens
                fleet tokens
                strategy tokens
                reinforcements ->
                    units ->
                        Fleet{list : {unit : num}, color}
                    command tokens
                    control tokens
                tech
                planets
                relic frags
                prom notes in hand
                relics
                playarea
                secrets
                acs
                strat card
                [?votes?]
                etc.
    teamMaps ->
        {teamname : map} ->
            {pos : tileID} some hidden by Frog of War
    gameState -> {}
        systemsWithWormholes : {type : [pos ... pos]}
        pos ... pos : systemState ->
            spTokens : []
            commandTokens : []
            fleet{list : {unit : num}, color}
            planets ->
                [Planet, Planet] -> {}
                    name
                    attachments -> {}
                        name
                        tokens -> {}
                            name (Res, Inf, TechSkip, etc.) : ""
                            value -- if Res or Inf : #
                    fleet{list : {unit : num}, color}
                    stats -> {exhausted, res, inf, etc.}
        objectives : {} ->
            name
            scored : [teamname ... teamname]
            type : (stage1, stage2, secret, [relic, agenda, custodians, imperial])
        visibility : {team : posList} ->
            {pos : visibility} (visbility ranges from 0 [tile only], 1 [full system], 2 [full system and adj])
        specialVis : {team : posList}
        ghosts : true/false
        ---gameState may expand over time
'''
baseGameState = {
    "systemsWithWormholes" : {"alpha" : [], "beta" : [], "delta" : [], "gamma" : []},
    #pos -> systemState
    "objectives" : {},
    "visibility" : {},
    "specialVis" : {},
    "ghosts" : [False, ""],
}

emptySystemState = {
    "spTokens" : [],
    "commandtokens" : [],
    "fleet" : {},
    "planets" : {},
}

emptyPlanetState = {
    "name" : "",
    "attachments" : {},

}

# 3 adjacency scenarios: (these assume the pos is on the vert axis (or 0 zone) and can be rotated 60deg by offseting the index [type 1 must rotate ccw, type 2 cw])
adjTypes = {
    1 : [[0, -1, -1], [0, 0, -1], [0, 1, 0], [0, 1, 1], [0, 0, 1], [0, -1, 0]], #Offaxis
    2 : [[0, 0, 1], [1, 0, 1], [1, 0, 0], [1, 1, 0], [0, 1, 0], [-1, 0, 0]],  #Onaxis
    3 : [[1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [1, 0, 1]], #At [0, 0, 0]
}

newTilePositionMapping = [
    "[1, 0, 0]",
    "[1, 1, 0]",
    "[0, 1, 0]",
    "[0, 1, 1]",
    "[0, 0, 1]",
    "[1, 0, 1]",
    # For adj through wormholes:
    "[3, 0, 0]",
    "[3, 2, 0]",
    "[2, 3, 0]",
    "[0, 3, 0]",
    "[0, 3, 2]",
    "[0, 2, 3]",
    "[0, 0, 3]",
    "[2, 0, 3]",
    "[3, 0, 2]",
    # ring-4 wormholes:
    "[4, 4, 0]",
    "[0, 4, 4]",
    "[4, 0, 4]",
    # ring-5 wormholes:
    "[5, 1, 0]",
    "[5, 3, 0]",
    "[3, 5, 0]",
    "[1, 5, 0]",
    "[0, 5, 1]",
    "[0, 5, 3]",
    "[0, 3, 5]",
    "[0, 1, 5]",
    "[1, 0, 5]",
    "[3, 0, 5]",
    "[5, 0, 3]",
    "[5, 0, 1]",
]

def identifyHomeSystem(mapObj, faction):
    if faction in hsIDFromFaction.keys():
        for key in mapObj.keys():
            if mapObj[key] == hsIDFromFaction[faction]:
                return key;
    else:
        return -1

def getAdjacentFromWormholes(gameFrog, syspos):
    outSysPos = []
    frogState = gameFrog.gameState
    allWorms = frogState["systemsWithWormholes"]
    for wormType in allWorms.keys():
        if syspos in allWorms[wormType]:
            for aPos in allWorms[wormType]:
                if aPos != syspos:
                    outSysPos.append(aPos)

    return outSysPos

def getAdjacentSystems(gameFrog, mapObj, syspos):
    tstr = re.sub(r"\s","",syspos[1:len(syspos)-1])
    tstr = tstr.split(',')
    sysposList = [0]*len(tstr)
    for t in range(len(tstr)):
        sysposList[t] = int(tstr[t])

    posAdj = []
    offSet = 0
    Xnull = (sysposList[0]==0)
    Ynull = (sysposList[1]==0)
    Znull = (sysposList[2]==0)
    adjType = Xnull + Ynull + Znull
    if(adjType == 1):
        offSet = (Xnull*0 + Ynull*2 + Znull*1) % 3
    elif(adjType == 2):
        offSet = (Ynull*Znull*0 + Xnull*Znull*2 + Xnull*Ynull*1) % 3
    
    for i in range(6):
        tempList = sysposList.copy()
        for ind in range(3):
            tempList[ind] = tempList[ind] + adjTypes[adjType][i][(ind+offSet)%3]
        posAdj.append(str(tempList))

    posAdj.extend(getAdjacentFromWormholes(gameFrog, syspos))
    outlist = []

    for aPos in posAdj:
        if aPos in mapObj.keys():
            outlist.append(aPos)

    return outlist

def getAdjacentSystemsOrderedList(gameFrog, mapObj, syspos):
    tstr = re.sub(r"\s","",syspos[1:len(syspos)-1])
    tstr = tstr.split(',')
    sysposList = [0]*len(tstr)
    for t in range(len(tstr)):
        sysposList[t] = int(tstr[t])

    posAdj = []
    offSet = 0
    odrOffset = 0
    Xnull = (sysposList[0]==0)
    Ynull = (sysposList[1]==0)
    Znull = (sysposList[2]==0)
    adjType = Xnull + Ynull + Znull
    if(adjType == 1):
        offSet = (Xnull*0 + Ynull*2 + Znull*1) % 3
        odrOffset = (Xnull*0 + Ynull*4 + Znull*2)
    elif(adjType == 2):
        offSet = (Ynull*Znull*0 + Xnull*Znull*2 + Xnull*Ynull*1) % 3
        odrOffset = (Ynull*Znull*2 + Xnull*Znull*0 + Xnull*Ynull*4)


    for i in range(6):
        tempList = sysposList.copy()
        for ind in range(3):
            tempList[ind] = tempList[ind] + adjTypes[adjType][(i+odrOffset)%6][(ind+offSet)%3]
        posAdj.append(str(tempList))

    outlist = []

    for aPos in posAdj:
        if aPos in mapObj.keys():
            outlist.append(aPos)
        else:
            outlist.append("")

    return outlist

class frogMap():
    def __init__(self, gameName, mapObj, teams, gameState = baseGameState):
        self.gameName = gameName
        self.globalmap = mapObj
        self.teams = teams
        teamMapsDef = {}
        for team in teams:
            teamMapsDef[team.teamColor] = {}
        self.teamMaps = teamMapsDef
        self.gameState = gameState

    def getTeamMap(self, team):
        return self.teamMaps[team.teamColor]

    def autoFillWormholes(self):
        systemsWithWormholes = {"alpha" : [], "beta" : [], "gamma" : [], "delta" : []}
        hList = []
        for h in allDefaultWormholes.values():
            hList.extend(h)
        for wType in self.gameState["systemsWithWormholes"]:
            for w in self.gameState["systemsWithWormholes"][wType]:
                if not(w in hList):
                    hList.extend(w)

        uniList = list(set(hList))
        for pos in self.globalmap:
            if self.globalmap[pos] in uniList:
                for wType in allDefaultWormholes.keys():
                    if self.globalmap[pos] in allDefaultWormholes[wType] or pos in self.gameState["systemsWithWormholes"][wType]:
                        systemsWithWormholes[wType].append(pos)

        self.gameState["systemsWithWormholes"] = systemsWithWormholes

    def getOccupiedSystems(self, team):
        occSystems = []
        color = team.teamColor
        for pos in self.globalmap.keys():
            colorskip = False
            for planetname in self.gameState[pos]["planets"]:
                if not(colorskip):
                    if self.gameState[pos]["planets"][planetname]["fleet"]["color"] == color:
                        colorskip = True
            if self.gameState[pos]["fleet"]["color"] == color or colorskip:
                occSystems.append(pos)
        return occSystems

    def determineVisibility(self, team):
        visible = []
        occupied = self.getOccupiedSystems(team)
        visible.extend(occupied)
        for pos in occupied:
            visible.extend(getAdjacentSystems(self, self.globalmap, pos))
        visible.extend(self.gameState["specialVis"][team.teamColor])
        visible = list(set(visible))
        return visible

    def generateTeamMaps(self):
        for team in self.teams:
            teamMap = self.teamMaps[team.teamColor]
            generateTeamMap(teamMap, team, self)

    def darkenFrogOfWar(self, adlPos = [], forceRegen = False):
        mapObj = self.globalmap
        emptyMap = {}

        for pos in mapObj.keys():
            emptyMap[pos] = "999"

        for team in self.teams:
            teamMap = emptyMap.copy()

            homePos = identifyHomeSystem(mapObj, team.faction)
            if not(homePos == -1):
                teamMap[homePos] = mapObj[homePos]
            visSystems = self.determineVisibility(team)

            if (visSystems != self.gameState["visibility"][team.teamColor]) or forceRegen:
                self.gameState["visibility"][team.teamColor] = visSystems
                self.teamMaps[team.teamColor] = teamMap
                
            self.teamMaps[team.name] = teamMap

    def darkenFrogOfWarOneTeam(self, team, adlPos = [], forceRegen = False):
        mapObj = self.globalmap
        emptyMap = {}

        for pos in mapObj.keys():
            emptyMap[pos] = "999"

        teamMap = emptyMap.copy()

        homePos = identifyHomeSystem(mapObj, team.faction)
        if not(homePos == -1):
            teamMap[homePos] = mapObj[homePos]
        visSystems = self.determineVisibility(team)

        if (visSystems != self.gameState["visibility"][team.teamColor]) or forceRegen:
            self.gameState["visibility"][team.teamColor] = visSystems
            self.teamMaps[team.teamColor] = teamMap
        self.teamMaps[team.name] = teamMap

    def genPlanetDict(self, sysnum):
        try:
            sysnum = re.sub('[A-Za-z].*', '', sysnum)
            if not(int(sysnum) in systems.keys()):
                return {}
            else:
                returnList = {}
                for planetname in systems[int(sysnum)]:
                    deepState = {}
                    planetDict = {}
                    planetDict["attachments"] = {}
                    planetDict["fleet"] = deepcopy(deepState, emptyGroundFleet)
                    planetDict["stats"] = planets[planetname]
                    returnList[planetname] = planetDict
                return returnList
        except:
            return {}

    def populateEmptySystems(self):
        for pos in self.globalmap.keys():
            planetD = self.genPlanetDict(self.globalmap[pos])
            deepState = {}
            self.gameState[pos] = {
                "spTokens" : [],
                "plTokens" : [],
                "fleet" : deepcopy(deepState, emptyFleet),
                "planets" : planetD,
            }

    def getPosFromTileNum(self, tileID):
        gs = self.globalmap
        keys = list(gs.keys())
        values = list(gs.values())
        values = [re.sub('[A-Za-z].*', '', s) for s in values]
        tileID = re.sub('[A-Za-z].*', '', tileID)
        return keys[values.index(tileID)]

    def getSingleSystemMapString(self, tileID, getNeighbors):
        #self.autoFillWormholes()
        tiles = []
        tiles.append(tileID)
        targetPos = self.getPosFromTileNum(tileID)
        if(getNeighbors):
            adj = getAdjacentSystemsOrderedList(self, self.globalmap, targetPos)
            for a in adj:
                if(a == ""):
                    tiles.append("")
                else:
                    tiles.append(a)
        mstring = "{" + tiles[0] + "}"
        for it in tiles[1:]:
            if(it == ""):
                mstring = mstring + " 999"
            else:
                mstring = mstring + " " + str(self.globalmap[it])

        wormholeTiles = []
        if(getNeighbors):
            for l in range(12):
                mstring = mstring + " 999"
            adj = getAdjacentFromWormholes(self, targetPos)
            for a in adj:
                wormholeTiles.append(a)
        wtt  = 0
        for wit in wormholeTiles:
            if(wtt == 12):
                mstring = mstring + " 999"
            wtt = wtt + 1
            mstring = mstring + " " + str(self.globalmap[wit]) + " 999"
            if(wtt == 9):
                mstring = mstring + " 999 999 999 999"
            if(wtt == 12):
                mstring = mstring + " 999 999"
            if(wtt > 9 and wtt < 12):
                mstring = mstring + " 999 999 999 999 999 999"
            if(wtt > 12 and wtt%2==0):
                mstring = mstring + " 999 999"
        return mstring

    def determineFrogVisibleFromSystem(self, tileID, mapObj, colorTeamDict):
        targetPos = self.getPosFromTileNum(tileID)
        adj = getAdjacentSystemsOrderedList(self, self.globalmap, targetPos)
        wadj = getAdjacentFromWormholes(self, targetPos)

        teams = []

        for t in colorTeamDict.keys():
            team = Team(t, t, colorTeamDict[t])
            teams.append(team)

        systemFrog = frogMap(tileID, mapObj, teams)
        tiles = [targetPos]
        oposTonpos = {targetPos : ["[0, 0, 0]"]}

        for al in range(len(adj)):
            if(adj[al] == ""):
                oposTonpos[adj[al]] = [""]
            else:
                if(adj[al] in oposTonpos):
                    oposTonpos[adj[al]].append(newTilePositionMapping[al])
                else:
                    oposTonpos[adj[al]] = [newTilePositionMapping[al]]
            tiles.append(adj[al])

        for w in range(len(wadj)):
            if(wadj[w] == ""):
                oposTonpos[wadj[w]] = [""]
            else:
                if(wadj[w] in oposTonpos):
                    oposTonpos[wadj[w]].append(newTilePositionMapping[w+6])
                else:
                    oposTonpos[wadj[w]] = [newTilePositionMapping[w+6]]
            tiles.append(wadj[w])

        mapList = []
        for t in tiles:
            if not(t == "") and not(t in mapList):
                mapList.append(t)
                for pos in oposTonpos[t]:
                    temp = {}
                    systemFrog.gameState[pos] = deepcopy(temp, self.gameState[t])

                    systemFrog.gameState[pos]["fleet"]["color"] = colorTeamDict[self.gameState[t]["fleet"]["color"]]

                    for planetname in self.gameState[t]["planets"]:
                        systemFrog.gameState[pos]["planets"][planetname]["fleet"]["color"] = colorTeamDict[self.gameState[t]["planets"][planetname]["fleet"]["color"]]

        return systemFrog

    def determineTeamsVisibleFromSystem(self, tileID, getNeighbors):
        targetPos = self.getPosFromTileNum(tileID)
        adj = getAdjacentSystems(self, self.globalmap, targetPos)
        wadj = getAdjacentFromWormholes(self, targetPos)
        tiles = [targetPos]
        for a in adj:
            tiles.append(a)
        for w in wadj:
            tiles.append(a)
        teamList = []
        for t in tiles:
            if not(self.gameState[t]["fleet"]["color"] in teamList):
                teamList.append(self.gameState[t]["fleet"]["color"])
            for planetname in self.gameState[t]["planets"]:
                if not(self.gameState[t]["planets"][planetname]["fleet"]["color"] in teamList):
                    teamList.append(self.gameState[t]["planets"][planetname]["fleet"]["color"])
        return teamList

    def reconcilePresetColors(self, teamColorDict):
        preset = {}
        if("preset" in self.gameState.keys()):
            preset = self.gameState["preset"]

        for k in teamColorDict.keys():
            preset[k] = teamColorDict[k]

        self.gameState["preset"] = preset

    def toggleCommandTokenInSystem(self, tileID, team):
        targetPos = self.getPosFromTileNum(tileID)
        if not("commandtokens" in self.gameState[targetPos]):
            self.gameState[targetPos]["commandtokens"] = {}
        if not(team["teamHSID"] in self.gameState[targetPos]["commandtokens"]):
            if("teamcolor" in team.keys()):
                self.gameState[targetPos]["commandtokens"][team["teamHSID"]] = team["teamcolor"]
            else:
                self.gameState[targetPos]["commandtokens"][team["teamHSID"]] = team["teamHSID"]
        else:
            del self.gameState[targetPos]["commandtokens"][team["teamHSID"]]

    def addStartingUnits(self):
        for team in self.teams:
            faction = team.faction
            startFleet = startingFleets[faction]
            fleetColor = team.teamColor
            hsID = hsIDFromFaction[faction]
            hsPos = list(self.globalmap.keys())[list(self.globalmap.values()).index(hsID)]

            for unittype in spaceUnits:
                if unittype in startFleet.keys():
                    self.gameState[hsPos]["fleet"]["list"][unittype] = startFleet[unittype]
            self.gameState[hsPos]["fleet"]["color"] = fleetColor

            for unittype in groundUnits:
                if unittype in startFleet.keys():
                    self.gameState[hsPos]["planets"][list(self.gameState[hsPos]["planets"].keys())[0]]["fleet"]["list"][unittype] = startFleet[unittype]
            self.gameState[hsPos]["planets"][list(self.gameState[hsPos]["planets"].keys())[0]]["fleet"]["color"] = fleetColor

    def setSystemState(self, tileID, systemState):
        targetPos = self.getPosFromTileNum(tileID)
        self.gameState[targetPos] = deepcopy(self.gameState[targetPos], systemState)

    def getSystemState(self, tileID):
        targetPos = self.getPosFromTileNum(tileID)
        return self.gameState[targetPos]

    def updateTeamMaps(self):
        generateMap(self)
        self.darkenFrogOfWar(forceRegen=True)

    def getGameState(self):
        return self.gameState

    def setGameState(self, gamestate):
        self.gameState = gamestate

    def init(self):
        self.autoFillWormholes()
        self.populateEmptySystems()
        self.addStartingUnits()

        if not(len(self.gameState["visibility"].keys()) > 0):
            for team in self.teams:
                self.gameState["visibility"][team.teamColor] = []
        if not(len(self.gameState["specialVis"].keys()) > 0):
            for team in self.teams:
                self.gameState["specialVis"][team.teamColor] = []

        self.updateTeamMaps()
        self.generateTeamMaps()

    def initEmpty(self):
        self.autoFillWormholes()
        self.populateEmptySystems()

        if not(len(self.gameState["visibility"].keys()) > 0):
            for team in self.teams:
                self.gameState["visibility"][team.teamColor] = []
        if not(len(self.gameState["specialVis"].keys()) > 0):
            for team in self.teams:
                self.gameState["specialVis"][team.teamColor] = []

        self.updateTeamMaps()

            

class Team():
    def __init__(self, teamName, teamFaction, teamColor):
        self.name = teamName
        self.faction = teamFaction
        self.stats = defaultStats
        self.teamColor = teamColor
        self.adjustStatsForColor()
        self.initFactionStats()

    def initStats(self, statsArray):
        self.stats = statsArray

    def initFactionStats(self):
        faction = self.faction
        if(faction in factionInfo.keys()):
            factionStats = factionInfo[faction]

            for stat in factionStats.keys():
                tstat = self.getStat(stat)
                ttype = type(tstat)
                if ttype is int or ttype is str:
                    tstat = factionStats[stat]
                elif ttype is list:
                    tstat.extend(factionStats[stat])
                elif ttype is dict:
                    deepcopy(tstat, factionStats[stat])
                self.setStat(stat, tstat)

    def setStat(self, statKey, statValue):
        self.stats[statKey] = statValue

    def getStat(self, statKey):
        return self.stats[statKey]

    def adjustStatsForColor(self):
        for note in promNotes:
            self.stats["promissoryNotes"].append(self.teamColor + " " + note)

    def adjReinforcements(self, adjList):
        rein = self.stats["reinforcements"].copy()
        error = {}

        for adj in adjList.keys():
            if(adj == "units"):
                unitList = adjList["units"]["list"]
                reinList = rein["units"]["list"]
                for unit in unitList.keys():
                    compare = reinList[unit] - uniList[unit]
                    if compare < 0:
                        error[unit] = {"want" : unitList[unit], "have" : reinList[unit]}
                    else:
                        reinList[unit] = compare

                rein["units"]["list"] = reinList
            else:
                compare = rein[adj] - adjList[adj]
                if compare < 0:
                    error[adj] = {"want" : adjList[adj], "have" : rein[adj]}
                else:
                    rein[adj] = compare

        if len(error) < 1:
            self.stats["reinforcements"] = rein

        return error

    def adjUnits(self, fleet):
        adjList = {}
        adjList["units"] = fleet
        return self.adjReinforcements(adjList)

    def adjTokens(self, numCC = 0, numCT = 0):
        adjList = {}
        adjList["commandtokens"] = numCC
        adjList["controltokens"] = numCT
        return self.adjReinforcements(adjList)


def deepcopy(outDict, inDict):
    for inkey in inDict.keys():
        if type(inDict[inkey]) is dict:
            if not(inkey in outDict.keys()):
                outDict[inkey] = {}
            outDict[inkey] = deepcopy(outDict[inkey], inDict[inkey])
        elif type(inDict[inkey]) is list:
            if not(inkey in outDict.keys()):
                outDict[inkey] = []
            outDict[inkey] = inDict[inkey]
        else:
            outDict[inkey] = inDict[inkey]

    return outDict

def isMapFileEmpty():
    pickleFile = mapsFile

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            if len(pickle.load(f)) > 0:
                return False
    return True

def readMapData(gameName):
    read = {}
    pickleFile = mapsFile

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)

    return read[gameName]

def writeMapData(gameFrog):
    read = {}
    pickleFile = mapsFile
    gameName = gameFrog.gameName

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)

    read[gameName] = gameFrog

    with open(pickleFile, 'wb') as f:
        pickle.dump(read, f, pickle.HIGHEST_PROTOCOL)

## DANGER FUNCTION
def clearMapDataPickle():
    read = {}
    pickleFile = mapsFile
    with open(pickleFile, 'wb') as f:
        pickle.dump(read, f, pickle.HIGHEST_PROTOCOL)

def isTeamFileEmpty():
    pickleFile = teamsFile

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            if len(pickle.load(f)) > 0:
                return False
    return True

def readTeamData(gameName):
    read = {}
    pickleFile = teamsFile

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)

    if not(gameName in read.keys()):
        read[gameName] = {}
    return read[gameName]

def writeTeamData(team):
    read = {}
    pickleFile = teamsFile
    gameName = team['gamename']
    teamName = team['teamname']

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)

    if not(gameName in read.keys()):
        read[gameName] = {}
    read[gameName][teamName] = team

    with open(pickleFile, 'wb') as f:
        pickle.dump(read, f, pickle.HIGHEST_PROTOCOL)

def deleteTeam(team):
    read = {}
    pickleFile = teamsFile
    gameName = team['gamename']
    teamName = team['teamname']

    if exists(pickleFile) and os.path.getsize(pickleFile) > 0:
        with open(pickleFile, 'rb') as f:
            read = pickle.load(f)

    if not(gameName in read.keys()):
        read[gameName] = {}
    if read[gameName][teamName]:
        del read[gameName][teamName]

    with open(pickleFile, 'wb') as f:
        pickle.dump(read, f, pickle.HIGHEST_PROTOCOL)

## DANGER FUNCTION
def clearTeamDataPickle():
    read = {}
    pickleFile = teamsFile
    with open(pickleFile, 'wb') as f:
        pickle.dump(read, f, pickle.HIGHEST_PROTOCOL)

def initGameMap(gameName, mapObj, teams, gameState = {}):
    if(len(gameState) > 0):
        gameFrog = frogMap(gameName, mapObj, teams, gameState)
    else:
        gameFrog = frogMap(gameName, mapObj, teams)
    writeMapData(gameFrog)
    return gameFrog

def saveGame(gameName, gameState):
    preGameFrog = readMapData(gameName)
    preGameFrog.gameState = gameState
    writeMapData(preGameFrog)

def inputToState(systemString):
    outSystem = {"fleet" : {}}
    outSystem["fleet"] = deepcopy(outSystem["fleet"], emptyFleet)
    items = systemString.split("|")

    for i in items:
        kvpairs = i.split(":")
        if kvpairs[0] == "spaceTokens":
            outSystem["spaceTokens"] = []
            for v in range(1,len(kvpairs)):
                outSystem["spaceTokens"].append(v)

async def testDarkMap(mapObj, factions, gameName):
    teams = []
    colors = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "black", "white"]
    random.shuffle(colors)

    for facName in factions:
        t = Team(facName, facName, colors.pop())
        teams.append(t)

    gameFrog = frogMap(gameName, mapObj, teams)

    writeMapData(gameFrog)

    gameFrog.init()

    writeMapData(gameFrog)

    return gameFrog

## Gamestate must include a systemsWithWormholes field that keeps a current record of all systems on the game board with wormholes (by position)