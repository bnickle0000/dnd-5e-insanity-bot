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
        # self.short = short
        # self.long = long
        # self.indef = indef
        # self.perm = perm
        self.allEffects = dict()
        self.allEffects["short"] = short
        self.allEffects["long"] = long
        self.allEffects["indef"] = indef
        self.allEffects["perm"] = perm
        self.NODECREMENTS = ("indef", "perm")
        # Constants for in-class dictionary actions
        self.ABBR = "abbrev."
        self.CUTOFF = 24
        self.DESC = "description"
        self.DURA = "duration"
        self.EID = "eid"
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
                  effect:dict, # Resembles {"id":"type-##", "description":"lorem ipsum ..."}
                  duration:float # Duration of effect in hours
                  ) -> int: # Returns 0 if no errors, 1 if error(s)
        # Return if an invalid effect type was given
        if effectType not in self.allEffects.keys():
            return 1
        # Otherwise, grab the dict for that effect type
        effectSet = self.allEffects[effectType]

        """
        Used to uniquely identify effects by their description;
        Now uniquely identifying effects by their key in the insanities
        JSON file.

        If the key is already in the effect set, then update the effect
        with the larger duration & time remaining. The effect will also
        be turned active again, automatically.
        """
        largerDuration = duration
        largerRemaining = duration
        if effect['id'] in effectSet.keys():
            if effectSet[effect['id']][self.DURA] > largerDuration:
                largerDuration = effectSet[self.DURA]
            
            if effectSet[effect['id']][self.HOUR] > largerRemaining:
                largerRemaining = effectSet[self.HOUR]
        else:
            effectSet[effect['id']] = dict()
        
        """
        TODO: re-examine whether this try/except block is needed.
        Haven't used abbrev. so far!
        """
        try:
            effectSet[effect['id']][self.ABBR] = effect['description'][:24] + "..."
        except IndexError as ie:
            print(ie)
            effectSet[effect['id']][self.ABBR] = ""
        except Exception as e:
            print(e)
            effectSet[effect['id']][self.ABBR] = "ERROR"
        
        # Update remaining fields for the insanity
        effectSet[effect['id']][self.EID] = effect['id']
        effectSet[effect['id']][self.DESC] = effect['description']
        effectSet[effect['id']][self.DURA] = largerDuration
        effectSet[effect['id']][self.HOUR] = largerRemaining
        effectSet[effect['id']][self.STAT] = config.effectStatus[config.E_ACTIVE]
        effectSet[effect['id']][self.TYPE] = effectType
        return 0
    def cureEffect(self,
                   eid:str # ID of effect
                   ):
        cured = 1
        for effectType in self.allEffects:
            """
            Search for the effect & cure all instances of it.
            Doesn't matter if the effect has multiple instances with
            differing durations.
            """
            # for key in effectType.keys():
            #     if key != "perm":
            #         curr = effectType[key]
            #         if curr[self.DESC] == description:
            #             curr[self.HOUR] = 0.0
            #             curr[self.STAT] = config.effectStatus[config.E_CURED]
            if effectType != "perm":
                try:
                    effect = self.allEffects[effectType][eid]
                except KeyError as e:
                    print(f"KeyError: No {effectType} effect {eid} to cure for player {self.pid}")
                except Exception as e:
                    print(f"Exception during cureEffect({eid}) for player {self.pid}")
                    print(e)
                else:
                    print(f"Curing {effectType} effect {eid} for player {self.pid}")
                    effect[self.STAT] = config.E_CURED
                    effect[self.HOUR] = 0.0
                    cured = 0
        return cured
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
    def hasEffects(self):
        count = 0
        for effectType in self.allEffects.keys():
            count += len(self.allEffects[effectType].keys())
        return count > 0
    def listEffects(self, onlyActive:bool=False):
        result = dict()
        for effectType in self.allEffects.keys():
            effectSet = self.allEffects[effectType]
            for key in effectSet.keys():
                curr = effectSet[key]
                if onlyActive:
                    if curr[self.STAT] == config.E_ACTIVE:
                        result[key] = curr
                else:
                    result[key] = curr
        return result
    
    def toJson(self):
        result = self.allEffects
        result[self.PID] = self.pid
        return result

