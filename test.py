import json
import requests

try:
	a += b
except:
	print ("BAH")
finally:
	print ("OK")

'''
PROBLEMS_URL = "https://codeforces.com/api/problemset.problems?"
response = requests.get(PROBLEMS_URL)

conversion_data = response.json()

arr = []

for problem in conversion_data['result']['problems']:
	for tag in problem['tags']:
		if tag not in arr:
			arr.append(tag)

f = open("output.txt",'w')

f.write(",".join(["\'"+x+"\'" for x in arr]))'''