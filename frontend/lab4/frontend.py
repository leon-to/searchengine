from operator import itemgetter
from bottle import *
import bottle as bottle 
import httplib2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
import beaker as beaker
import sqlite3
from math import ceil, floor
from autocorrect import spell
from enchant.checker import SpellChecker



# int
home_page_or_not = 1 # If home page, it shows 1. If not, it shows 0
saved_pageid = '1' # saved data of pageid
words_count_string = 0
auto_correct_needed = 0
is_it_signed_in = 0
auto_caculator_needed = 0

# dict
signed_out_result = {} # buffer for input words & word-counts. It resets every input.
sorted_signed_out_result = {} # buffer for sorted input words & word-counts. It resets every input.
original_history = {} # buffer for history of words & word-counts. It stacks every input only when signed-in. 
sorted_history = {} # buffer for sorted data of original_history
twenty_sorted_history = {} # buffer for the first 20 of sorted_history
user_input_words = {} # buffer for the inputted words
user_input_words_corrected = {} # buffer for the corrected inputted words
user_input_words_auto_calculated = {} # buffer for the auto-calculated inputted words
user_input_words_auto_corrected_calculated = {} # buffer for the auto-calculated inputted words

# str
connected_string_w_downslash = ""
connected_string_w_space = ""
corrected_connected_string_w_space = ""
auto_calculated_connected_string_w_space = ""
auto_corrected_calculated_connected_string_w_space = ""



#configure middleware
session_opts = {
	'session.type': 'file', 
	'session.cookie_expires': 300,
	'session.data_dir': './data',
	'session.auto': True,
}

new_app = SessionMiddleware(bottle.app(), session_opts)



