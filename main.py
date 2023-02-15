try:
    # User implemented
    import auth
    import bot
    import config
    # Discord
    import discord
    from discord.ext import commands
    # Python
    import asyncio
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

"""
Repeat a message back at the user who said it, mentioning them by their
server-specific nickname, or if they don't have one, their "raw" username
"""
@bot.command()
async def parrot(ctx, *message):
    reply = " ".join(message)
    print(reply)
    await ctx.send(f"{ctx.author.display_name} said \"{reply}\"")

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
    bot.run(auth.token)

if __name__ == "__main__":
    main(sys.argv[1:])