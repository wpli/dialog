
all: tbh_language_processor


# since python is not compiled, make just moves files to the bin folder
tbh_language_processor:
	cp *.csv *.py ../bin


# for cleaning, we want to remove those pesky compiled-pythin file
# and also remove the file we copied into the bin folder
clean:
	rm -rf *~
	rm -rf *.pyc
	rm -rf ../bin/*.py
	rm -rf ../bin/*.pyc


