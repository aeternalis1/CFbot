import discord
import json
import requests
import asyncio
import time
from util_commands import get_problems, valid_handle
from models import *
from random import randint


challenges = []		# list of Challenges
pending = {} 	# pending challenges, mapped from challenger to list of challengees
ratings = {}	# mapping players to their ratings (base rating of 1500)
record = {}		# mapping players to their win/loss

problem_types = ['constructive algorithms','sortings','strings','dp',
'greedy','math','flows','graphs','data structures','matrices','brute force',
'implementation','hashing','trees','two pointers','combinatorics','fft',
'binary search','dfs and similar','divide and conquer','shortest paths',
'meet-in-the-middle','dsu','geometry','bitmasks','probabilities','number theory',
'ternary search','2-sat','graph matchings','games','*special','string suffix structures',
'interactive','expression parsing','chinese remainder theorem','schedules']

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

	if not (await valid_handle(query[2]) and await valid_handle(query[3])):
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

	if challenge_id in pending:
		for challenge in pending[challenge_id]:
			if challenge.user == author:
				await message.channel.send('<@%i> has already challenged you to a race! You may either cancel or accept it with the commands `c!cancel <@user>` or `c!accept <@user>` respectively.' % challenge_id)
				return

	if author not in pending:
		pending[author] = [cur_challenge]
	else:
		for challenge in pending[author]:
			if challenge_id == challenge.user:
				await message.channel.send('You already have a pending challenge with <@%i>! If you wish to cancel it, use the `c!cancel` command.' % challenge_id)
				return
		pending[author].append(cur_challenge)

	if author not in ratings:
		ratings[author] = 1500
		record[author] = [0,0]
	if challenge_id not in ratings:
		ratings[challenge_id] = 1500
		record[challenge_id] = [0,0]

	await message.channel.send('<@%i> (Rating: %i) has challenged <@%i> (Rating: %i) to a race! <@%i> should send the message \"c!accept <@%i>\" to accept.' % (author, ratings[author], challenge_id, ratings[challenge_id], challenge_id, author))
	


async def c_cancel(message, author, server):

	query = message.content.split()
	if len(query) != 2:
		await message.channel.send('That is an invalid request. Cancel pending challenges in the format `c!cancel @user`. See c!help for clarification.')
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

	if author not in pending and target_id not in pending:
		await message.channel.send('You have no pending challenge with that user.')
		return

	if author in pending:
		for challenge in pending[author]:
			if challenge.user == target_id:
				await message.channel.send('You have successfully canceled your pending challenge with <@%i>.' % target_id)
				pending[author].remove(challenge)
				return

	if target_id in pending:
		for challenge in pending[target_id]:
			if challenge.user == author:
				await message.channel.send('You have successfully canceled your pending challenge with <@%i>.' % target_id)
				pending[target_id].remove(challenge)
				return

	await message.channel.send('You have no pending challenge with that user.')


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
			await message.channel.send('Please wait while I verify there are still problems fulfilling your constraints.')
			problems = await get_problems(challenge)
			if not problems:
				await message.channel.send('Apparently there are no longer any problems filling the constraints. Please try resending the challenge.')
				pending[challenge_id].remove(challenge)
				return
			else:
				problem = problems[randint(0,len(problems)-1)]
				await message.channel.send('<@%i> has accepted <@%i>\'s challenge!' % (author, challenge_id))
				await asyncio.sleep(1)
				await message.channel.send('3... 2... 1...')
				await asyncio.sleep(1)
				await message.channel.send("Let the race between <@%i> and <@%i> begin! https://codeforces.com/problemset/problem/%i/%s" % (author, challenge_id, problem['contestId'], problem['index']))
				cur_challenge = Challenge(challenge_id, author, challenge.handle1, challenge.handle2, problem, message.channel)
				challenges.append(cur_challenge)
				pending[challenge_id].remove(challenge)
				return

	await message.channel.send('You have no pending challenge from that user.')