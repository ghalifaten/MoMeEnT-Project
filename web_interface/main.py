from flask import Flask, request, render_template, jsonify
import os, sys, json
import datetime
import numpy as np

#TODO clean URLs from args

#module_path = "/home/faten/HERUS/MoMeEnT-Project/web_interface/src/" #TODO change this
module_path = os.path.abspath(os.path.join('..'))+'/MoMeEnT-Project'
if module_path not in sys.path:
    sys.path.append(module_path)
print("\n"+module_path+"\n")
from demod_survey.examples.DEMO_SIMULATOR import demo_qualtrics_price

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
    if request.method == 'GET':
        #variables coming from the form on page questions.html
        household_type = request.args.get('household_type')
        n_residents = request.args.get('n_residents')
        machines = request.args.get('machine')
        print(household_type, n_residents, machines)
        #f = open(module_path+"/MoMeEnT-Project/web_interface/src/static/data/responses.txt", "w") #in overwrite mode
        #f.write(response1 + "\n" + response2 + "\n" + response3)
        #f.close()
        data = {
            'n_residents':n_residents,
            'household_type':household_type
        }
        return render_template("experiment_1.html", data=data)

n_households = 1000

#251, 100, values given from qualtrics
usage_patterns = {'target_cycles':{'DISH_WASHER':np.ones(n_households)*251,
                                    'WASHING_MACHINE':np.ones(n_households)*100},
                  'day_prob_profiles':{'DISH_WASHER':np.ones((n_households,24)),  #from the barchart, change vector of frq over 24 hours
                                       'WASHING_MACHINE':np.ones((n_households,24))
                                       }
                }

@app.route('/get-cost', methods=['POST'])
def get_cost():
    #variables coming from ajax request (see barchart_1.js)
    n_residents = request.get_json()['n_residents']
    household_type = request.get_json()['household_type']

    try:
        n_residents = int(n_residents)
        household_type = int(household_type)
    except:
        return 'error'
    
    subgroups = [{'n_residents': n_residents, 'household_type': household_type, 'weekday':[1,2,3,4,5]}]
    
    cost = demo_qualtrics_price(
        hh_subgroups = subgroups,
        n_hh_list = [n_households],
        start_datetime = datetime.datetime(2014, 4, 1, 0, 0, 0),
        usage_patterns = usage_patterns,
        )
        
    response = {
        'cost': cost,
    }
    return jsonify(response)


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