#http://127.0.0.1:5000//data?m=1&ID=QR001&hh_size=1&hh_type=1&frequency=2&weekly_freq=3
from flask import Flask, request, render_template, jsonify, session
import os, sys, json
import datetime
import numpy as np
import boto3
import conf.credentials as conf
import secrets

secret = secrets.token_urlsafe(32) #generate secret key for the current session

module_path = os.path.abspath(os.path.join('..'))+'/MoMeEnT-Project'
if module_path not in sys.path:
    sys.path.append(module_path)

###########
client = boto3.client('lambda',
                        region_name= conf.region,
                        aws_access_key_id=conf.aws_access_key_id,
                        aws_secret_access_key=conf.aws_secret_access_key)

dynamodb = boto3.resource('dynamodb', 
                        region_name= conf.region,
                        aws_access_key_id=conf.aws_access_key_id,
                        aws_secret_access_key=conf.aws_secret_access_key)

table = dynamodb.Table('MockMomeentProjectData')

app = Flask(__name__, template_folder='templates')
app.secret_key = secret

############
n_households = 1000
usage_patterns = {'target_cycles':{'DISH_WASHER':(np.ones(n_households)*251).tolist(),#/!\.tolist() is necessary to make ndarrays JSON serializable
                                    'WASHING_MACHINE':(np.ones(n_households)*100).tolist()},
                  'day_prob_profiles':{'DISH_WASHER':(np.ones((n_households,24))).tolist(),  
                                       'WASHING_MACHINE':(np.ones((n_households,24))).tolist()
                                       }
                }

############
@app.route('/<qualtrics_data>')
def index(qualtrics_data):
    try:
        #All args are of type str, change type here if needed.
        m = request.args.get('m')
        ID = request.args.get('ID')
        hh_size = int(request.args.get('hh_size'))
        hh_type = int(request.args.get('hh_type'))
        frequency = request.args.get('frequency')

        #TODO add weekly_freq argument to the Qualtrics link 
        weekly_freq = request.args.get('weekly_freq')
        
    except:
        return 'Error in extracting arguments from URL. Either missing or data type not correct.'

    #TODO ADD MAPPING OF weekly_freq HERE 
    #AND USE IT TO UPDATE target_cycles OF usage_patterns
    #/!\ make sure the data is JSON serializable, use .tolist() on ndarrays (see initialization example above)
    # ...

    #save usage_patterns to session
    session["usage_patterns"] = json.dumps(usage_patterns) #objects in session have to be JSON serialized (i.e converted to a string)
    
    #TODO ADD MAPPING OF hh_size and/or hh_type HERE IF NEEDED
    #....

    #save hh_size and hh_type to session for later use in the cost computation
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type

    #create an item (DB record)
    item = {
        "m": m,
        "ResponseID": ID,
        "hh_size": hh_size,
        "hh_type": hh_type,
        "frequency": frequency
    }
    #add item to DB
    table.put_item(Item=item)

    #also send item to the web_interface as a JSON object for localStorage
    qualtrics_data = json.dumps(item)

    return render_template("index.html", qualtrics_data=qualtrics_data)

@app.route('/experiment0')
def experiment0():
    return render_template("experiment_0.html")

@app.route('/questions', methods=['GET','POST'])
def questions():
    return render_template("questions.html")

@app.route('/experiment1')
def experiment_1():
    return render_template("experiment_1.html")

@app.route('/get-cost', methods=['POST'])
def get_cost():
    """
        We used to go through localStorage on the browser to move variables around different routes (using ajax)
    """
    """
    #variables coming from ajax request (see barchart_1.js)
    n_residents = request.get_json()['n_residents']
    household_type = request.get_json()['household_type']
    try:
        n_residents = int(n_residents)
        household_type = int(household_type)
    except:
        return 'error'
    """
    """
        Now we use Flask session
    """
    n_residents = session["hh_size"]
    household_type = session["hh_type"]

    #the data of the bar_charts: (coming from barChart_1.js)
    #baseline: 1st bar chart (Experience0)
    #current: 2nd bar chart (Experience1)
    baseline = request.get_json()['baseline_data']
    current = request.get_json()['current_data']

    #to be able to get the data from session in the correct data type, we have to deserialize it
    #using json.loads:
    usage_patterns = json.loads(session["usage_patterns"])

    #TODO interpolation of above data to create the day_prob_profiles field in usage_patterns
    #...
    

    #payload is the input data to the lambda function
    payload = {"n_residents": n_residents, "household_type": household_type, "usage_patterns":usage_patterns}

    #Invoke a lambda function which calculates the cost from a demod simulation           
    result = client.invoke(FunctionName=conf.lambda_function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload))
    range = result['Payload'].read()  
    api_response = json.loads(range) 
   
    return jsonify(api_response)


@app.route('/experiment2')
def experiment_2():
    #demo_qualtrics_function()
    return render_template("experiment_2.html")

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