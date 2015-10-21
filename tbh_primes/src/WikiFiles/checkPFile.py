import pickle
contents=pickle.load(open("Present.p", "rb"))
for word in contents:
	if word=="now":
		print word

