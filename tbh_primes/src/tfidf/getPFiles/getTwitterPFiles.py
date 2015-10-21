from __future__ import division
from math import log10
import pickle
import urllib

#categories is the keys in the dictionary stored in commands.p
def makePFiles(categories):
	keywords=[]
	#make a list that contains the split up categories -- [monday, tuesday, lunch, activities, etc.]
	for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0:
				keywords.append(parts[b])
	MAX_PAGES=10
	for b in range(len(keywords)):
		tweetwords=[]
		keyword=""
		splitkeywords=keywords[b].split("_")
		for c in range(len(splitkeywords)):
			keyword=keyword+splitkeywords[c]+" "
		for c in range(MAX_PAGES):
			#opener=urllib2.build_opener() <-- for urllib2
			#opener.addheaders=[("User-agent", "Mozilla/5.0")]
	        	f=urllib.urlopen("http://search.twitter.com/search.atom?q="+keyword+"&rpp=100&page="+str(c))
	        	s=f.read()
			tweet=""
			count=0
	        	for d in range(len(s)):
				if s[d:(d+7)]=="<title>":
					count=1	
				if count==1:
					tweet=tweet+s[d]
				if s[d:(d+8)]=="</title>":
					count=0
					tweet=tweet[7:len(tweet)-1]
					tweetwords.extend(tweet.split(" "))
					tweet=""
		for c in range(len(tweetwords)):
			tweetwords[c]=tweetwords[c].lower()
			tweetwords[c]=tweetwords[c].strip(".")
			tweetwords[c]=tweetwords[c].strip("@")
			tweetwords[c]=tweetwords[c].strip("\"")
			tweetwords[c]=tweetwords[c].strip("_")
			tweetwords[c]=tweetwords[c].strip("!")
			tweetwords[c]=tweetwords[c].strip(".")
			tweetwords[c]=tweetwords[c].strip(",")
			tweetwords[c]=tweetwords[c].strip("/")
			tweetwords[c]=tweetwords[c].strip("?")
			tweetwords[c]=tweetwords[c].strip(":")
			tweetwords[c]=tweetwords[c].strip(";")
			tweetwords[c]=tweetwords[c].strip("{")
			tweetwords[c]=tweetwords[c].strip("}")
			tweetwords[c]=tweetwords[c].strip("[")
			tweetwords[c]=tweetwords[c].strip("]")
			tweetwords[c]=tweetwords[c].strip("(")
			tweetwords[c]=tweetwords[c].strip(")")
			tweetwords[c]=tweetwords[c].strip("-")
			tweetwords[c]=tweetwords[c].strip("=")
			tweetwords[c]=tweetwords[c].strip("+")
			tweetwords[c]=tweetwords[c].strip("&")
			tweetwords[c]=tweetwords[c].strip("%")
			tweetwords[c]=tweetwords[c].strip("$")
			tweetwords[c]=tweetwords[c].strip("'''")
			print tweetwords[c]
			#still more stripping
		f=open("pFiles/"+keywords[b]+".p", "wb")
		pickle.dump(tweetwords, f)
		f.close()
		
#outside lists used:
	#categories-NOT ANYMORE (use as parameter)
	#keywords-NOT ANYMORE
#pFiles--this is a two dimensional array, one dimention are the keywords, and the other are the list of twitter words per keyword
def getScore(s, categories, pFiles):
	keywords=[]
	#make a list that contains the split up categories -- [monday, tuesday, lunch, activities, etc.]
	for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0:
				keywords.append(parts[b])
	words=s.split(" ")
	scores=[]
	
	idfs=[] #only needed once

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

		#find the tf idfs
		#TF IDF'ING START
			#TF'ING NOW
		tfs=[]
		for b in range(len(parts)):
			#pFile=pickle.load(open("pFiles/"+parts[b]+".p", "rb")) #list of words
			pFile=pFiles[keywords.index(parts[b])] #edited
			for c in range(len(words)):
				count=pFile.count(words[c])
				if b==0:
					if count==0:
						tfs.append(0)
					else:
						tfs.append(pFile.count(words[c])/len(pFile))
				else:
					if count!=0:
						tfs[c]=tfs[c]+(pFile.count(words[c])/len(pFile))
		
			#IDF'ING NOW
		#idfs=[]
		total=len(keywords)
		if a==0:
			for b in range(len(words)):
				filesThatContain=0			
				for c in range(len(keywords)):
					#pFile=pickle.load(open("pFiles/"+keywords[c]+".p", "rb"))
					pFile=pFiles[c] #edited					
					if pFile.count(words[b])>0:
						filesThatContain=filesThatContain+1
				if filesThatContain>0:
					idfs.append(log10(total/filesThatContain))
				else:
					idfs.append(0)

			#TF*IDF'ING NOW
		tfidfs=[]
		for b in range(len(words)):
			tfidfs.append(tfs[b]*idfs[b])
		
		#DONE TF*IDF'ING
		#add the tf idfs to the score
		for b in range(len(tfidfs)):
			tempscore=tempscore+tfidfs[b]
		
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
keywords=[] #get keywords
for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0:
				keywords.append(parts[b])
pFiles=[] #get pFiles
for a in range(len(keywords)):
	pFile=pickle.load(open("pFiles/"+keywords[a]+".p", "rb"))
	pFiles.append(pFile)		

getScore("what is the weather today", categories, pFiles)
