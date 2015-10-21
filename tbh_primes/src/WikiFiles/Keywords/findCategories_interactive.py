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
	for a in range(len(scores)):
		print categories[oldscores.index(scores[a])]
		print scores[a]
		print

commands=pickle.load(open("commands.p", "rb"))
categories=commands.keys()
if __name__=="__main__":
	while( 1 ):
		input=raw_input("Enter a sentence: ")
		getScore(input, categories)
