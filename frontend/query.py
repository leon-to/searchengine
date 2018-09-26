from bottle import route, run, static_file, get, post, request
@get('/')
def query():
    return static_file('index.html', root='')

run (host='localhost', port=8080, debug=True)

@post('/')
def display_query():
    return "Query string: {{request.form.get('query')}}"
