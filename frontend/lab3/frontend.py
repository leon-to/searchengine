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



home_page_or_not = 1 # If home page, it shows 1. If not, it shows 0
saved_pageid = '1' # saved data of pageid

signed_out_result = {} # buffer for input words & word-counts. It resets every input.
original_history = {} # buffer for history of words & word-counts. It stacks every input only when signed-in. 
sorted_history = {} # buffer for sorted data of original_history
twenty_sorted_history = {} # buffer for the first 20 of sorted_history

the_first_word_string = {} # buffer for the first word as a string
the_first_word = {} # buffer for the first word to input db_search sub-function

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
	home_page_or_not = 1
	saved_pageid = '1'

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
	print beakersession
	
	global signed_out_result
	global the_first_word_string
	global the_first_word

	# If the user typed something and submitted
	if request.GET.get('submit',''):
		global original_history
		global sorted_history
		global twenty_sorted_history
		
		signed_out_result = {}
		temp_keywords = request.query['keywords'].split(" ")
		
		if temp_keywords[0]: # If the user data typed at least one character and submitted
			the_first_word_string = temp_keywords[0]
			the_first_word = (the_first_word_string,)

			for temp_keyword in temp_keywords:
				if temp_keyword != "":
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
			bottle.redirect('/page' + saved_pageid + '/'+ the_first_word_string)	
		else: # If the user typed nothing and submitted	
			bottle.redirect("/") # Go to homepage
	else:
		signed_out_result = {} #empty the results - for the initiation

	

	# if signed out,
	if 'email' not in beakersession.keys():
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

		# Tpl file according to the signed-out HTML structure
		return_buffer += template('table_signed_out', results = signed_out_result)
		
		# Shows the message that the user can have an access to the "Top 10 History Words" Functionality once logged in.
		return_buffer += '''<p style =
								"width:180px;height:50px;
								position:absolute;
					    		top:0%;
					    		left:-20%;">Please Log in to use the "Top 10 History Words" service.
							</p>'''
	# if signed in,	
	else:
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

		sorted_history = sorted(original_history.iteritems(), key = itemgetter(1), reverse = True)
		twenty_sorted_history = sorted_history[:10]

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_in', results = signed_out_result, history = twenty_sorted_history)

	return return_buffer

# The page that redirects the user to the home page
@route('/return_home', method='GET') 
def return_home():
	bottle.redirect("/")

# The page that the user can log in.
@route('/sign_in', method='GET') 
def sign_in():
	flow = flow_from_clientsecrets("client_secrets.json",
					scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
					redirect_uri="http://localhost:8080/redirect")
	url = flow.step1_get_authorize_url()
	bottle.redirect(str(url))

# The page that the user can log out.
# After log out, it will go back to the previous page just before log out.
@route('/sign_out', method='GET') 
def sign_out():
	beakersession = bottle.request.environ.get('beaker.session')
	beakersession.invalidate()
	
	if home_page_or_not == 1:
		bottle.redirect("/")
	else:
		bottle.redirect('/page' + saved_pageid + '/'+ the_first_word_string)

# The page for retrieving the user's google login information
@route('/redirect', method='GET') 
def redirect(): 
	#redirected page, this means the user has successfully signed in
	code = request.query.get('code', 'denied')
	if code == "denied":
		if home_page_or_not == 1:
			bottle.redirect("/")
		else:
			bottle.redirect('/page' + saved_pageid + '/'+ the_first_word_string)

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
		bottle.redirect('/page' + saved_pageid + '/'+ the_first_word_string)

	return return_buffer

# For error-404
@error(404)
def error_404(error):
	# The picture from https://www.elegantthemes.com/blog/tips-tricks/how-to-fix-the-404-error-for-wordpress-websites
    return '''<html>
				<body background="error_404.png" rel="input_image" style = "background-size : 100% auto;">
					<div style="position:absolute;
				    	top:70%;
				    	left:45%;">
						<form action="/" method="get">
							<input type="image" src = "back.png" rel="input_image" style = "width:80px;height:80px;">
							</input><br>
						</form>
					</div>
				</body>'''

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
# For example, if the user typed "google uoft projects", it will show "http://localhost:8080/page1/google"
@route('/page<input_pageid>/<input_first_word>')
def searchpages(input_pageid, input_first_word):
	global home_page_or_not
	global saved_pageid
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
	print beakersession
	
	global signed_out_result
	global the_first_word_string
	global the_first_word
	
	# If the user typed something and submitted
	if request.GET.get('submit',''):
		global original_history
		global sorted_history
		global twenty_sorted_history

		signed_out_result = {}
		temp_keywords = request.query['keywords'].split(" ")

		if temp_keywords[0]: # If the user data typed at least one character and submitted
			the_first_word_string = temp_keywords[0]
			the_first_word = (the_first_word_string,)

			for temp_keyword in temp_keywords:
				if temp_keyword != "":
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
			bottle.redirect('/page' + saved_pageid + '/'+ the_first_word_string)
		else: # If the user typed nothing and submitted
			bottle.redirect('/') # Go to homepage
	


	# if signed out,
	if 'email' not in beakersession.keys():
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

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_out', results = signed_out_result)
		
		# Shows the message that the user can have an access to the "Top 10 History Words" Functionality once logged in.
		return_buffer += '''<p style =
								"width:180px;height:50px;
								position:absolute;
					    		top:0%;
					    		left:-20%;">Please Log in to use the "Top 10 History Words" service.
							</p>'''
	# if signed in,	
	else:
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

		sorted_history = sorted(original_history.iteritems(), key = itemgetter(1), reverse = True)
		twenty_sorted_history = sorted_history[:10]

		# Tpl file according to the signed-in HTML structure
		return_buffer += template('table_signed_in', results = signed_out_result, history = twenty_sorted_history)

	temp_page = []
	temp_result = db_search(the_first_word) # Receive the necessary data from the database	
	
	# Organize the list of data
	# Max 5 links per page
	temp_count = 0
	for row in temp_result:
		temp_count += 1

		if temp_count % 5 == 1:
			temp_page.append("")

		url = str(row).split("'")
		temp_page[int( floor((temp_count - 1) / 5) )] += ('<tr><td><a href="' + url[1] + '" target="_blank">'+ url[1] + "</a></td></tr>")
	
	# When there is no result found
	if temp_count == 0:
		return_buffer += "<br><br>" +"Search based on the first word: "+ "\"%s\"<br><br> No results found."  %(input_first_word) 

	temp_page_list = "Go to Page:<br>"+"""<table border = "0"><tr>"""
	
	# Hyperlink the page number buttons
	for temp_page_number in range(0, len(temp_page)):
		temp_page_list += '<th><a href= "' + 'http://localhost:8080' + '/page' + str(temp_page_number +1 ) + '/' + input_first_word + '">' + str(temp_page_number + 1) + "<a></th>"

	temp_page_list += "</tr>"

	# Output the contents of the researched data
	if len(temp_page) != 0:
		if (int(input_pageid)-1) < len(temp_page): 
			return_buffer += "<br><br>" + "Search based on the first word: "+  "\"%s\"<br><br><table border = \"0\"><tr><th align = \"left\"> Search Results</th></tr> %s</table><br><br>%s"  %(input_first_word, temp_page[(int(input_pageid)-1)], temp_page_list) 
		else:
			bottle.redirect('/err')

	return return_buffer

run(host = "localhost", port = "8080", debug = True, app = new_app)


