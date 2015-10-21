python tbh_create_skype_contacts_grammar.py $1 > call_contact.jsgf
cp $1.contacts ../../tbh_compute_text_feature_set/src/tbh_skype_contact.txt

cp call_contact.jsgf ~/summit/tbh/tbh_user_specific_recognizer/wheelchair.jsgf
cp $1.vocab ~/summit/tbh/tbh_user_specific_recognizer/wheelchair.vocab

cd ~/summit/tbh/tbh_user_specific_recognizer/
./build-from-jsgf.csh wheelchair
mv ~/summit/tbh/tbh_user_specific_recognizer/wheelchair.ffst ~/summit/tbh/tbh_baseline_recognizer/grammar/call_contact.ffst