#Home page
@route('/')
def main_page():
	global home_page_or_not
	global saved_pageid
	global signed_out_result
	global sorted_signed_out_result
	global original_history
	global sorted_history
	global twenty_sorted_history
	global user_input_words
	global connected_string_w_downslash
	global connected_string_w_space
	global words_count_string
	global user_input_words_corrected
	global corrected_connected_string_w_space
	global auto_correct_needed
	global is_it_signed_in
	global auto_caculator_needed
	global user_input_words_auto_calculated
	global auto_calculated_connected_string_w_space
	global user_input_words_auto_corrected_calculated
	global auto_corrected_calculated_connected_string_w_space

	home_page_or_not = 1

	# If the user clicks Google Logo, it goes to homepage.
	# The picture from https://domaingang.com/domain-news/dr-chris-hartnett-the-google-logo-is-a-family-business/
	return_buffer = '''<form action="/return_home" method="get">
								<input type= "image" src="Global_Logo.png" rel="input_image" style = 
									"width:800px;height:300px;
									position:absolute;
					    			top:15%;
					    			left:30%;" alt = "Submit">
								</input><br>
						</form>'''
	
	# Check if the user is logged in.
	beakersession = bottle.request.environ.get('beaker.session')

	# If the user typed something and submitted
	if request.GET.get('submit',''):
		auto_correct_needed = 0
		inputted_words_index = 0
		auto_caculator_needed = 0
		user_input_words = {}
		user_input_words_corrected = {}
		user_input_words_auto_calculated = {}
		user_input_words_auto_corrected_calculated = {}
		signed_out_result = {}
		sorted_signed_out_result = {}
		saved_pageid = '1'
		connected_string_w_downslash = ""
		connected_string_w_space = ""
		corrected_connected_string_w_space = ""
		auto_calculated_connected_string_w_space = ""
		auto_corrected_calculated_connected_string_w_space = ""

		temp_keywords = request.query['keywords'].split(" ")

		if temp_keywords[0]: # If the user data typed at least one character and submitted
			words_count_string = str(len(temp_keywords))

			for temp_keyword in temp_keywords:
				if temp_keyword != "":
					temp_auto_correct_needed = 0
					temp_auto_calculator_needed = 0
					temp_html_address_slash_removed = 0

					# -----spell error auto-correct -----
					temp_auto_corrected_string = ""

					temp_keyword_corrected = temp_keyword
					temp_keyword_for_html_address = temp_keyword

					for char in temp_keyword_for_html_address: # the characters that are not allowed for internet address are replaced to "_"
						if not char.isalnum():
							temp_keyword_for_html_address = temp_keyword_for_html_address.replace(char,'_')
							temp_html_address_slash_removed = 1

					for char in temp_keyword_corrected: # non-alphanumeric values are replaced to "_"
						if not char.isalnum():
							temp_keyword_corrected = temp_keyword_corrected.replace(char,'')
							temp_auto_corrected_string = temp_keyword_corrected
							auto_correct_needed = 1
							temp_auto_correct_needed = 1

					chkr = SpellChecker("en_US")
					chkr.set_text(temp_keyword_corrected)
					for err in chkr:
						sug = err.suggest()[0]
						err.replace(sug)
						auto_correct_needed = 1
						temp_auto_correct_needed = 1
						temp_auto_corrected_string = str(chkr.get_text())
					# ----------------------------------

					# --------- auto-calculator ------------------------------------
					temp_auto_calculated_string = ""

					temp_plus_count = temp_keyword.count('+')
					temp_minus_count = temp_keyword.count('-')
					temp_multiply_count = temp_keyword.count('*')
					temp_divide_count = temp_keyword.count('/')
					temp_open_bracket_count = temp_keyword.count('(')
					temp_close_bracket_count = temp_keyword.count(')')

					temp_pre_auto_caculator_needed = auto_caculator_needed
			
					if( ((temp_plus_count != 0) or (temp_minus_count != 0) or (temp_multiply_count != 0) or (temp_divide_count != 0)) and (temp_open_bracket_count == temp_close_bracket_count) ):
						try:
							temp_auto_calculator_needed = 1
							temp_auto_calculated_string = str(eval(temp_keyword))
						except SyntaxError: #if non-numeric values are located beside the calculation symbols, treat them as normal characters
							temp_auto_calculator_needed = 0
							temp_auto_calculated_string = temp_keyword

						if temp_auto_calculator_needed == 1:
							auto_caculator_needed = 1
					# --------------------------------------------------------------

					user_input_words[inputted_words_index] = temp_keyword
					user_input_words_corrected[inputted_words_index] = temp_auto_corrected_string
					if inputted_words_index != 0:
						connected_string_w_downslash += '_'
						connected_string_w_space += ' '
						corrected_connected_string_w_space += ' '
						auto_calculated_connected_string_w_space += ' '
						auto_corrected_calculated_connected_string_w_space += ' '
					if temp_html_address_slash_removed == 1:
						connected_string_w_downslash += temp_keyword_for_html_address
					else:
						connected_string_w_downslash += temp_keyword
					connected_string_w_space += temp_keyword
					corrected_connected_string_w_space += temp_auto_corrected_string

					if (temp_auto_correct_needed == 1) and (temp_auto_calculator_needed == 1):
						user_input_words_auto_calculated[inputted_words_index] = temp_auto_calculated_string
						auto_calculated_connected_string_w_space += temp_auto_calculated_string

						user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_calculated_string
						auto_corrected_calculated_connected_string_w_space += temp_auto_calculated_string

					elif (temp_auto_correct_needed == 1) and (temp_auto_calculator_needed == 0):
						user_input_words_auto_calculated[inputted_words_index] = temp_keyword						
						auto_calculated_connected_string_w_space += temp_keyword

						user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_corrected_string
						auto_corrected_calculated_connected_string_w_space += temp_auto_corrected_string

					elif (temp_auto_correct_needed == 0) and (temp_auto_calculator_needed == 1):
						user_input_words_auto_calculated[inputted_words_index] = temp_auto_calculated_string
						auto_calculated_connected_string_w_space += temp_auto_calculated_string

						user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_calculated_string
						auto_corrected_calculated_connected_string_w_space += temp_auto_calculated_string

					else:
						user_input_words_auto_calculated[inputted_words_index] = temp_keyword
						auto_calculated_connected_string_w_space += temp_keyword

						user_input_words_auto_corrected_calculated[inputted_words_index] = temp_keyword
						auto_corrected_calculated_connected_string_w_space += temp_keyword

					inputted_words_index += 1

					if temp_keyword in signed_out_result:
						signed_out_result[temp_keyword] += 1 
					else:
						signed_out_result[temp_keyword] = 1 #initial
				
					# Save the counted words data to history only when signed in.
					if 'email' in beakersession.keys():
						if temp_keyword in original_history:
							original_history[temp_keyword] += 1 
						else:
							original_history[temp_keyword] = 1 #initial

			bottle.redirect('/'+ connected_string_w_downslash + '/word_count' + words_count_string + '/page' + saved_pageid)
		else: # If the user typed nothing and submitted	
			bottle.redirect("/") # Go to homepage
	else:
		signed_out_result = {} #empty the results - for the initiation

	# if signed out,
	if 'email' not in beakersession.keys():
		is_it_signed_in = 0

		# When this log-in button is clicked, it will redirect the user to the page that the user can do the google login.
		# The picture from https://www.codenameone.com/blog/login-tutorials-future-of-windows-phone.html
		return_buffer += '''<form action="/sign_in" method="get">
								<input type= "image" src="Google_Sign_In.png" rel="input_image" style = 
									"width:180px;height:50px;
									position:absolute;
					    			top:5%;
					    			left:70%;" alt = "Submit">
								</input><br>
							</form>'''

		sorted_signed_out_result = sorted(signed_out_result.iteritems(), key = lambda x: (-x[1], x[0]))

		# Tpl file according to the signed-out HTML structure
		return_buffer += template('table_signed_out', results = sorted_signed_out_result)
		
		# Shows the message that the user can have an access to the "Top 10 History Words" Functionality once logged in.
		return_buffer += '''<p style =
								"width:180px;height:50px;
								position:absolute;
					    		top:0%;
					    		left:-20%;">Please Log in to use the "Top 10 History Words" service.<br>(The words that you have searched while you are logged out do not count)
							</p>'''
	# if signed in,	
	else:
		is_it_signed_in = 1

		# The picture is from https://stackoverflow.com/questions/25022861/android-google-plus-sign-out-button-looks-different-from-sign-in-button-in-googl
		# It also shows the user email address
		return_buffer += '''<form action="/sign_out" method="get">
								<input type="image" src="Google_Sign_Out.png" rel="input_image" style = 
									"width:120px;height:50px;
									position:absolute;
					    			top:5%%;
					    			left:70%%;" 
									alt = "Submit">
								</input><br>
							</form>
							<p style = 
								"width:120px;height:50px;
								position:absolute;
					    		top:10%%;
					    		left:70%%;">%s
							</p>''' %beakersession['email']

		sorted_signed_out_result = sorted(signed_out_result.iteritems(), key = lambda x: (-x[1], x[0]))
		sorted_history = sorted(original_history.iteritems(), key = lambda x: (-x[1], x[0]))
		twenty_sorted_history = sorted_history[:10]

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_in', results = sorted_signed_out_result, history = twenty_sorted_history)

	return return_buffer

