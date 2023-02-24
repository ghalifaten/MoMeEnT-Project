#http://127.0.0.1:5000//data?m=1&ID=QR001&hh_size=1&hh_type=1&frequency=2
from flask import Flask, request, render_template, jsonify, session
import os, sys, json
import datetime
import numpy as np
import boto3
import conf.credentials as conf
import secrets

#---- SET UP PATH ----#
module_path = os.path.abspath(os.path.join('..'))+'/MoMeEnT-Project'
if module_path not in sys.path:
    sys.path.append(module_path)

#---- SET UP CONNECTIONS ----#
client = boto3.client('lambda',
                        region_name= conf.region,
                        aws_access_key_id=conf.aws_access_key_id,
                        aws_secret_access_key=conf.aws_secret_access_key)

dynamodb = boto3.resource('dynamodb', 
                        region_name= conf.region,
                        aws_access_key_id=conf.aws_access_key_id,
                        aws_secret_access_key=conf.aws_secret_access_key)

table = dynamodb.Table('MockMomeentProjectData')

secret = secrets.token_urlsafe(32) #generate secret key for the current session
app = Flask(__name__, template_folder='templates')
app.secret_key = secret

#---- INITIALIZE VARIABLES ----#
n_households = 1000
usage_patterns = {'target_cycles':{'DISH_WASHER':(np.ones(n_households)*251).tolist(),#/!\.tolist() is necessary to make ndarrays JSON serializable
                                    'WASHING_MACHINE':(np.ones(n_households)*100).tolist()},
                  'day_prob_profiles':{'DISH_WASHER':(np.ones((n_households,24))).tolist(),  
                                       'WASHING_MACHINE':(np.ones((n_households,24))).tolist()
                                       }
                }

#---- FLASK ROUTES ----#
@app.route('/<qualtrics_data>')
def index(qualtrics_data):
    try:
        #All args are of type str, change type here if needed.
        m = request.args.get('m')
        ID = request.args.get('ID')
        hh_size = int(request.args.get('hh_size'))
        hh_type = int(request.args.get('hh_type'))
        weekly_freq = request.args.get('frequency')
        
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

    #save responseID for further DB updates
    session["ID"] = ID

    #create an item (DB record)
    item = {
        "m": m,
        "ResponseID": ID,
        "hh_size": hh_size,
        "hh_type": hh_type,
        "frequency": weekly_freq
    }
    #add item to DB
    table.put_item(Item=item)

    return render_template("index.html")



@app.route('/experiment_0')
def experiment_0():
    return render_template("experiment_0.html")

@app.route('/get-baseline-values', methods=['POST'])
def get_baseline_values():
    values_dict = {}
    baseline = request.get_json()['baseline_data']
    for d in baseline:
        key = d["Period"].split()[0] #remove the additional information of time between ()
        value = d["Value"]
        values_dict[key] = int(value)
    """
        values_dict has the format: {'morning': 0, 'midday': 1, 'afternoon': 2, 'evening': 3, 'night': 4}
    """

    profile = generate_profile()

    return 0

def generate_profile():
    #TODO make the calcluations to generate the profile
    return profile


@app.route('/questions_0', methods=['GET','POST'])
def questions_0():
    return render_template("questions_0.html")



@app.route('/experiment_1')
def experiment_1():
    #retrieve answers to questions_0 here
    q0_answers = request.args
    #/!\ args for now look like this: 
    #ImmutableMultiDict([('q0_r1', '1'), ('q0_r2', 'hello'), ('q0_r3', 'washmachine'), ('q0_r3', 'dryer'), ('q0_r3', 'fridge')])
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record

    return render_template("experiment_1.html")

@app.route('/questions_1a', methods=['GET','POST'])
def questions_1a():
    return render_template("questions_1a.html")

@app.route('/questions_1b', methods=['GET','POST'])
def questions_1b():
    q1a_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB with the corresponding ID from the session
    #ResponseID = session["ID"]
    #table.set_item(ResponseID ...) 

    return render_template("questions_1b.html")



@app.route('/experiment_2')
def experiment_2():
    q1b_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("experiment_2.html")

@app.route('/questions_2a', methods=['GET','POST'])
def questions_2a():
    return render_template("questions_2a.html")

@app.route('/questions_2b', methods=['GET','POST'])
def questions_2b():
    q2a_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record

    return render_template("questions_2b.html")



@app.route('/experiment_3')
def experiment_3():
    q2b_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("experiment_3.html")

@app.route('/questions_3a', methods=['GET','POST'])
def questions_3a():
    return render_template("questions_3a.html")

@app.route('/questions_3b', methods=['GET','POST'])
def questions_3b():
    q3a_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("questions_3b.html")



@app.route('/experiment_4')
def experiment_4():    
    q3b_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("experiment_4.html")

@app.route('/questions_4a', methods=['GET','POST'])
def questions_4a():
    return render_template("questions_4a.html")

@app.route('/questions_4b', methods=['GET','POST'])
def questions_4b():    
    q4a_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("questions_4b.html")



@app.route('/conclusion')
def conclusion():
    q4b_answers = request.args
    #TODO manipulate answers here to get the desired type
    #save answers to DB
    #table.set_item() #need the responseID to set the corresponding record
    
    return render_template("conclusion.html")


#---- COST FUNCTION ----# (TO BE CALLED LOAD FUNCITON LATER)
@app.route('/get-cost', methods=['POST'])
def get_cost():
    #retrieve hh_size and hh_type from session
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


#---- MAIN CALL ----# 
if __name__ == "__main__":
    app.run(debug=True)