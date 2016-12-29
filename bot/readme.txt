[bot_preprocessing.py]
Save the needed data into DB
Handle the QAset

[bot_function.py]
The module for using the bot

[method.py]
Handle different weighting methods

[bot_run.py]
Direct using for asking
Default method is "probability"
	use -w "frequency"/"ratio"/"probability" to set

[bot_config.py]
Save information of DB & QAset

[Training_test.py]
Do training test using QAset
Output the failed matching

/*
data & code required :
	bot_preprocessing.py
	bot_function.py
	method.py
	bot_run.py
	bot_config.py
	QAset.txt
steps :
	rewrite the mongodb config in [bot_config.py]
	run [bot_preprocessing.py] as pre-job
	run [bot_run.py] to direct key-in input
PS.
using bot_run.py -w "frequency"/"ratio"/"probability" to set method
default method is "probability"