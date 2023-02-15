import config
import json
import os

"""
json documentation: https://docs.python.org/3/library/json.html
"""

class DMID:
    def __init__(self, value:str = None):
        self.__value = None
        self.setValue(value)
    def getValue(self):
        return self.__value
    def setValue(self, value:str = None):
        if self.__value == None:
            self.__value = value

"""# dmid1 = DMID("id-01")
# # dmid1.shared = "id-01"
# print(dmid1.value)
# dmid1 = DMID("id-02")
# print(dmid1.value)"""

"""
Represents the D&D player. Allows for a player to be in many servers
"""
class Player:
    def __init__(self, pid:str,
                 short:dict={},
                 long:dict={},
                 indef:dict={},
                 perm:dict={}
                 ):
        self.setPid(pid)
        # self.effectTypes = "short long indef perm".split(" ")
        self.short = short
        self.long = long
        self.indef = indef
        self.perm = perm
        self.allEffects = dict()
        self.allEffects["short"] = self.short
        self.allEffects["long"] = self.long
        self.allEffects["indef"] = self.indef
        self.allEffects["perm"] = self.perm
        self.NODECREMENTS = ("indef", "perm")
        # Constants for in-class dictionary actions
        self.ABBR = "abbrev."
        self.CUTOFF = 24
        self.DESC = "description"
        self.DURA = "duration"
        self.HOUR = "hoursRemaining"
        self.STAT = "status"
        self.PID = "pid"
        self.TYPE = "type"

    def setPid(self, pid:str):
        self.pid = pid
    def getPid(self):
        return self.pid
    def addEffect(self,
                  effectType:str, # Type of effect duration (short, long, etc)
                  description:str, # Description of the effect
                  duration:float # Duration of effect in hours
                  ):
        if effectType not in self.allEffects.keys():
            return 1
        type = self.allEffects[effectType]

        """Uniquely identifying effects by their description
        This will update duration and hoursRemaining
        """
        largerDuration = duration
        largerRemaining = duration
        if description in type.keys():
            if type[description][self.DURA] > largerDuration:
                largerDuration = type[self.DURA]
            
            if type[description][self.HOUR] > largerRemaining:
                largerRemaining = type[self.HOUR]
        else:
            type[description] = dict()
        try:
            type[description][self.ABBR] = description[:24]
        except IndexError as ie:
            print(ie)
            type[description][self.ABBR] = ""
        except Exception as e:
            print(e)
            type[description][self.ABBR] = "ERROR"
        type[description][self.DESC] = description
        type[description][self.DURA] = largerDuration
        type[description][self.HOUR] = largerRemaining
        type[description][self.STAT] = config.effectStatus[config.E_ACTIVE]
        type[description][self.TYPE] = effectType
        return 0
    def cureEffect(self,
                   description:str # May not uniquely id effect instances, but good enough
                   ):
        for effectType in self.allEffects:
            for key in effectType.keys():
                if key != "perm":
                    curr = effectType[key]
                    if curr[self.DESC] == description:
                        curr[self.HOUR] = 0.0
                        curr[self.STAT] = config.effectStatus[config.E_CURED]
        return 0
    def decrementEffects(self,
                         duration:float # Number of hours to decrement by
                         ):
        for effectType in self.allEffects:
            if effectType not in self.NODECREMENTS:
                effectSet = self.allEffects[effectType]
                for key in effectSet.keys():
                    # if key not in self.NODECREMENTS:
                    curr = effectSet[key]
                    curr[self.HOUR] -= duration
                    if curr[self.HOUR] <= 0.0:
                        curr[self.STAT] = config.effectStatus[config.E_ENDED]
    def listEffects(self, onlyActive:bool=False):
        result = dict()
        for effectType in self.allEffects.keys():
            effectSet = self.allEffects[effectType]
            for key in effectSet.keys():
                curr = effectSet[key]
                if onlyActive:
                    if curr[self.STAT] == config.E_ACTIVE:
                        result[curr[self.DESC]] = curr
                else:
                    result[curr[self.DESC]] = curr
        return result
    # Return a human-readable list of effects the player is experiencing
    # Should look something like
    """
    {Player} has the effect:
    > {description}
    > Type: {type}
    > Status: {status}
    > Max duration: {duration}
    > Hours remaining: {hoursRemaining}
    """
    def returnPrintable(self, name):
        lines = []
        fx = []
        for effectType in self.allEffects.keys():
            effectSet = self.allEffects[effectType]
            fx = fx + [effectSet[key] for key in effectSet.keys()]
        for effect in fx:
            message = "\n".join([f"{name} has the following effect:",
                                 f"--------------------------------",
                                 f"> {effect[self.DESC]}",
                                 f"--------------------------------",
                                 f"> Type: {effect[self.TYPE]}",
                                 f"> Status: {effect[self.STAT]}",
                                 f"> Max duration: {effect[self.DURA]}",
                                 f"> Hours remaining: {effect[self.HOUR]}"])
            lines.append(message)

        return lines
    def toJson(self):
        result = self.allEffects
        result[self.PID] = self.pid
        return result