# The page that redirects the user to the home page
@route('/return_home', method='GET') 
def return_home():
	bottle.redirect("/")

# The page that the user can log in.
@route('/sign_in', method = 'GET') 
def sign_in():
	flow = flow_from_clientsecrets("client_secrets.json",
					scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
					redirect_uri="http://localhost:8080/redirect")
	url = flow.step1_get_authorize_url()
	bottle.redirect(str(url))

# The page that the user can log out.
# After log out, it will go back to the previous page just before log out.
@route('/sign_out', method = 'GET') 
def sign_out():
	global temp_connected_string_w_downslash
	global temp_words_count_string
	global saved_page_id

	beakersession = bottle.request.environ.get('beaker.session')
	beakersession.invalidate()
	
	if home_page_or_not == 1:
		bottle.redirect("/")
	else:
		bottle.redirect('/'+ connected_string_w_downslash + '/word_count' + words_count_string + '/page' + saved_pageid)

# The page for retrieving the user's google login information
@route('/redirect', method = 'GET') 
def redirect(): 
	global temp_connected_string_w_downslash
	global temp_words_count_string
	global saved_page_id

	#redirected page, this means the user has successfully signed in
	code = request.query.get('code', 'denied')
	if code == "denied":
		if home_page_or_not == 1:
			bottle.redirect("/")
		else:
			bottle.redirect('/'+ connected_string_w_downslash + '/word_count' + words_count_string + '/page' + saved_pageid)	

	# Given from the lab2 description w/ personal CLIEND_ID & CLIENT_SECRET
	flow = OAuth2WebServerFlow(client_id="705846826446-f39onlnv2kug4pss07rkde8h8p4ai7p0.apps.googleusercontent.com",
					client_secret="3D5y8LmZ_KiFFYnVPkivMTyr",
					scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
					redirect_uri="http://localhost:8080/redirect")
	credentials = flow.step2_exchange(code)
	token = credentials.id_token['sub']

	# Obtain the user email through httplib2
	http = httplib2.Http()
	http = credentials.authorize(http)
	users_service = build('oauth2', 'v2', http=http)
	user_document = users_service.userinfo().get().execute()
	user_email = user_document['email']

	
	#Create the beaker session
	beakersession = bottle.request.environ.get('beaker.session')
	beakersession['unique_user'] = beakersession.id
	beakersession['email'] = user_email
	beakersession.save()
	print beakersession

	if home_page_or_not == 1:
		bottle.redirect("/")
	else:
		bottle.redirect('/'+ connected_string_w_downslash + '/word_count' + words_count_string + '/page' + saved_pageid)

	return return_buffer

