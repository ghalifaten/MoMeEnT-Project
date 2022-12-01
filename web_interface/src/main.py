from flask import Flask, request, render_template
import os, sys, json

#TODO clean URLs from args

#module_path = "/home/faten/HERUS/MoMeEnT-Project/web_interface/src/" #TODO change this
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

#from demod_survey.examples.DEMO_QUALTRICS_FUNCTION import demo_qualtrics_function

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/experiment0')
def experiment0():
    return render_template("experiment_0.html")

@app.route('/questions', methods=['GET','POST'])
def questions():
    return render_template("questions.html")

@app.route('/experiment1', methods=['GET', 'POST'])
def experiment_1():
    response1 = request.args.get('response1')
    response2 = request.args.get('response2')
    response3 = request.args.get('response3')
    f = open(module_path+"/MoMeEnT-Project/web_interface/src/static/data/responses.txt", "w") #in overwrite mode
    f.write(response1 + "\n" + response2 + "\n" + response3)
    f.close()
    return render_template("experiment_1.html")

@app.route('/experiment2')
def experiment_2():
    #demo_qualtrics_function()
    return render_template("experiment_2.html", nresidents=1, nhouseholds=5)

@app.route('/experiment2', methods=['POST'])
def experiment_2_post():
    nresidents = request.form['nresidents']
    nhouseholds = request.form['nhouseholds']
    #demo_qualtrics_function(n_households=int(nhouseholds))
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