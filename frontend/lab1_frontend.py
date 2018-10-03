from bottle import route, run, template, request
from operator import itemgetter

original_history = {}
sorted_history = {}
twenty_sorted_history = {}

@route('/', method='GET')
def frontend():
	if request.GET.get('submit',''):
		global original_history
		global sorted_history
		global twenty_sorted_history

		temp_results = {}
		temp_keywords = request.query['keywords'].split(" ")

		for temp_keyword in temp_keywords:
			if temp_keyword != "":
				if temp_keyword in temp_results:
					temp_results[temp_keyword] += 1 
				else:
					temp_results[temp_keyword] = 1 #initial

				if temp_keyword in original_history:
					original_history[temp_keyword] += 1 
				else:
					original_history[temp_keyword] = 1 #initial

		sorted_history = sorted(original_history.iteritems(), key = itemgetter(1), reverse = True)
		twenty_sorted_history = sorted_history[:20]

		return template('table', results = temp_results, history = twenty_sorted_history)
	else:
		temp_results = {} #empty the results - for the initiation
		sorted_history = sorted(original_history.iteritems(), key = itemgetter(1), reverse = True)
		twenty_sorted_history = sorted_history[:20]

		return template('table', results = temp_results, history = twenty_sorted_history)

run(host='127.0.0.1', port=8080, debug=True)
