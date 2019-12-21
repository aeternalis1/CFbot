import discord
import json
import requests
import asyncio
from models import client
from random import randint


async def get_user(user_id):
	return await client.fetch_user(str(user_id))


async def valid_handle(handle): 		# check validity of submitted handles by querying CF API
	HANDLE_URL = "https://codeforces.com/api/user.info?handles=%s" % handle
	response = requests.get(HANDLE_URL)

	if response.status_code != 200:
		return False

	conversion_data = response.json()

	if conversion_data['status'] != 'OK':
		return False
	return True


async def rand_problem():
	URL = "https://codeforces.com/api/problemset.problems?"
	response = requests.get(URL)
	if response.status_code != 200:
		return False

	problems = response.json()

	pos = []
	for problem in problems['result']['problems']:
		pos.append(problem)

	return pos[randint(0,len(pos))]


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