from flask import Flask, request, render_template

app = Flask(__name__, template_folder='templates') #__name__ helps finding other paths of files, a good practice is to specify the template_folder

# -- ROUTING --
# @ signifies a decorator - way to wrap a function and modify its behaviour
#@app.route to connect a web page, specifically means that when I go to the web page in the argument, I get the return value of the function
@app.route('/') #here the page is '/' the home page 
def index():
    return 'This is the home page'


# --- HTTP METHODS (GET and POST) --- 
#Here is where we use the package request
@app.route('/http') #here the page is '/' the home page 
def get_method_type():
    return "Method used: %s" % request.method 

@app.route('/bacon', methods=['GET', 'POST']) #page bacon is capable of handling GET and POST
def bacon():
    if request.method == 'POST':
        return "You are using POST" #can be checked using Postman
    else:
        return "You are probably using GET"

"""
This is an example to show that we can put HTML in the return value
@app.route('/tuna')
def tuna():
    return '<h2>Tuna is good</h2>'
"""

"""
Examples using variables in the url
#simple string
@app.route('/profile/<username>')
def profile(username):
    return 'hello {0}'.format(username)

#Int variables need the type to be specified
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post ID is {0}'.format(post_id)
"""

# --- RENDER TEMPLATES ---
"""
 templates/ contains HTML files
 static/ for static files that never changes like CSS
"""

@app.route("/profile/<username>")
def profile(username):
    return render_template("tuto_profile.html", name=username) #every time I go to the /profile/<name> page, I should look for the file "tuto_profile.html" in the templates directory
    #username is the variable's name, that we can use in the html file using the {{ }}

from another_file import some_function
@app.route("/page2")
def page2():
    some_variable = some_function()
    print(some_variable)
    return render_template("page2.html", name=some_variable)


from function_1 import function
@app.route("/plot")
def plot():
    return function()

if __name__ == "__main__":
    app.run(debug=True) 