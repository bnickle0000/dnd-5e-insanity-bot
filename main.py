try:
    # User implemented
    import bot
    import data
    import config
    # Discord
    import discord
    from discord.ext import commands
    # Python
    import asyncio
    import json
    import os
    from random import randint
    import sys
except Exception as e:
    print(e)
    intents = None
    bot = None
else:
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="-", description=config.description, intents=intents)

    bot.files = []
    bot.servers = dict()
    bot.insanities = dict()

    """
    # Old pseudocode, just save it to be safe :)
    for file in wd/data:
        if file is json and "insanity-data" in file's name:
            read server & players from file
            server = new Server()
            for player in file:
                p = new Player()
                server.add(p)
            datastore.add(server)
    done
    """        

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

"""
Repeat a message back at the user who said it, mentioning them by their
server-specific nickname, or if they don't have one, their "raw" username
"""
@bot.command()
async def parrot(ctx, *message):
    # reply = " ".join(message)
    # print(reply)
    # await ctx.send(f"{ctx.author.display_name} said \"{reply}\"")
    print(ctx.message.mentions)
    print(ctx.message.content)
    await ctx.send(f"{ctx.author.display_name} said \"{ctx.message.content}\"")

@bot.command()
async def shoot(ctx):
    await ctx.send("bro w-***AGGGGGGAGGGAGAGAGAGAGH [GETS SHOT]***")

# Syntax: -addplayer [player1] [player2] ... [playerN]
@bot.command()
async def addplayer(ctx, *message):
    reply = ""
    server = getServer(str(ctx.guild.id), bot.servers)
    if server != None:
        count = 0
        for mention in ctx.message.mentions:
            print(mention)
            try:
                print(f"Adding player `{str(mention.id)}` to `{ctx.guild.name}`:")
                player = data.Player(str(mention.id))
                server.addPlayer(player)
            except Exception as e:
                print(f"Exception while adding player `{mention}` to `{ctx.guild.name}`:")
                print(e)
            else:
                count += 1
                curr = await bot.fetch_user(mention.id)
                await ctx.send(f"Added player {curr.mention} !")
        reply = f"Added `{count}` players in server `{ctx.guild.name}`!"
    else:
        reply = f"Could not find server `{ctx.guild.name}` in registered servers"
    await ctx.send(reply)

# Syntax: -addeffect [type] [player1] [player2] ... [playerN]
@bot.command()
async def addeffect(ctx, *message):
    try:
        args = ctx.message.content.split(" ")
        effectType = args[1]
    except IndexError as e:
        effectType = "short"
    except Exception as e:
        print(f"Exception while setting effect type ('{effectType}'):")
        print(f"\t{ctx.message.content}")
        print(e)

    effectSides = {
        "short":10,
        "long":10,
        "indef":1,
        "perm":1
    }

    effectMods = {
        "short":0.0,
        "long":0.0,
        "indef":999.0,
        "perm":999.0
    }

    effectMultipliers = {
        "short":1,
        "long":1,
        "indef":1,
        "perm":1
    }

    for p in ctx.message.mentions:
        print(f"Getting random effect for player {p.id}...")
        # Pull random insanity effect to give to the player
        effect = pullIsanity(effectType)
        print(f"Got effect {effect} for player {p.id}.")
        duration = 0.0

        player = getPlayerFromServer(str(p.id), str(ctx.guild.id), bot.servers)
        try:
            if player != None:
                print(f"Configuring effect {effect['id']} for {player.pid}...")
                sides = effectSides[effectType]
                mod = effectMods[effectType]
                multiplier = effectMultipliers[effectType]
                duration = d(sides, mod) * multiplier

                print(f"Adding effect {effect['id']} to {player.pid}...")
                player.addEffect(effectType, effect, duration)

                print(f"Fetching user {p.id}...")
                mentionable = await bot.fetch_user(p.id)
                
                print(f"Player {player.pid} now has effect {effect['id']}")
                await ctx.send(f"{mentionable.mention} now has effect `{effect['id']}`: ```{effect['description']}``` for `{duration}` hours!")
        except Exception as e:
            print("Exception while applying insanity:")
            print(e)
  
