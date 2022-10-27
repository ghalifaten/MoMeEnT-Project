from flask import Flask, request, render_template
import os, sys

module_path = os.path.abspath(os.path.join('..'))
print(module_path)
if module_path not in sys.path:
    sys.path.append(module_path)

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/experiment')
def experiment():
    return render_template("experiment.html")

@app.route('/conclusion')
def conclusion():
    return render_template("conclusion.html")

if __name__ == "__main__":
    n_households = 5 
    app.run(debug=True)