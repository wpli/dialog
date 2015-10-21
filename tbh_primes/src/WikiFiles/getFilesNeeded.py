files={
"system wake_up":["Booting_up", "Wakefulness"],

"system go_to_sleep":["Sleep_mode", "Shutdown_(computing)"],

"time time":["Time", "Time"],

"time date":["Calendar_date", "Time"],




"activities today":["Action_(philosophy)", "Present"],
"activities tomorrow":["Action_(philosophy)", "Future"],
"activities monday":["Action_(philosophy)", "Monday"],
"activities tuesday":["Action_(philosophy)", "Tuesday"],
"activities wednesday":["Action_(philosophy)", "Wednesday"],
"activities thursday":["Action_(philosophy)", "Thursday"],
"activities friday":["Action_(philosophy)", "Friday"],
"activities saturday":["Action_(philosophy)", "Saturday"],
"activities sunday":["Action_(philosophy)", "Sunday"],

"weather today":["Weather", "Present"],
"weather tomorrow":["Weather", "Future"],
"weather monday":["Weather", "Monday"],
"weather tuesday":["Weather", "Tuesday"],
"weather wednesday":["Weather", "Wednesday"],
"weather thursday":["Weather", "Thursday"],
"weather friday":["Weather", "Friday"],
"weather saturday":["Weather", "Saturday"],
"weather sunday":["Weather", "Sunday"],





"breakfast today":["Breakfast", "Present"],
"breakfast tomorrow":["Breakfast", "Future"],
"breakfast monday":["Breakfast", "Monday"],
"breakfast tuesday":["Breakfast", "Tuesday"],
"breakfast wednesday":["Breakfast", "Wednesday"],
"breakfast thursday":["Breakfast", "Thursday"],
"breakfast friday":["Breakfast", "Friday"],
"breakfast saturday":["Breakfast", "Saturday"],
"breakfast sunday":["Breakfast", "Sunday"],

"lunch today":["Lunch", "Present"],
"lunch tomorrow":["Lunch", "Future"],
"lunch monday":["Lunch", "Monday"],
"lunch tuesday":["Lunch", "Tuesday"],
"lunch wednesday":["Lunch", "Wednesday"],
"lunch thursday":["Lunch", "Thursday"],
"lunch friday":["Lunch", "Friday"],
"lunch saturday":["Lunch", "Saturday"],
"lunch sunday":["Lunch", "Sunday"],

"dinner today":["Dinner", "Present"],
"dinner tomorrow":["Dinner", "Future"],
"dinner monday":["Dinner", "Monday"],
"dinner tuesday":["Dinner", "Tuesday"],
"dinner wednesday":["Dinner", "Wednesday"],
"dinner thursday":["Dinner", "Thursday"],
"dinner friday":["Dinner", "Friday"],
"dinner saturday":["Dinner", "Saturday"],
"dinner sunday":["Dinner", "Sunday"],

"voice_synthesizer audio_on":["Sound", "Wakefulness"],
"voice_synthesizer audio_off":["Sound", "Shutdown_(computing)"], 
"voice_synthesizer interrupt":["Sound", "Interrupt"],
"voice_synthesizer speak_text_on_screen":["Speech", "Text_(literary_theory)"],

"phone make_phone_call":["Phone", "Phone_call"],
"phone hang_up":["Phone"], #need more 
"phone hold_call":["Phone", "Hold_(telephone)"],
"phone resume_call":["Phone"], #need more
"phone fullscreen_video":["Phone"], #need more
"phone unfullscreen_video":["Phone"], #need more
"phone show_contacts":["Phone", "Contact_list"],
"phone answer_phone":["Phone"], #need more

"confirmatory yes":["Acceptance"],
"confirmatory no":["Negation_(linguistics)"],

"null yes_record":[""]

}
import pickle
out=open("filesneeded.p", "wb")
pickle.dump(files, out)
out.close()

wikifiles=[]
for map in files.keys():
	for wikifile in files.get(map):
		if wikifiles.count(wikifile)==0 and wikifile!="":
			 wikifiles.append(wikifile)	
out=open("picklefiles.p", "wb")
pickle.dump(wikifiles, out)
out.close()