# Helper    
def pullIsanity(effectType:str) -> dict:
    # If loading insanities didn't work the first time, try again
    # Isn't that the definition of insanity, though?
    if len(bot.insanities) == 0:
        bot.insanities = data.loadInsanities(os.path.join(config.wd, config.insanitiesFileName))
    
    # Cut the possible insanities (possibilities) down to only include ones applicable to the effectType
    try:
        possibilities = bot.insanities.keys()
        # If it's permanent insanity, exclude short-term insanities. Not fun gameplay.
        # Anything else is fair game.
        if effectType.lower() == "perm":
            possibilities = [bot.insanities[p] for p in possibilities if "short" not in p]
        
        # If effectType == short, then only keys containing "short" or "any" are included
        # Same logic for "long", "indef"
        else:
            possibilities = [bot.insanities[p] for p in possibilities if config.ANYPREFIX in p or effectType.lower() in p]
    except Exception as e:
        print("Exception while pulling insanity:")
        print(e)
    else:
        length = len(possibilities)
        if length > 0:
            return possibilities[d(length, -1)]
        return {"id":None, "description":None}
  
# Helper   
def d(sides:int, mod:int=0) -> int:
    return randint(1, sides) + mod

@bot.event
async def on_guild_join(guild):
    try:
        newServer = data.Server(str(guild.id), players=dict())
    except Exception as e:
        print(f"Exception while joining guild {guild.id}")
        print(e)

# Syntax: -setdm
@bot.command()
async def setdm(ctx, *message):
    print(ctx.message.mentions)
    reply = ""
    print(f"Setting {ctx.author.id} as DM for server {ctx.guild.id}")
    server = None
    server = getServer(str(ctx.guild.id), bot.servers)
    if server != None:
        success = server.setDMID(str(ctx.author.id))
        if success:
            reply = f"Set `{ctx.author.display_name}` as DM for server `{ctx.guild.name}` !"
        else:
            # Reference here for mentioning user by id
            dm = await bot.fetch_user(int(server.getDMID().getValue()))
            # reply = f"Could not set new DM for server `{ctx.guild.name}`; DM is `{server.getDMID().getValue()}` !"
            reply = f"Could not set new DM for server `{ctx.guild.name}`; DM is {dm.mention} !"
        print(reply)
        await ctx.send(reply)
    else:
        await ctx.send(f"Could not find server `{ctx.guild.name}` in registered servers")

# Helper 
def isDm(pid:str, server:data.Server) -> bool:
    print(f"Is {pid} the DM of server {server.sid} ?")
    print(f"Is {pid} == {server.getDMID().getValue()} ?")
    return pid == server.getDMID().getValue()

# Helper 
def getServer(id:str, servers:dict) -> data.Server:
    result = None
    try:
        print(servers.keys())
        result = servers[id]
        print(f"Found server {id} in servers")
    except KeyError as e:
        print(f"Could not find server {id} in servers")
        return None
    return result

# Syntax: -listeffects [OPTIONAL:-a] [player1] [player2] ... [playerN]
@bot.command()
async def listeffects(ctx, *message):
    all = False
    try:
        args = ctx.message.content.split(" ")
        all = args[1].lower() == "-a"
    except IndexError as e:
        print(f"IndexError while setting 'all':")
        print(f"\t{ctx.message.content}")
        print(e)
    except Exception as e:
        print(f"Exception while setting 'all':")
        print(f"\t{ctx.message.content}")
        print(e)

    try:
        print(ctx)
        print(ctx.message)
        print(ctx.message.content.split(" "))
        print(ctx.message.mentions)
        # for p in ctx.message.content.split(" ")[1:]:
        print("Servers:", bot.servers.keys())
        for p in ctx.message.mentions:
            print(f"Listing effects for player {p.id}...")
            # player = await getPlayerFromServer(p, "0", bot.servers)
            # TODO: update to accommodate using actual discord IDs, server IDs
            player = getPlayerFromServer(str(p.id), str(ctx.guild.id), bot.servers)
            try:
                print(f"Fetching discord usesr {p.id}...")
                curr = await bot.fetch_user(p.id)
            except Exception as e:
                print(f"Exception while fetching discord user from id {p.id}:")
                print(e)
            else:
                try:
                    if player != None:
                        print(f"Player: {player} ({player.pid}) {len(player.allEffects.keys())} effects")
                        # effects = await printPlayerEffects(player)
                        effects = printPlayerEffects(player, curr.mention, all)
                        print("Effects:", effects)
                        for effect in effects:
                            try:
                                await ctx.send(f"{effect}")
                            except Exception as e:
                                print(f"Exception while sending {player.pid}'s effect {effect[player.EID]}:")
                                print(e)
                    else:
                        await ctx.send(f"Foundn't player {curr.mention} in server `{ctx.guild.name}`")
                except Exception as e:
                    print(f"Exception while formatting & sending player {player.pid}'s effects:")
                    print(e)
    except Exception as e:
        print(e)
        await ctx.send(f"Exception raised see terminal")
    
