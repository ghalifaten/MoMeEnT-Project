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

@app.route('/experiment1')
def experiment_1():
    return render_template("experiment_1.html")

@app.route('/experiment2')
def experiment_2():
    return render_template("experiment_2.html")

@app.route('/experiment3')
def experiment_3():
    return render_template("experiment_3.html")

@app.route('/experiment4')
def experiment_4():
    return render_template("experiment_4.html")


@app.route('/conclusion')
def conclusion():
    return render_template("conclusion.html")

if __name__ == "__main__":
    app.run(debug=True)