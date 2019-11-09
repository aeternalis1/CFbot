import discord

client = discord.Client()

activity = discord.Game(name="c!help")

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)



async def race(message, author, server):


to_func = {
    'help' : c_help,				# info about commands
    'challenge' : c_challenge,		# challenge user to race
    'retract' : c_retract,			# retract challenge to user
    'accept' : c_accept,			# accept user's challenge
    'decline' : c_decline			# decline user's challenge
}

# format of challenge:
# c!challenge [user] [difficulty range] [problem tags]

# format of accept:
# c!accept [user]

@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'c!':
        return

    query = message.content[2:].split()
    if len(query) and query[0] in commands:
        if message.channel.type == discord.ChannelType.private:
            await message.channel.send('This function cannot be used in DMs.')
        else:
            func = to_func[query[0]]
            await func(message, message.author.id, servers[message.guild])
    else:
        await invalid(message, servers[message.guild])

client.run('')