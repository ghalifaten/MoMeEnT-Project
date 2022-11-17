from flask import Flask, request, render_template
import os, sys

module_path = "/home/faten/HERUS/MoMeEnT-Project/" #TODO change this
if module_path not in sys.path:
    sys.path.append(module_path)

from demod_survey.examples.DEMO_QUALTRICS_FUNCTION import demo_qualtrics_function

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/experiment1')
def experiment_1():
    a = -3
    if (a < 0):
        arrow_image="arrow-decrease.png"
        direction="Decrease"
    else:
        arrow_image="arrow-increase.png"
        direction="Increase"

    return render_template("experiment_1.html", arrow_image=arrow_image, direction=direction)

@app.route('/experiment2')
def experiment_2():
    demo_qualtrics_function()
    return render_template("experiment_2.html", nresidents=1, nhouseholds=5)

@app.route('/experiment2', methods=['POST'])
def experiment_2_post():
    nresidents = request.form['nresidents']
    nhouseholds = request.form['nhouseholds']
    demo_qualtrics_function(n_households=int(nhouseholds))
    return render_template("experiment_2.html", nresidents=nresidents, nhouseholds=nhouseholds)

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