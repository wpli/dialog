from __future__ import division
from math import log10
import pickle
import urllib2

#categories is the keys in the dictionary stored in commands.p
def makePFiles(categories):
	files={
		"wake_up":"Wakefulness",
		"system":"System",
		"go_to_sleep":"Sleep_mode",		
	
		"time":"Time",
		"date":"Calendar_date",

		"today":"Present",
		"tomorrow":"Future",
		"monday":"Monday",
		"tuesday":"Tuesday",
		"wednesday":"Wednesday",
		"thursday":"Thursday",
		"friday":"Friday",
		"saturday":"Saturday",
		"sunday":"Sunday",

		"activities":"Action_(philosophy)",

		"weather":"Weather",

		"breakfast":"Breakfast",		
		
		"lunch":"Lunch",	
		
		"dinner":"Dinner",

		"audio_on":"Wakefulness",
		"voice_synthesizer":"Sound",
		"audio_off":"Shutdown_(computing)",
		"interrupt":"Interrupt",		
		"speak_text_on_screen":"Speech",			
				
		"phone":"Phone",
		"make_phone_call":"Phone_call",	
		"hold_call":"Hold_(telephone)",

		#add more for these
		"hang_up":"none",
		"phone resume_call":"none",
		"phone fullscreen_video":"none",
		"phone unfullscreen_video":"none",
		"phone show_contacts":"none",
		"phone answer_phone":"none",

		"confirmatory yes":"Acceptance",
		"confirmatory no":"Negation_(linguistics)",

		"null yes_record":"none",
	}	
	keywords=[]
	#make a list that contains the split up categories -- [monday, tuesday, lunch, activities, etc.]
	for a in range(len(categories)):
		parts=categories[a].split(" ")
		for b in range(len(parts)):
			if keywords.count(parts[b])==0:
				keywords.append(parts[b])
	for b in range(len(keywords)):
		opener=urllib2.build_opener()
		opener.addheaders=[("User-agent", "Mozilla/5.0")]
		f=opener.open("http://en.wikipedia.org/wiki/"+str(files.get(keywords[b])))
		s=f.read()
		para=check=checkifdone=0
		paragraphs=''	       	
		for a in s:
			if check==0 and a!='>' and a!='<' and para==1:
				paragraphs+=a
			if a=='p' and checkifdone==1:
				para=0
				checkifdone=0
				paragraphs+="  "
			elif checkifdone==1:
				checkifdone=0
			if a=='/':
				checkifdone=1
			if a=='>' and check==2:
				check=0
			if check==1:
				check=2
				if a=='p':
					para=1
			if a=='<':
				check=1
		wordlist=paragraphs.split(' ')
		for a in range(len(wordlist)):
			wordlist[a]=wordlist[a].lower()
			wordlist[a]=wordlist[a].strip('.,[]123456\\7890?!&$@*()-=+{}\n/;:"<\'>`~_|')
			print wordlist[a]		
		f=open("pFiles/"+keywords[b]+".p", "wb")
		pickle.dump(wordlist, f)
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

getScore("what is the forecast for today", categories, pFiles)
#makePFiles(categories)
