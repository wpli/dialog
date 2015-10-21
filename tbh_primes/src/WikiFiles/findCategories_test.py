from __future__ import division
from math import log10
import pickle
def findCategory(s):	
	picklefiles=pickle.load(open("picklefiles.p", "rb"))
	#print filesNeeded
	wordcounts=[]
	tfs=[]
	idfs=[]
	sentencewords=s.split(" ")
	for a in range(len(picklefiles)):
		#just count the number of each word in each pickle file.
		wikifile=picklefiles[a]
		words=pickle.load(open(wikifile+".p", "rb"))
		tempscores=[]
		tempcounts=[]
		for word in sentencewords:
			tempscores.append(words.count(word)/len(words))
			tempcounts.append(words.count(word))
		tfs.append(tempscores)
		wordcounts.append(tempcounts)
	#for a in range(len(tfs)):
	#	print picklefiles[a]
	#	for b in range(len(tfs[a])):
	#		print "%.5f" % tfs[a][b]
	#	print
	#print
	#print
	for a in range(len(sentencewords)):
		docs=0
		for b in range(len(wordcounts)):
			if wordcounts[b][a]>0:
				docs+=1
	#	print docs
		if docs>0:
			idf=len(wordcounts)/docs
		else:
			idf=1
		idf=log10(idf)
		idfs.append(idf)
	#for a in range(len(idfs)):
	#	print idfs[a]

	tfidfs=[]
	for a in range(len(tfs)):
		tempscores=[]
	#	print picklefiles[a]
		for b in range(len(tfs[a])):
			tempscores.append(tfs[a][b]*idfs[b])
	#		print tfs[a][b]*idfs[b]
		tfidfs.append(tempscores)
	#	print
	#	print

	totalscores=[]
	for a in range(len(tfidfs)):
		totalscore=0
		for b in range(len(tfidfs[a])):
			totalscore+=tfidfs[a][b]
		totalscores.append(totalscore)
	#for a in range(len(totalscores)):
	#	print picklefiles[a]
	#	print totalscores[a]
	#	print
	#origscores=list(totalscores)
	#totalscores.sort()
	#totalscores.reverse()
	#for a in range(len(totalscores)):
	#	print picklefiles[origscores.index(totalscores[a])]
	#	print totalscores[a]
	#	print

	# totalscores contain the total scores corresponding to picklefiles
	categories=pickle.load(open("filesneeded.p", "rb"))
	categoryscores=[]
	ckeys=categories.keys()
	for a in range(len(ckeys)):
	#	print ckeys[a]
		tempscore=0
		for b in range(len(categories[ckeys[a]])):
			c=categories[ckeys[a]][b]
			if c!="": 
				indexOfC=picklefiles.index(c)
			else:
				break
			if indexOfC!=-1: 
				tempscore+=totalscores[indexOfC]
	#	print tempscore
	#	print
		twowords=ckeys[a].split(" ")
		sentencewords1=s.split(" ")		
		for b in range(len(twowords)):
			for c in range(len(sentencewords1)): #if sentencewords have not been modified
				if sentencewords1[c]==twowords[b]:
					tempscore+=1000
		categoryscores.append(tempscore)
	origscores=list(categoryscores)
	categoryscores.sort()
	#categoryscores.reverse()
	#for a in range(len(categoryscores)):
		#print categoryscores[a]
		#print ckeys[origscores.index(categoryscores[a])]
		#print
	categoryscores.reverse()
	return(ckeys[origscores.index(categoryscores[0])])

#test set is a dictionary of words as keys and lists as values
test_set=pickle.load(open("commands.p", "rb"))
tkeys=test_set.keys()
total_total=0
total_yes=0
for a in range(len(tkeys)):
	category_yes=0
	category_total=0	
	for b in range(len(test_set[tkeys[a]])):
		word=test_set[tkeys[a]][b]
		word.strip(".,?!")
		#print word
		category=findCategory(word)
		#print category
		if category==tkeys[a]:
			#print "yes"
			category_yes+=1
		else:
			print word
		#print
		category_total+=1
	#print tkeys[a]
	#print category_yes/category_total
	if tkeys[a].split(" ")[0] != "phone":
		total_total+=category_total
		total_yes+=category_yes

print total_yes/total_total	
	











