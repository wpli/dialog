from __future__ import division
from math import log10
import pickle
import urllib
		
def getScore(s, categories):
	words=s.split(" ")
	scores=[]
	for a in range(len(categories)):
		tempscore=0
		parts=categories[a].split(" ")
		#KEYWORD SEARCHING START
		for b in range(len(parts)):
			partsinparts=parts[b].split("_")
			for c in range(len(partsinparts)):
				if words.count(partsinparts[c])>0 or words.count(partsinparts[c]+"'s")>0:
					tempscore=tempscore+(1000/len(partsinparts))
		#KEYWORD SEARCHING END
		#DONE ADDING
		scores.append(tempscore)
	oldscores=list(scores)
	scores.sort()
	scores.reverse()
	if scores[0]==2000:
		return categories[oldscores.index(scores[0])]
	else:
		return "none"
commands=pickle.load(open("commands.p", "rb"))
categories=commands.keys()
#start testing
yes=0
total=0
for a in range(len(categories)):
	sentences=commands.get(categories[a])
	for b in range(len(sentences)):
		keywordcategory=getScore(sentences[b], categories)
		if keywordcategory==categories[a]:
			yes=yes+1
		else:
			print sentences[b]
	total=total+len(sentences)
print (yes/total)
