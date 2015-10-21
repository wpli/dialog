from __future__ import division
from math import log10
import pickle
import urllib

#categories is the keys in the dictionary stored in commands.p
#makes pFiles of 80% of the turk data
#makePFiles also makes commands.p for the 20% that should be tested on
def makePFiles(commands):
	categories=commands.keys()
	keywords=[]
	#make a list that contains the split up categories -- [monday, tuesday, lunch, activities, etc.]
	days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
	for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0 and days.count(parts[b])==0: #added not including days of week
				keywords.append(parts[b])
	for b in range(len(keywords)):
		words=[]
		for c in range(len(categories)):
			if categories[c].split(" ").count(keywords[b])==1:
				phrases=commands.get(categories[c])
				for d in range(int(len(phrases)*4/5)):
					for word in phrases[d].split(" "):
						if days.count(word)==0:
							words.append(word)		
		f=open("pFiles/"+keywords[b]+".p", "wb")
		pickle.dump(words, f)
		f.close()
	dict={}
	for b in range(len(categories)):
		phrases=commands.get(categories[c])
		splat=[]
		for d in range(int(len(phrases)*2/5)):
			splat.append(phrases[len(phrases)-1-d])
		dict[categories[b]]=splat
	f=open("commands.p", "wb")
	pickle.dump(dict, f)
	f.close()

commands=pickle.load(open("../../MTurk/turkCommands.p", "rb"))
categories=commands.keys()
keywords=[] #get keywords
days=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0 and days.count(parts[b])==0:
				keywords.append(parts[b])
makePFiles(commands)
pFiles=[] #get pFiles
for a in range(len(keywords)):
	pFile=pickle.load(open("amtPFiles/"+keywords[a]+".p", "rb"))
	pFiles.append(pFile)