# For error-404
@error(404)
def error_404(error):
	# The picture from https://www.elegantthemes.com/blog/tips-tricks/how-to-fix-the-404-error-for-wordpress-websites
	# Go back picture from http://clipartcollections.com/clipart-homepage-3-2/
	# Background with the go back button (to homepage)
    return '''<html>
				<body background="error_404.png" rel="input_image" style = "background-size : 100% auto;">
					<div style="position:absolute;
				    	top:65%;
				    	left:40%;">
						<form action="/" method="get">
							<input type="image" src = "back.png" rel="input_image" style = "width:100px;height:100px;">
							</input><br>
						</form>
					</div>
				</body>
				'''

# For the image processing
@get('/<filename:re:.*\.(png)>')
def input_image(filename):
    return static_file(filename, root='static/img')

# Sub-function of algorithm to retrieve necessary information from the database table
def db_search(searchWord):
	conn = sqlite3.connect('table.db')
	c=conn.cursor()
	c.execute("SELECT DISTINCT DocIndex.url FROM Lexicon, DocIndex, InvertedIndex, PageRank WHERE Lexicon.word_id = InvertedIndex.word_id AND InvertedIndex.doc_id = DocIndex.doc_id AND InvertedIndex.doc_id=PageRank.doc_id AND Lexicon.word LIKE ? ORDER BY PageRank.rank", searchWord)

	return  c.fetchall()