# Helper 
def getPlayerFromServer(pid:str, sid:str, servers:dict()) -> data.Player:
    # TODO: update to accommodate using actual discord IDs ?
    try:
        print(f"Getting player '{pid}' from server '{sid}'...")
        server = servers[sid]
        player = server.players[pid]
        print(f"Found player '{pid}' in server '{sid}'!")
        return player
    except KeyError as e:
        print(f"Foundn't player '{pid}' in server '{sid}'!")
        print(e)
    except Exception as e:
        print(e)
    return None

# Helper 
def printPlayerEffects(player:data.Player, mention, all:bool=False) -> list:
    # Return a human-readable list of effects the player is experiencing,
    # resembling something like the following:
    # {Player} has the effect:
    # > {description}
    # > Type: {type}
    # > Status: {status}
    # > Max duration: {duration}
    # > Hours remaining: {hoursRemaining}
    print(f"Gathering {player.pid}'s effects...")
    if not player.hasEffects():
        lines = [f"{mention} does not have any effects!"]
    else:
        print(f"""{player.allEffects["short"]}
        {player.allEffects["long"]}
        {player.allEffects["indef"]}
        {player.allEffects["perm"]}
        """)
        # lines = [f"{mention} has the following effect(s):"]
        lines = []
        fx = []
        for effectType in player.allEffects.keys():
            effectSet = player.allEffects[effectType]
            fx = fx + [effectSet[key] for key in effectSet.keys()]
        print(f"fx: {fx}")
        for effect in fx:
            print(effect)
            print("Datatype of effect:", type(effect))
            try:
                message = "message"
                description = "desc"
                # typE = "type"
                eid = "eid"
                status = "stat"
                duration = "dura"
                hoursRemaining = "hour"
                try:
                    description = effect[player.DESC]
                    # typE = effect[player.TYPE]
                    eid = effect[player.EID]
                    status = effect[player.STAT]
                    duration = effect[player.DURA]
                    hoursRemaining = effect[player.HOUR]
                    minutes = int(hoursRemaining * 60)
                except KeyError as e:
                    print(f"KeyError while accessing effect dict:")
                    print(e)
                except Exception as e:
                    print(f"Exception while accessing effect dict:")
                    print(e)
                
                # If all is True, print all effects
                # Otherwise, check that effects are active before printing
                if all or (status) == config.E_ACTIVE:
                    print(description)
                    # print(typE)
                    print(eid)
                    print(status)
                    print(duration)
                    print(hoursRemaining)
                    message = "\n".join([f"{mention} has the effect: ",
                                        f"```{description}```",
                                        f"> ID: `{eid}`",
                                        #  f"> Type: {typE}",
                                        f"> Status: `{status}`",
                                        f"> Max duration: `{duration}`",
                                        f"> Hours remaining: `{hoursRemaining}` (about `{minutes}` minutes)"])
                    print(message)
            except Exception as e:
                print(f"Exception while gathering {player.pid}'s effects:")
                print(e)
            else:
                if message != 'message':
                    lines.append(message)
            finally:
                print(len(lines), end=", ")
                lines.append("Done")
        print(f"\nReturning {player.pid}'s effects...")
    return lines

