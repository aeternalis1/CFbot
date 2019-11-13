import discord
from challenges import problem_types

help_text = [
	"> List of CFbot commands:",
	"> ** c!help **",
	"> Literally the command you just typed. The results are as you see. To get more information about a certain command, type `c!help [command]`, e.g. `c!help challenge`",
	"> ** c!challenge [@user] [handle1] [handle2] [difficulty LB] [difficulty UB] [problem tags] **",
	"> Challenge another user to a race to solve a problem on Codeforces that neither user has attempted," + \
	" within difficulty rating and problem type constraints provided by the user. e.g. `c!challenge @user tourist petr 100 3000 dp implementation fft`",
	"> ** c!accept [@user] **",
	"> Accept a pending challenge from target user.",
	"> ** c!cancel [@user] **",
	"> Cancel a pending challenge with target user (can be issued from both challenger or challengee).",
	"> ** c!pending **",
	"> See your pending challenges.",
	"> ** c!ongoing **",
	"> See your ongoing challenges.",
]

command_text = {
	'help': ["Really not sure what you expected from this."],
	'challenge': [
		"Challenges are sent in the following format:",
		"`c!challenge [@user] [handle1] [handle2] [difficulty LB] [difficulty UB] [problem tags]`",
		"[@user] : a ping you send to the discord user you wish to challenge.",
		"[handle1] [handle2] : your Codeforces handle and the challengee's handle respectively.",
		"[difficulty LB] [difficulty UB] : Two integers, the lower and upper bounds for your challenge problem.",
		"[problem tags] : This field isn\'t required, but you may include a space-separated list of problem types. Type `c!help types` to see what\'s available."
	],
	'accept': ["Type `c!accept [@user]` to accept a pending challenge from that user."],
	'cancel': ["Type `c!cancel [@user]` to cancel a pending challenge between yourself and that user. You may be either challenger or challengee (note that you may not cancel an ongoing challenge)."],
	'pending': ["Type `c!pending` to see your pending challenges."],
	'ongoing': ["Type `c!ongoing` to see your ongoing challenges."],
	'types': ["The available problem types are: "+", ".join(map(lambda x: '`'+x+'`', problem_types))]
}

async def c_help(message, author, server):
	query = message.content.split()
	if len(query) == 1:
		await message.channel.send('\n'.join(help_text))
		return
	elif len(query) == 2:
		if query[1] in command_text:
			await message.channel.send('\n'.join(command_text[query[1]]))
			return
	await message.channel.send('Sorry, you didn\'t seem to query for an actual command. Type `c!help` for aid.')


async def c_pending(message, author, server):
	pass


async def c_ongoing(message, author, server):
	pass