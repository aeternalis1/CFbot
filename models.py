import time


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