# The page after the user typed something and submitted.
# The address is "http://localhost:8080/page(page #)/(The first word of the inputted data)"
# For example, if the user typed "google log in", it will show "http://localhost:8080/page1/google"
@route('/<input_words_w_slash>/word_count<input_words_count>/page<input_pageid>')
def searchpages(input_words_w_slash, input_words_count, input_pageid):
	global home_page_or_not
	global saved_pageid
	global signed_out_result
	global sorted_signed_out_result
	global sorted_history
	global twenty_sorted_history
	global user_input_words
	global connected_string_w_downslash
	global connected_string_w_space
	global words_count_string
	global corrected_connected_string_w_space
	global auto_correct_needed
	global is_it_signed_in
	global auto_caculator_needed
	global user_input_words_auto_calculated
	global auto_calculated_connected_string_w_space
	global user_input_words_auto_corrected_calculated
	global auto_corrected_calculated_connected_string_w_space

	home_page_or_not = 0
	saved_pageid = input_pageid
	
	# If the user clicks Google Logo, it goes to homepage.
	# The picture from https://domaingang.com/domain-news/dr-chris-hartnett-the-google-logo-is-a-family-business/
	return_buffer = '''<form action="/return_home" method="get">
								<input type= "image" src="/Global_Logo.png" rel="input_image" style = 
									"width:800px;height:300px;
									position:absolute;
					    			top:15%;
					    			left:30%;" alt = "Submit">
								</input><br>
						</form>'''


	# Check if the user is logged in.
	beakersession = bottle.request.environ.get('beaker.session')

	# if signed out,
	if 'email' not in beakersession.keys():
		is_it_signed_in = 0

		# When this log-in button is clicked, it will redirect the user to the page that the user can do the google login.		
		# The picture from https://www.codenameone.com/blog/login-tutorials-future-of-windows-phone.html
		return_buffer += '''<form action="/sign_in" method="get">
								<input type= "image" src="/Google_Sign_In.png" rel="input_image" style = 
									"width:180px;height:50px;
									position:absolute;
					    			top:5%;
					    			left:70%;" alt = "Submit">
								</input><br>
							</form>'''
		
		sorted_signed_out_result = sorted(signed_out_result.iteritems(), key = lambda x: (-x[1], x[0]))

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_out', results = sorted_signed_out_result)
		
		# Shows the message that the user can have an access to the "Top 10 History Words" Functionality once logged in.
		return_buffer += '''<p style =
								"width:180px;height:50px;
								position:absolute;
					    		top:0%;
					    		left:-20%;">Please Log in to use the "Top 10 History Words" service.<br>(The words that you have searched while you are logged out do not count)
							</p>'''
	# if signed in,	
	else:
		is_it_signed_in = 1

		# The picture is from https://stackoverflow.com/questions/25022861/android-google-plus-sign-out-button-looks-different-from-sign-in-button-in-googl
		# It also shows the user email address
		return_buffer += '''<form action="/sign_out" method="get">
								<input type="image" src="/Google_Sign_Out.png" rel="input_image" style = 
									"width:120px;height:50px;
									position:absolute;
					    			top:5%%;
					    			left:70%%;" 
									alt = "Submit">
								</input><br>
							</form>
							<p style = 
								"width:120px;height:50px;
								position:absolute;
					    		top:10%%;
					    		left:70%%;">%s
							</p>''' %beakersession['email']
		

		sorted_signed_out_result = sorted(signed_out_result.iteritems(), key = lambda x: (-x[1], x[0]))
		sorted_history = sorted(original_history.iteritems(), key = lambda x: (-x[1], x[0]))
		twenty_sorted_history = sorted_history[:10]

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_in', results = sorted_signed_out_result, history = twenty_sorted_history)

	temp_page = []
	temp_row_count = 0
	temp_signed_out_alphabetical = {}
	temp_signed_out_alphabetical = signed_out_result.copy()
	temp_signed_out_alphabetical_count = 0
	temp_signed_out_alphabetical_connected_string_w_space = ""

	temp_signed_out_alphabetical = sorted(temp_signed_out_alphabetical)

	for key in temp_signed_out_alphabetical:
		if temp_signed_out_alphabetical_count != 0:
			temp_signed_out_alphabetical_connected_string_w_space += ' '
		temp_signed_out_alphabetical_connected_string_w_space += key
		temp_signed_out_alphabetical_count += 1
		
		temp_word_db_format = (key,)
		temp_result = db_search(temp_word_db_format) # Receive the necessary data from the database	
	
		# Organize the list of data
		# Max 5 links per page
		for row in temp_result:
			temp_row_count += 1

			if temp_row_count % 5 == 1:
				temp_page.append("")

			url = str(row).split("'")
			temp_page[int( floor((temp_row_count - 1) / 5) )] += ('<tr><td>' + key + ': ' + '<a href="' + url[1] + '" target="_blank">'+ url[1] + "</a></td></tr>")
	
	# Hyperlink the suggestion page
	temp_corrected_connected_string_w_space_link = '<tr><td><a href= http://localhost:8080/spell_auto_correct_calculator_route>' + corrected_connected_string_w_space + "</a></td></tr>"
	temp_auto_calculated_connected_string_w_space_link = '<tr><td><a href= http://localhost:8080/spell_auto_correct_calculator_route>' + auto_calculated_connected_string_w_space + "</a></td></tr>"
	temp_auto_corrected_calculated_connected_string_w_space_link = '<tr><td><a href= http://localhost:8080/spell_auto_correct_calculator_route>' + auto_corrected_calculated_connected_string_w_space + "</a></td></tr>"

	temp_page_list = "Go to Page:<br>" + """<table border = "0"><tr>"""

	# Hyperlink the page number buttons
	for temp_page_number in range(0, len(temp_page)):
		temp_page_list += '<th><a href= "' + 'http://localhost:8080' + '/' + input_words_w_slash + '/word_count' + input_words_count + '/page' + str(temp_page_number +1) + '">' + str(temp_page_number + 1) + "</a></th>"

	temp_page_list += "</tr>"

	# When there is no result found
	return_buffer += "<br><strong>You typed: </strong>\"%s\"" %connected_string_w_space

	if auto_correct_needed == 1:
		return_buffer += "<br>You mean(spell auto-corrector): %s" %temp_corrected_connected_string_w_space_link
	if auto_caculator_needed == 1:
		return_buffer += "<br>You mean(auto-calculator): %s" %temp_auto_calculated_connected_string_w_space_link
	
	if (auto_correct_needed == 1) and (auto_caculator_needed == 1):
		return_buffer += "<br>You mean(spell auto-corrector & auto-calculator): %s" %temp_auto_corrected_calculated_connected_string_w_space_link

	# Output the contents of the researched data
	if temp_row_count == 0:
		return_buffer += "<br><br> No results found."
	else:
		if len(temp_page) != 0:
			if (int(input_pageid)-1) < len(temp_page): 
					return_buffer += "<br><br><table border = \"0\"><tr><th align = \"left\"> Search Results (Alphabetical, w/o Duplicates)<br>%s</th></tr> %s</table><br><br>%s" %(temp_signed_out_alphabetical, temp_page[(int(input_pageid)-1)], temp_page_list)
			else:
				bottle.redirect('/err')

	return return_buffer