"""
Represents the whole ass discord server.
"""
class Server:
    def __init__(self, sid:str, players:dict={}, dmid:str=""):
        self.sid = sid
        self.players = players
        self.__dmid = None
        if dmid != "":
            self.setDMID(dmid)
        # Constants for in-class dictionary actions
        self.SID = "sid"
        self.PLAY = "players"
        self.DMID = "dmid"
    def addPlayer(self, player:Player):
        pid = player.getPid()
        self.players[pid] = player
    def getDMID(self) -> str:
        return self.__dmid.getValue()
    def setDMID(self, value:str) -> bool:
        if value != "" and self.__dmid == None:
            self.__dmid = DMID(value)
            return True
        return False
    def cureEffect(self,pid:str,effect:str):
        player = self.players[pid]
        player.cureEffect(effect)
    def decrementPlayerEffects(self, duration:float, minutes:bool=False):
        """
        duration: Number of hours to decrement by
        minutes:  If True, decrements by minutes instead
        """
        if minutes:
            duration /= 60
        for pid in self.players.keys():
            curr = self.players[pid]
            curr.decrementEffects(duration)
    def toJson(self):
        result = dict()
        result[self.SID] = self.sid

        """
        WEIRD BUG I have NO idea why the commented out line below doesn't work
        but then the one directly below it 
        """
        # result[self.DMID] = self.getDMID() # DOESN'T WORK?
        result[self.DMID] = self.__dmid.getValue().getValue() # DOES WORK?! HOW?!
        
        result[self.PLAY] = dict()
        for pid in self.players.keys():
            result[self.PLAY][pid] = self.players[pid].toJson()
        print(result)
        return result

"""
daeolt = Player("daeolt")
daeolt.addEffect("short", "You laugh uncontrollably", 8.0)
daeolt.addEffect("short", "You laugh uncontrollably", 8.0)
daeolt.addEffect("short", "You laugh uncontrollably", 13.13)
daeolt.addEffect("long", "You sneeze uncontrollably", 16.0)
daeolt.addEffect("indef", "You cough uncontrollably", 24.0)
daeolt.addEffect("perm", "You shart uncontrollably", 32.0)
daeolt.decrementEffects(32.0)
for printable in daeolt.returnPrintable("daeolt"):
    print(printable)
# print(daeolt.listEffects())

debug = Server("0", dict(), "brad")
debug.addPlayer(daeolt)

data = dict()
data[debug.sid] = debug
# data["server"] = dict()
# data["server"]["sid"] = 0
# data["server"]["players"] = dict()
# data["server"]["players"]["daeolt"] = daeolt.toJson()
"""

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

# (1/5) Read JSON files
def loadServers(basePath:str):
    files = []
    try:
        # servers = dict()
        # basePath = os.path.join(config.wd, config.jsonDir)
        with os.scandir(basePath) as iter:
            for file in iter:
                fileIsValid = False
                if ".json" in file.name and "insanity-data" in file.name:
                    with open(file, config.readM) as infile:
                        files.append(json.load(infile))
    except Exception as e:
        print(f"Exception while loading server files:")
        print(e)
    finally:
        return files
        # return servers

# (2/5) Convert the read JSON files to Servers
def convertFilesToObjects(files:list):
    servers = dict()
    try:
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
                print(f"Server: {sid} DMID: {files[i]['dmid']}")
                servers[sid] = Server(files[i]["sid"], players, DMID(files[i]["dmid"]))
            except Exception as e:
                print(e)
    except Exception as e:
        print(f"Exception while converting file contents to objects:")
        print(e)
    finally:
        return servers

# (3/5) Load insanity effects (insanities) from JSON
def loadInsanities(filename:str) -> dict:
    results = []
    try:
        with open(filename, config.readM) as infile:
            results = json.load(infile)
    except Exception as e:
        print(f"Exception while loading insanities:")
        print(e)
    finally:
        return results

# discord.py does all the heavy lifting in step (4/5) in main

# (5/5) Helper for saveAllServers; also a good option for incremental saving later
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

# (5/5) Write servers to JSON files
def saveAllServers(data:dict):
    try:
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
    except Exception as e:
            print(f"Exception while saving all servers:")
            print(e)
    finally:
        return