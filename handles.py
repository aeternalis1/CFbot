import discord
import json
import requests
import asyncio
import time
from random import randint
from util_commands import valid_handle, rand_problem, get_user


handles = {}	# maps discord ids to cf handles
				# each handle can have multiple discord ids, but each discord id has a unique handle


async def verify(author, start_time, handle, message):
	user = await get_user(author)
	problem = await rand_problem()
	await user.send("To verify your handle `%s`, please make a CE submission (on that account) to https://codeforces.com/problemset/problem/%i/%s within the next five minutes." % (handle, problem['contestId'], problem['index']))
	while time.time() - start_time < 300:
		SUBS_URL = "https://codeforces.com/api/problemset.recentStatus?count=50"
		response = requests.get(SUBS_URL)
		if response.status_code != 200:
			await asyncio.sleep(5)
			continue

		conversion_data = response.json()
		for sub in conversion_data['result']:
			try:
				if sub['verdict'] != 'COMPILATION_ERROR':
					continue
			except KeyError:
				continue
			for user in sub['author']['members']:
				if user['handle'].lower() == handle.lower():
					return True

		await asyncio.sleep(5)	# check every 5 seconds
		print (time.time()-start_time)

	return False


async def c_sethandle(message, author, server):	# sets handle of user
	query = message.content.split()
	if len(query) != 2:
		await message.channel.send("Invalid request. Please format your requests as such: `c!sethandle [handle]`")
		return
	handle = query[1]
	if not await valid_handle(handle):
		await message.channel.send("Invalid handle. Please check your spelling.")
		return
	if author in handles and handles[author] == handle:
		await message.channel.send("Your handle is already `%s`." % handle)
		return
	if await verify(author, time.time(), handle, message):
		await message.channel.send("<@%i>, your new handle is `%s`!" % (author, handle))
		handles[author] = handle
		return
	await message.channel.send("<@%i>, we were unable to verify your new handle `%s`. Please try again." % (author, handle))


async def c_handle(message, author, server):	# checks handle of target user
	pass