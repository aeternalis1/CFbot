import discord
import json
import requests
import asyncio
import time
from challenges import challenges

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
