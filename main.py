import discord
import json
import requests
import asyncio
import time
from random import randint

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


class PendingChallenge:
	def __init__(self, user, handle1, handle2, diff_range, problem_types):
		self.user = user  		# discord id of first user
		self.handle1 = handle1  	# cf handle of first user
		self.handle2 = handle2 		# cf handle of second user
		self.diff_range = diff_range 		# difficulty range
		self.problem_types = problem_types		# problem types (AND, not OR)


problem_types = ['constructive algorithms','sortings','strings','dp',
'greedy','math','flows','graphs','data structures','matrices','brute force',
'implementation','hashing','trees','two pointers','combinatorics','fft',
'binary search','dfs and similar','divide and conquer','shortest paths',
'meet-in-the-middle','dsu','geometry','bitmasks','probabilities','number theory',
'ternary search','2-sat','graph matchings','games','*special','string suffix structures',
'interactive','expression parsing','chinese remainder theorem','schedules']


test = {
	"contestId":1251,
	"index":"A",
	"name":"Broken Keyboard",
	"type":"PROGRAMMING",
	"rating":1000,
	"tags":["brute force","strings","two pointers"]
}


challenges = []		# list of Challenges
pending = {} 	#pending challenges, mapped from challenger to list of challengees


async def end_challenge_draw(challenge):
	total_time = time.time() - challenge.start_time 
	minutes = total_time / 60
	seconds = total_time % 60
	await challenge.channel.send("<@%i> and <@%i> solved the problem https://codeforces.com/problemset/problem/%i/%s in %i minutes and %i seconds as a team. Guess it's a draw!" \
	 							% (challenge.user1, challenge.user2, challenge.problem['contestId'], challenge.problem['index'], minutes, seconds))
	challenge.complete = True


