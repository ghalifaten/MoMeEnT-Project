from flask import Flask, request, render_template
import os, sys

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from plot_1 import plot_function


app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/plot', methods=['GET', 'POST'])
def plot():
    global n_households
    if request.method == 'POST':
        n_households = request.form.get('n_households')
    print(n_households)
    plot = plot_function(n_households=int(n_households))
    return render_template("plot.html", plot=plot)



if __name__ == "__main__":
    n_households = 5 
    app.run(debug=True)