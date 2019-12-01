import discord
from challenges import problem_types, challenges, pending, ratings

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
	"> ** c!rating **",
	"> See your current rating."
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
	'rating': ["Type `c!rating` to see your current rating (default rating is 1500)."],
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
	incoming = []
	outgoing = []
	for challenge_id in pending:
		for challenge in pending[challenge_id]:
			if challenge.user == author:
				incoming.append([challenge_id, challenge])

	if author in pending:
		outgoing = pending[author]

	if incoming == [] and outgoing == []:
		await message.channel.send("You have no pending challenges.")
		return

	msg = []
	if incoming:
		msg.append("You have %d incoming challenge(s):" % len(incoming))
		for [user, challenge] in incoming:
			msg.append("Competitor: %s" % challenge.handle1)
			msg.append("Difficulty: %d - %d" % (challenge.diff_range[0], challenge.diff_range[1]))
			if challenge.problem_types == []:
				msg.append("Problem types: None \n")
			else:
				msg.append("Problem types: " + ", ".join(challenge.problem_types)+'\n')
	if outgoing:
		msg.append("You have %d outgoing challenge(s):" % len(outgoing))
		for challenge in outgoing:
			msg.append("Competitor: %s" % challenge.handle2)
			msg.append("Difficulty: %d - %d" % (challenge.diff_range[0], challenge.diff_range[1]))
			if challenge.problem_types == []:
				msg.append("Problem types: None \n")
			else:
				msg.append("Problem types: " + ", ".join(challenge.problem_types)+'\n')

	await message.channel.send('\n'.join(msg))


async def c_ongoing(message, author, server):
	ongoing = []
	for challenge in challenges:
		if challenge.user1 == author:
			ongoing.append([challenge.handle2, challenge])
		elif challenge.user2 == author:
			ongoing.append([challenge.handle1, challenge])

	if ongoing == []:
		await message.channel.send("You have no ongoing challenges.")
		return

	msg = ["You have %d ongoing challenge(s):" % len(ongoing)]
	for [user, challenge] in ongoing:
		msg.append("Competitor: %s" % user)
		msg.append("Problem: https://codeforces.com/problemset/problem/%i/%s" % (challenge.problem['contestId'], challenge.problem['index']))
		total_time = time.time() - challenge.start_time
		msg.append("Time in progress: %d minute(s) and %d second(s)\n" % (total_time / 60, total_time % 60))

	await message.channel.send('\n'.join(msg))


async def c_rating(message, author, server):
	if author not in ratings:
		ratings[author] = 1500
	await message.channel.send("<@%i>, your current rating is %i!" % (author, ratings[author]))