async def end_challenge_win(challenge, winner, loser):
	total_time = time.time() - challenge.start_time 
	minutes = total_time / 60
	seconds = total_time % 60
	await challenge.channel.send("<@%i> defeated <@%i>, solving the problem https://codeforces.com/problemset/problem/%i/%s in %i minutes and %i seconds!" \
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
			try:
				if sub['verdict'] != 'OK':
					continue
			except KeyError:
				continue
			for challenge in challenges:
				if challenge.complete:
					continue
				if sub['problem']['name'] == challenge.problem['name']:
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



async def valid_handles(handle1, handle2): 		# check validity of submitted handles by querying CF API
	HANDLES_URL = "https://codeforces.com/api/user.info?handles=%s;%s" % (handle1, handle2)
	response = requests.get(HANDLES_URL)

	if response.status_code != 200:
		return False

	conversion_data = response.json()

	if conversion_data['status'] != 'OK':
		return False
	return True


async def get_problems(challenge):
	SUBS_URL = "https://codeforces.com/api/user.status?handle=%s" % challenge.handle1
	response = requests.get(SUBS_URL)
	if response.status_code != 200:
		return False

	submissions1 = response.json()

	SUBS_URL = "https://codeforces.com/api/user.status?handle=%s" % challenge.handle2
	response = requests.get(SUBS_URL)
	if response.status_code != 200:
		return False

	submissions2 = response.json()

	PROBLEMS_URL = "https://codeforces.com/api/problemset.problems?"

	if challenge.problem_types:
		PROBLEMS_URL += "tags="+";".join(challenge.problem_types)

	response = requests.get(PROBLEMS_URL)
	if response.status_code != 200:
		return False

	seen = {}

	for sub in submissions1['result']:
		if 'problemsetName' in sub['problem']:
			continue
		seen[sub['problem']['name']] = 1

	for sub in submissions2['result']:
		if 'problemsetName' in sub['problem']:
			continue
		seen[sub['problem']['name']] = 1

	problems = response.json()

	viable = []

	for problem in problems['result']['problems']:
		if 'rating' in problem and 'problemsetName' not in problem and problem['name'] not in seen:
			if problem['rating'] and challenge.diff_range[0] <= problem['rating'] <= challenge.diff_range[1]:
				viable.append(problem)

	return viable


async def c_challenge(message, author, server):
	query = message.content.split()
	if len(query) < 6:
		await message.channel.send('Your query is missing fields. See `c!help` for details.')
		return

	#	check if the queried user is a member of the same discord server

	tar = query[1].replace('!',"")
	try:
		if len(tar) <= 3 or tar[:2] != '<@' or tar[-1] != '>' or int(tar[2:-1]) not in [member.id for member in server.members]:
			await message.channel.send('That is an invalid request. Please format challenges as thus: `c!challenge [@discord user] [cf handle1] [cf handle2] [difficulty floor] [difficulty ceiling] [problem tags]`. See c!help for clarification.')
			return
	except ValueError:
		await message.channel.send('That is an invalid request. Please format challenges as thus: `c!challenge [@discord user] [cf handle1] [cf handle2] [difficulty floor] [difficulty ceiling] [problem tags]`. See c!help for clarification.')
		return
	challenge_id = int(tar[2:-1])
	cur_challenge = PendingChallenge(challenge_id, query[2], query[3], [0,5000], [])

	#	check if handles are both valid

	if not await valid_handles(query[2], query[3]):
		await message.channel.send('One or both of the handles are invalid. Check your spelling.')
		return

	#	check if query range is integers

	try:
		cur_challenge.diff_range[0], cur_challenge.diff_range[1] = int(query[4]), int(query[5])
	except:
		await message.channel.send('The difficulty range requested is invalid.')
		return

	#	get all the queried problem types (watch out for queries like 'chinese remainder theorem')
	#	that case is handled by concatenating the strings

	cur = ''

	for i in range(6,len(query)):
		cur = (cur + " " + query[i]).strip()
		if cur in problem_types:
			cur_challenge.problem_types.append(cur)
			cur = ''
	if cur != '':
		await message.channel.send('You submitted an invalid problem type. Refer to `c!help` for aid.')
		return

	#	need to check whether or not a challenge between the two users is already pending

	await message.channel.send('Please wait while I ensure there are problems filling those constraints.')

	if not await get_problems(cur_challenge):
		await message.channel.send('There were no problems filling those contraints. Either you\'ve solved too many problems or you should adjust the difficulty range or problem types.')
		return

	if author not in pending:
		pending[author] = [cur_challenge]
	else:
		for challenge in pending[author]:
			if challenge_id == challenge.user:
				await message.channel.send('You already have a pending challenge with <@%i>! If you wish to cancel it, use the `c!cancel` command.' % challenge_id)
				return
		pending[author].append(cur_challenge)

	await message.channel.send('<@%i> has challenged <@%i> to a race! <@%i> should send the message \"c!accept <@%i>\" to accept.' % (author, challenge_id, challenge_id, author))
	


async def c_cancel(message, author, server):

	query = message.content.split()
	if len(query) != 2:
		await message.channel.send('That is an invalid request. Cancel challenges in the format `c!cancel @user`. See c!help for clarification.')
		return

	tar = query[1].replace('!',"")
	try:
		if len(tar) <= 3 or tar[:2] != '<@' or tar[-1] != '>' or int(tar[2:-1]) not in [member.id for member in server.members]:
			await message.channel.send('That is an invalid request. Cancel challenges in the format `c!cancel @user`. See c!help for clarification.')
			return
	except ValueError:
		await message.channel.send('That is an invalid request. Cancel challenges in the format `c!cancel @user`. See c!help for clarification.')
		return
	target_id = int(tar[2:-1])

	if author not in pending:
		await message.channel.send('You have no ongoing or pending challenge with that user.')
		return

	for challenge in pending[author]:
		if challenge.user == target_id:
			await message.channel.send('You have successfully canceled your pending challenge with <@%i>.' % target_id)
			return

	for challenge in challenges:
		if (challenge.user1 == author and challenge.user2 == target_id) or (challenge.user1 == target_id and challenge.user2 == author):
			await message.channel.send('You have successfully canceled your pending challenge with <@%i>.' % target_id)
			return

	await message.channel.send('You have no ongoing or pending challenge with that user.')


async def c_accept(message, author, server):
	query = message.content.split()
	if len(query) != 2:
		await message.channel.send('That is an invalid request. Accept challenges in the format `c!accept @user`. See c!help for clarification.')
		return

	tar = query[1].replace('!',"")
	try:
		if len(tar) <= 3 or tar[:2] != '<@' or tar[-1] != '>' or int(tar[2:-1]) not in [member.id for member in server.members]:
			await message.channel.send('That is an invalid request. Accept challenges in the format `c!accept @user`. See c!help for clarification.')
			return
	except ValueError:
		await message.channel.send('That is an invalid request. Accept challenges in the format `c!accept @user`. See c!help for clarification.')
		return
	challenge_id = int(tar[2:-1])

	#	if the target user never even started a challenge
	if challenge_id not in pending:
		await message.channel.send('You have no pending challenge from that user.')
		return

	for challenge in pending[challenge_id]:
		if challenge.user == author:
			problems = await get_problems(challenge)
			if not problems:
				await message.channel.send('Apparently there are no longer any problems filling the constraints. Please try resending the challenge.')
				pending[challenge_id].remove(challenge)
				return
			else:
				problem = problems[randint(0,len(problems)-1)]
				await message.channel.send('<@%i> has accepted <@%i>\'s challenge! The problem will be revealed in 3' % (author, challenge_id))
				await asyncio.sleep(1)
				await message.channel.send('2')
				await asyncio.sleep(1)
				await message.channel.send('1')
				await asyncio.sleep(1)
				await message.channel.send("The challenge has begun! https://codeforces.com/problemset/problem/%i/%s" % (problem['contestId'], problem['index']))
				cur_challenge = Challenge(challenge_id, author, challenge.handle1, challenge.handle2, problem, message.channel)
				challenges.append(cur_challenge)
				return

	await message.channel.send('You have no pending challenge from that user.')



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
# c!challenge [user(discord user)] [handle1] [handle2] [difficulty lower bound] [difficulty upper bound] [problem tags]

# format of accept, decline, cancel:
# c![command] [user]


async def invalid(message):
	await message.channel.send("Invalid command. Refer to c!help.")


@client.event
async def on_message(message):
    if message.author == client.user or len(message.content) < 2 or message.content[:2] != 'c!':
        return
    query = message.content[2:].split()
    if len(query) and query[0] in to_func:
        if message.channel.type == discord.ChannelType.private:
            await message.channel.send('This function cannot be used in DMs.')
        else:
            func = to_func[query[0]]
            await func(message, message.author.id, message.guild)
    else:
        await invalid(message)

client.run('')