# The page for spell auto-corrector / auto-calculator
@route('/spell_auto_correct_calculator_route') 
def auto_correct_calculator_route(): 
	global saved_pageid
	global signed_out_result
	global sorted_signed_out_result
	global original_history
	global sorted_history
	global twenty_sorted_history
	global user_input_words
	global connected_string_w_downslash
	global connected_string_w_space
	global words_count_string
	global user_input_words_corrected
	global corrected_connected_string_w_space
	global auto_correct_needed
	global is_it_signed_in
	global auto_caculator_needed
	global user_input_words_auto_calculated
	global auto_calculated_connected_string_w_space
	global user_input_words_auto_corrected_calculated
	global auto_corrected_calculated_connected_string_w_space

	temp_keywords = {}

	if (auto_correct_needed == 1) and (auto_caculator_needed == 1):
		temp_keywords = user_input_words_auto_corrected_calculated.copy()	
	elif (auto_correct_needed == 1) and (auto_caculator_needed == 0):
		temp_keywords = user_input_words_corrected.copy()	
	elif (auto_correct_needed == 0) and (auto_caculator_needed == 1):
		temp_keywords = user_input_words_auto_calculated.copy()
	else:
		bottle.redirect('/err')

	auto_correct_needed = 0
	inputted_words_index = 0
	auto_caculator_needed = 0
	user_input_words = {}
	user_input_words_corrected = {}
	user_input_words_auto_calculated = {}
	user_input_words_auto_corrected_calculated = {}
	signed_out_result = {}
	sorted_signed_out_result = {}
	saved_pageid = '1'
	connected_string_w_downslash = ""
	connected_string_w_space = ""
	corrected_connected_string_w_space = ""
	auto_calculated_connected_string_w_space = ""
	auto_corrected_calculated_connected_string_w_space = ""

	if temp_keywords[0]: # If the user data typed at least one character and submitted
		words_count_string = str(len(temp_keywords))

		for temp_keyword in temp_keywords:
			if temp_keyword != "":
				temp_auto_correct_needed = 0
				temp_auto_calculator_needed = 0
				temp_html_address_slash_removed = 0

				# -----spell error auto-correct -----
				temp_auto_corrected_string = ""
				temp_keyword_corrected = temp_keyword
				temp_keyword_for_html_address = temp_keyword

				for char in temp_keyword_for_html_address: # the characters that are not allowed for internet address are replaced to "_"
					if not char.isalnum():
						temp_keyword_for_html_address = temp_keyword_for_html_address.replace(char,'_')
						temp_html_address_slash_removed = 1

				for char in temp_keyword_corrected: # non-alphanumeric values are replaced to "_"
					if not char.isalnum():
						temp_keyword_corrected = temp_keyword_corrected.replace(char,'')
						temp_auto_corrected_string = temp_keyword_corrected
						auto_correct_needed = 1
						temp_auto_correct_needed = 1

				chkr = SpellChecker("en_US")
				chkr.set_text(temp_keyword_corrected)
				for err in chkr:
					sug = err.suggest()[0]
					err.replace(sug)
					auto_correct_needed = 1
					temp_auto_correct_needed = 1
					temp_auto_corrected_string = str(chkr.get_text())
				# ----------------------------------

				# --------- auto-calculator ------------------------------------
				temp_auto_calculated_string = ""

				temp_plus_count = temp_keyword.count('+')
				temp_minus_count = temp_keyword.count('-')
				temp_multiply_count = temp_keyword.count('*')
				temp_divide_count = temp_keyword.count('/')
				temp_open_bracket_count = temp_keyword.count('(')
				temp_close_bracket_count = temp_keyword.count(')')

				temp_pre_auto_caculator_needed = auto_caculator_needed
			
				if( ((temp_plus_count != 0) or (temp_minus_count != 0) or (temp_multiply_count != 0) or (temp_divide_count != 0)) and (temp_open_bracket_count == temp_close_bracket_count) ):
					try:
						temp_auto_calculator_needed = 1
						temp_auto_calculated_string = str(eval(temp_keyword))
					except SyntaxError: #if non-numeric values are located beside the calculation symbols, treat them as normal characters
						temp_auto_calculator_needed = 0
						temp_auto_calculated_string = temp_keyword

					if temp_auto_calculator_needed == 1:
						auto_caculator_needed = 1
				# --------------------------------------------------------------

				user_input_words[inputted_words_index] = temp_keyword
				user_input_words_corrected[inputted_words_index] = temp_auto_corrected_string
				if inputted_words_index != 0:
					connected_string_w_downslash += '_'
					connected_string_w_space += ' '
					corrected_connected_string_w_space += ' '
					auto_calculated_connected_string_w_space += ' '
					auto_corrected_calculated_connected_string_w_space += ' '
				if temp_html_address_slash_removed == 1:
					connected_string_w_downslash += temp_keyword_for_html_address
				else:
					connected_string_w_downslash += temp_keyword
				connected_string_w_space += temp_keyword
				corrected_connected_string_w_space += temp_auto_corrected_string

				if (temp_auto_correct_needed == 1) and (temp_auto_calculator_needed == 1):
					user_input_words_auto_calculated[inputted_words_index] = temp_auto_calculated_string
					auto_calculated_connected_string_w_space += temp_auto_calculated_string

					user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_calculated_string
					auto_corrected_calculated_connected_string_w_space += temp_auto_calculated_string

				elif (temp_auto_correct_needed == 1) and (temp_auto_calculator_needed == 0):
					user_input_words_auto_calculated[inputted_words_index] = temp_keyword						
					auto_calculated_connected_string_w_space += temp_keyword

					user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_corrected_string
					auto_corrected_calculated_connected_string_w_space += temp_auto_corrected_string

				elif (temp_auto_correct_needed == 0) and (temp_auto_calculator_needed == 1):
					user_input_words_auto_calculated[inputted_words_index] = temp_auto_calculated_string
					auto_calculated_connected_string_w_space += temp_auto_calculated_string

					user_input_words_auto_corrected_calculated[inputted_words_index] = temp_auto_calculated_string
					auto_corrected_calculated_connected_string_w_space += temp_auto_calculated_string

				else:
					user_input_words_auto_calculated[inputted_words_index] = temp_keyword
					auto_calculated_connected_string_w_space += temp_keyword

					user_input_words_auto_corrected_calculated[inputted_words_index] = temp_keyword
					auto_corrected_calculated_connected_string_w_space += temp_keyword

				inputted_words_index += 1

				if temp_keyword in signed_out_result:
					signed_out_result[temp_keyword] += 1 
				else:
					signed_out_result[temp_keyword] = 1 #initial
				
				# Save the counted words data to history only when signed in.
				if 'email' in beakersession.keys():
					if temp_keyword in original_history:
						original_history[temp_keyword] += 1 
					else:
						original_history[temp_keyword] = 1 #initial

		bottle.redirect('/'+ connected_string_w_downslash + '/word_count' + words_count_string + '/page' + saved_pageid)
	else: # If the user typed nothing and submitted	
		bottle.redirect("/") # Go to homepage

	return bottle.redirect('/err')

run(host = "localhost", port = "8080", debug = True, app = new_app)