# Syntax: -cureeffect @player any-00
# Future syntax: -cureeffect * any-00
# Future syntax: -cureeffect @player *
@bot.command()
async def cureeffect(ctx, *message):
    try:
        args = ctx.message.content.split(" ")
        while "" in args:
            args.remove("")
        eid = args[2]
    except IndexError as e:
        print(f"IndexError while getting eid from message '{ctx.message.content}':")
        print(e)
        return
    except Exception as e:
        print(f"Exception while getting eid from message '{ctx.message.content}':")
        print(e)
        return
    else:
        for p in ctx.message.mentions:
            print(f"Curing eid {eid} for player {p.id}...")
            # player = await getPlayerFromServer(p, "0", bot.servers)
            # TODO: update to accommodate using actual discord IDs, server IDs
            player = getPlayerFromServer(str(p.id), str(ctx.guild.id), bot.servers)
            try:
                print(f"Fetching discord user {p.id}...")
                curr = await bot.fetch_user(p.id)
            except Exception as e:
                print(f"Exception while fetching discord user from id {p.id}:")
                print(e)
            else:
                try:
                    if player != None:
                        print(f"Player: {player} ({player.pid}) {len(player.allEffects.keys())} effects")
                        try:
                            print(f"Curing {eid} for player {player.pid}...")
                            player.cureEffect(eid)
                        except Exception as e:
                            print(f"Exception while curing {player.pid}'s effect {eid}:")
                            print(e)
                        else:
                            try:
                                await ctx.send(f"Cured effect `{eid}` for {curr.mention}!")
                            except Exception as e:
                                print(f"Exception while sending {player.pid}'s effect {eid}:")
                                print(e)
                    else:
                        await ctx.send(f"Foundn't player {curr.mention} in server `{ctx.guild.name}`")
                        return
                except Exception as e:
                    print(f"Misc exception while curing {player.pid}'s effect {eid}:")
                    print(e)

# Syntax: -decrementeffects [amount] [OPTIONAL:minutes]
# Syntax: -decrementeffects 1           # Decrements by 1 hour
# Syntax: -decrementeffects 1 -min      # Decrements by 1 minute
# Syntax: -decrementeffects 60 -minutes # Decrements by 1 hour
@bot.command()
async def decrementeffects(ctx, *message):
    amount = 0.0
    minutes = False
    try:
        args = ctx.message.content.split(" ")
        while "" in args:
            args.remove("")
        amount = float(args[1])
        minutes = "-m" in ctx.message.content.split(" ")
        server = getServer(str(ctx.guild.id), bot.servers)
        if server != None:
            print(f"decrementing effects with args [{amount}, '{ctx.message.content}', {minutes}] in {ctx.guild.name}...")
            # server.decrementPlayerEffects(amount, minutes)
            server.decrementPlayerEffects(amount, minutes)
            if minutes:
                await ctx.send(f"{amount} minutes have now passed!")
            else:
                await ctx.send(f"{amount} hours have now passed!")
        else:
            await ctx.send(f"Could not find `{ctx.guild.name}` in registered servers")
    except Exception as e:
        print(f"Exception while decrementing effects with args [{amount}, '{ctx.message.content}', {minutes}] in {ctx.guild.name}:")
        print(e)

@bot.command()
async def shutdown(ctx):
    await ctx.send("Shutting down")
    await bot.close()

def main(argv):
    if len(argv) > 1:
        pass
    try:
        # TODO: move try/excepts out of main, except (4/5)
        # (1/5) Read JSON files
        bot.files = data.loadServers(os.path.join(config.wd, config.jsonDir))

        # (2/5) Convert the read JSON files to Servers. Delete files to save memory
        bot.servers = data.convertFilesToObjects(bot.files)
        try:
            del bot.files
        except Exception as e:
            print(e)
        
        # (3/5) Load insanities from JSON
        bot.insanities = data.loadInsanities(os.path.join(config.wd, config.insanitiesFileName))

        # (4/5) Run the bot
        try:
            from auth import token
            bot.run(token)
        except Exception as e:
            print(e)

        # (5/5) Write servers to JSON files
        data.saveAllServers(bot.servers)
        print("Closing...")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv[1:])
    print("Closed")