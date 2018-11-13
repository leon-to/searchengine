* Frontend
1. Requirements: 
- frontend.py
- client_secrets.json (GoogleAPI)
- table.db (database)
- table_signed_in.tpl (html format - signed in)
- table_signed_out.tpl (html format - signed out)

2. If modification of baseURL is needed: 
The "frontend.py" uses "http://localhost:8080" as its baseURL. 
If this baseURL is wanted to be changed by the user, 
the following 4 lines in "frontend.py" have to be modified: 
(the modified baseURL is described as MODIFIED-BASEURL)
- In @route('/sign_in', method='GET'), more specifically in line 161,
redirect_uri="http://localhost:8080/redirect" has to be changed to 
redirect_uri="MODIFIED-BASEURL/redirect"
- In @route('/redirect', method='GET'), , more specifically in line 192,
redirect_uri="http://localhost:8080/redirect" has to be changed to
redirect_uri="MODIFIED-BASEURL/redirect"
- In def searchpages(input_pageid, input_first_word):, more specifically in line 381,
temp_page_list += '<th><a href= "' + 'http://localhost:8080' + '/page' has to be changed to
temp_page_list += '<th><a href= "' + 'MODIFIED-BASEURL' + '/page'
- In line 394,
run(host = "localhost", port = "8080", debug = True, app = new_app) has to be changed to
run(host = "0.0.0.0", port = "80", debug = True, app = new_app)

3. Features: 
- When the baseURL (ex. "http://localhost:8080") is entered, it goes to the main homepage.

- It also includes the previous feature from lab2 
(google sign-in, sign-out, sign-in message, entered word counts, top 10 inputted words).

- If the main google logo is clicked, it goes to the main home page.

- When a keyword is submitted, it returns a page with a list of clickable URL
links, or indicating results for such keyword cannot be found.

- The returned list of URLs are sorted in greatest-to-least order.

- Each page should have a maximum of 5 links.

- Eace page has the follwing url address: 
"http://localhost:8080/page(Page #)/(The first word of the inputted data)"
ex) http://localhost:8080/page2/video

- An Error page should be returned when user is trying to access a page that does not existed,
or using a HTTP method that is not supported.