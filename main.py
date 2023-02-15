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

    files = []
    servers = dict()

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

@bot.command()
async def addPlayer(ctx):
    pass

@bot.command()
async def shutdown(ctx):
    await ctx.send("Shutting down")
    await bot.close()

def main(argv):
    if len(argv) > 1:
        pass
    try:
        # (1/4) Read JSON files
        try:
            files = data.loadServers(os.path.join(config.wd, config.jsonDir))
        except Exception as e:
            print(e)

        # (2/4) Convert the read JSON files to Servers. Delete files to save memory
        try:
            servers = data.convertFilesToObjects(files)
            del files
        except Exception as e:
            print(e)

        # (3/4) Run the bot
        try:
            from auth import token
            bot.run(token)
        except Exception as e:
            print(e)

        # (4/4) Write servers to JSON files
        try:
            data.saveAllServers(servers)
        except Exception as e:
            print(e)
        print("Closing...")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv[1:])