"""
Represents the whole ass discord server.
"""
class Server:
    def __init__(self, sid:str,
                 players:dict={},
                 dmid:str=""
                ):
        self.sid = sid
        self.players = players
        self.dmid = DMID(dmid)
        # Constants for in-class dictionary actions
        self.SID = "sid"
        self.PLAY = "players"
        self.DMID = "dmid"
    def addPlayer(self, player:Player):
        pid = player.getPid()
        self.players[pid] = player
    def getDMID(self) -> str:
        return self.dmid.getValue()
    def cureEffect(self,pid:str,effect:str):
        player = self.players[pid]
        player.cureEffect(effect)
    def decrementEffects(self,
                         duration:float # Number of hours to decrement by
                         ):
        for pid in self.players.keys():
            curr = self.player[pid]
            curr.decrementEffects(duration)
        pass
    def toJson(self):
        result = dict()
        result[self.SID] = self.sid

        """
        WEIRD BUG I have NO idea why the commented out line below doesn't work
        but then the one directly below it 
        """
        # result[self.DMID] = self.getDMID() # DOESN'T WORK?
        result[self.DMID] = self.dmid.getValue().getValue() # DOES WORK?! HOW?!
        
        result[self.PLAY] = dict()
        for pid in self.players.keys():
            result[self.PLAY][pid] = self.players[pid].toJson()
        print(result)
        return result

"""daeolt = Player("daeolt")
daeolt.addEffect("short", "You laugh uncontrollably", 8.0)
daeolt.addEffect("short", "You laugh uncontrollably", 8.0)
daeolt.addEffect("short", "You laugh uncontrollably", 13.13)
daeolt.addEffect("long", "You sneeze uncontrollably", 16.0)
daeolt.addEffect("indef", "You cough uncontrollably", 24.0)
daeolt.addEffect("perm", "You shart uncontrollably", 32.0)
daeolt.decrementEffects(32.0)
# print(daeolt.listEffects())

debug = Server("0", dict(), "brad")
debug.addPlayer(daeolt)

data = dict()
data[debug.sid] = debug
# data["server"] = dict()
# data["server"]["sid"] = 0
# data["server"]["players"] = dict()
# data["server"]["players"]["daeolt"] = daeolt.toJson()"""

"""data = {
    "server":{
        "serverId":0,
        "users":{
            # dev will use nicknames for simplicity
            # prod will use actual user id assigned by discord; unique id
            "brad":{ 
                "shortTerm":[
                    {
                        "id":0,
                        "effect":"description of effect",
                        "hoursRemaining":24
                    },
                    {
                        "id":1,
                        "effect":"You think your nipples are speaking to you",
                        "hoursRemaining":16
                    },
                ],
                "longTerm":[
                ],
                "indefinite":[
                ],
                "permanent":[
                ],
            }
        }
    }
}"""

# (1/4) Read JSON files
def loadServers(basePath:str):
    files = []
    # servers = dict()
    # basePath = os.path.join(config.wd, config.jsonDir)
    with os.scandir(basePath) as iter:
        for file in iter:
            fileIsValid = False
            if ".json" in file.name and "insanity-data" in file.name:
                with open(file, config.readM) as infile:
                    files.append(json.load(infile))
    return files
    # return servers

# (2/4) Convert the read JSON files to Servers
def convertFilesToObjects(files:list):
    servers = dict()
    for i in range(0, len(files)):
        try:
            p = files[i]["players"]
            players = dict()
            for key in p.keys():
                curr = p[key]
                temp = Player(key,
                            curr["short"],
                            curr["long"],
                            curr["indef"],
                            curr["perm"]
                            )
                curr = temp
                players[key] = curr
            # files[i] = data.Server(files[i]["sid"], players, files[i]["dmid"])
            sid = files[i]["sid"]
            print(f"DMID: {files[i]['dmid']}")
            servers[sid] = Server(files[i]["sid"], players, DMID(files[i]["dmid"]))
        except Exception as e:
            print(e)
    return servers

# discord.py does all the heavy lifting in step (3/4) in main

# (4/4) Helper for saveAllServers; also a good option for incremental saving later
def saveServer(sid:str, server:Server):
    try:
        print(f"Saving {sid}-{config.jsonFile} ...")
        with open(os.path.join(config.wd, config.jsonDir, f"{sid}-{config.jsonFile}"), config.writeM) as outfile:
            # server = data[sid] # Deprecated
            jsonData = json.dumps(server.toJson(), indent=2)
            outfile.write(jsonData)
        print(f"Saved {sid}-{config.jsonFile} !")
    except Exception as e:
            print(f"Exception occurred while writing to {sid}-{config.jsonFile} !")
            print(e)
    return

# (4/4) Write servers to JSON files
def saveAllServers(data:dict):
    for sid in data.keys():
        """try:"""
        print(sid)
        if sid != None:
            saveServer(sid, data[sid])
            """Deprecated
            # print(f"Saving {sid}-{config.jsonFile} ...")
            # with open(os.path.join(config.wd, config.jsonDir, f"{sid}-{config.jsonFile}"), config.writeM) as outfile:
            #     server = data[sid]
            #     jsonData = json.dumps(server.toJson(), indent=2)
            #     outfile.write(jsonData)
            # print(f"Saved {sid}-{config.jsonFile} !")"""
        """else:
            raise Exception(f"Could not get server id for server {sid}")"""
    print(f"Done")
    return