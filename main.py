import discord
import json
import requests
import asyncio
import time
from random import randint
from check_subs import check_subs
from challenges import *
from misc_commands import *
from handles import c_sethandle, c_handle
from models import client

'''
FILE ORGANIZATION:

models.py (CLASSES):
	- Challenge(user1, user2, handle1, handle2, problem, channel)
	- PendingChallenge(user, handle1, handle2, diff_range, problem_types)
    - client(discord.client())
check_subs.py:
	- end_challenge_win(challenge, winner, loser)
	- end_challenge_draw(challenge)
	- check_subs()
challenges.py:
	- c_challenge(message, author, server)
	- c_accept(message, author, server)
	- c_cancel(message, author, server)
	- challenges = []
	- pending = {}
util_commands.py:
	- valid_handle(handle1, handle2)
	- get_problems(challenge)
misc_commands.py:ww
	- c_help(message,author,server)
	- c_pending(message, author, server)
	- c_ongoing(message, author, server)
	- c_rating(message, author, server)
	- c_leaders(message, author, server)
verification.py:
    - c_sethandle(message, author, server)
    - c_handle(message, author, server)

'''

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=activity)
    await check_subs()


to_func = {
    'help' : c_help,				# info about commands
    'challenge' : c_challenge,		# challenge user to race
    'cancel' : c_cancel,			# cancel pending challenge with user (can be from either challenger or challengee)
    'accept' : c_accept,			# accept user's challenge
    'pending' : c_pending,			# view pending challenges
    'ongoing' : c_ongoing,			# view ongoing challenges
    'rating' : c_rating,			# view target user's rating and win/loss
    'leaders' : c_leaders,			# view top users
    'sethandle' : c_sethandle       # set handle
}


# format of challenge:
# c!challenge [user(discord user)] [difficulty lower bound] [difficulty upper bound] [problem tags]

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


'''
TO-DO list:

- create registration system (verify user and link to cf account)
- create match history (see last 10 matches or so?)
- take problem difficulty into account when determining rating change?
	- take difficulty / rating as a multiplier if you win, as a divisor if you lose?

Future ideas:
- analysis of matches, problem types, problem difficulties
- tournament bracket: allow people to create and join tournaments



'''