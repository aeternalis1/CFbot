import discord
import json
import requests
import asyncio
import time

client = discord.Client()

activity = discord.Game(name="c!help")


class Challenge:
	def __init__(self, user1, user2, handle1, handle2, problem, channel):
		self.user1 = user1  		# discord id of first user
		self.user2 = user2 			# discord id of second user
		self.handle1 = handle1  	# cf handle of first user
		self.handle2 = handle2 		# cf handle of second user
		self.problem = problem 		# Problem Type of CF API
		self.channel = channel 		# original channel the challenge was sent in
		self.complete = False 		# is challenge complete or not?
		self.start_time = time.time()

test = {
	"contestId":1251,
	"index":"A",
	"name":"Broken Keyboard",
	"type":"PROGRAMMING",
	"rating":1000,
	"tags":["brute force","strings","two pointers"]
}

challenges = [Challenge(159105923841785857, 159105923841785857, 'aeternalis1', 'AQT', test, 473158290948227083)]		# list of Challenges

async def end_challenge_draw(challenge):
	total_time = time.time() - challenge.start_time 
	minutes = total_time / 60
	seconds = total_time % 60
	channel = client.get_channel(challenge.channel)
	await channel.send("<@%i> and <@%i> solved the problem https://codeforces.com/problemset/problem/%i/%s in %i minutes and %i seconds as a team. Guess it's a draw!" \
	 							% (challenge.user1, challenge.user2, challenge.problem['contestId'], challenge.problem['index'], minutes, seconds))
	challenge.complete = True


async def end_challenge_win(challenge, winner, loser):
	total_time = time.time() - challenge.start_time 
	minutes = total_time / 60
	seconds = total_time % 60
	channel = client.get_channel(challenge.channel)
	await channel.send("<@%i> defeated <@%i>, solving the problem https://codeforces.com/problemset/problem/%i/%s in %i minutes and %i seconds!" \
								% (winner, loser, challenge.problem['contestId'], challenge.problem['index'], minutes, seconds))
	challenge.complete = True


async def check_subs():
	while True:
		SUBS_URL = "https://codeforces.com/api/problemset.recentStatus?count=50"
		response = requests.get(SUBS_URL)

		if response.status_code != 200:
			await asyncio.sleep(5)
			continue

		conversion_data = response.json()
		for sub in conversion_data['result'][::-1]:
			if sub['verdict'] != 'OK':
				continue
			for challenge in challenges:
				if challenge.complete:
					continue
				if sub['problem'] == challenge.problem:
					print ("YES", sub)
					found = 0
					for user in sub['author']['members']:
						if user['handle'].lower() == challenge.handle1.lower():
							found ^= 2
						elif user['handle'].lower() == challenge.handle2.lower():
							found ^= 1
					if found == 3:
						await end_challenge_draw(challenge)
					elif found == 2:
						await end_challenge_win(challenge, challenge.user1, challenge.user2)
					elif found == 1:
						await end_challenge_win(challenge, challenge.user2, challenge.user1)

		for challenge in challenges:
			if challenge.complete:
				challenges.remove(challenge)

		await asyncio.sleep(5)	# check every 5 seconds



@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)
    await check_subs()


'''
API queries needed:

user.status (gets submissions of user, check for problems already attempted)
problemset.problems (gets all problems)
problemset.recentStatus (gets recent submissions)
'''

async def c_help(message, author, server):
	pass

async def c_challenge(message, author, server):
	pass

async def c_cancel(message, author, server):
	pass

async def c_accept(message, author, server):
	pass

async def c_decline(message, author, server):
	pass



to_func = {
    'help' : c_help,				# info about commands
    'challenge' : c_challenge,		# challenge user to race
    'cancel' : c_cancel,			# retract challenge to user
    'accept' : c_accept,			# accept user's challenge
    'decline' : c_decline			# decline user's challenge
}


# format of challenge:
# c!challenge [user(discord user)] [handle1] [handle2] [difficulty range] [problem tags]

# format of accept, decline, cancel:
# c![command] [user]

@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'c!':
        return
    await message.channel.send("REACHED")
    await check_subs()
    query = message.content[2:].split()
    if len(query) and query[0] in to_func:
        if message.channel.type == discord.ChannelType.private:
            await message.channel.send('This function cannot be used in DMs.')
        else:
            func = to_func[query[0]]
            await func(message, message.author.id, servers[message.guild])
    else:
        await invalid(message, servers[message.guild])

client.run('')