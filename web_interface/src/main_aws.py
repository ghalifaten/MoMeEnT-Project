#http://127.0.0.1:8080//data?appliance=WASHING_MACHINE&m=${e://Field/m}&ID=${e://Field/ResponseID}&hh_size=${e://Field/household_size}&hh_type=${e://Field/household_type}&frequency=${q://QID193/SelectedChoicesRecode}&program30=${q://QID194/SelectedAnswerRecode/1}&program40=${q://QID194/SelectedAnswerRecode/2}&program60=${q://QID194/SelectedAnswerRecode/3}&program90=${q://QID194/SelectedAnswerRecode/4}
#Public IP: 35.180.87.158
#launc: http://35.180.87.158:8080/

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

table = dynamodb.Table('MockMomeentProjectData') #2 tables, change depending on type of appliance

secret = secrets.token_urlsafe(32) #generate secret key for the current session
app = Flask(__name__, template_folder='templates')
app.secret_key = secret

#---- INITIALIZE VARIABLES ----#
n_households = 1000
usage_patterns = {
                'target_cycles': {
                    'DISH_WASHER': [], 
                    'WASHING_MACHINE': []},
                'day_prob_profiles':{
                    'DISH_WASHER':[],
                    'WASHING_MACHINE': []},
                'energy_cycle': {
                    'DISH_WASHER': 0, 
                    'WASHING_MACHINE': 0}
                }

#---- FLASK ROUTES ----#
#---- TEMPORARY MAIN
@app.route('/') #without args, define default args: data?m=1&ID=QR001&hh_size=1&hh_type=1&frequency=2
def _index():
    #Default args
    m = "1"
    ID = "test"
    hh_size = 1
    hh_type = 1
    weekly_freq = 2
        
    #save usage_patterns to session
    session["usage_patterns"] = json.dumps(usage_patterns) #objects in session have to be JSON serialized (i.e converted to a string)
    
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
        "frequency": weekly_freq,
    }
    #add item to DB
    table.put_item(Item=item)

    return render_template("index.html")
#------------------------------------------
# ORIGINAL MAIN
@app.route('/<qualtrics_data>')
def index(qualtrics_data):
    """
        appliance:WM = 4 args
        appliance:DW = 6 or args 
        ==> read appliance and decide based upon
        ==> change table DB
    """

    try:
        #All args are of type str, change type here if needed.
        appliance = request.args.get('appliance')
        m = request.args.get('m')
        ID = request.args.get('ID')
        hh_size = int(request.args.get('hh_size'))
        hh_type = int(request.args.get('hh_type'))
        weekly_freq = request.args.get('frequency')   
        program30 = request.args.get('program30')
        program40 = request.args.get('program40')
        program60 = request.args.get('program60')
        program90 = request.args.get('program90')
    except:
        return 'Error in extracting arguments from URL. Either missing or data type not correct.'

    year_freq = weekly_freq * 52 #TODO check with matteo
    usage_patterns['target_cycles'][appliance] = (np.ones(n_households)*year_freq).tolist()
    #usage_patterns['energy_cycle'][appliance] = some_function(program30, program40, program60, program90)
    
    #save args to session
    session["appliance"] = appliance
    session["ID"] = ID
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type
    session["usage_patterns"] = json.dumps(usage_patterns) #objects in session have to be JSON serialized (i.e converted to a string)

    #choose which table to save data
    #if appliance == "DISH_WASHER":
        #table = dynamodb.Table('MockMomeentProjectData') 
    #else if appliance == "WASHING_MASHINE":
        #table = dynamodb.Table('MockMomeentProjectData')

    #create an item (DB record)
    item = {
        "m": m,
        "ResponseID": ID,
        "hh_size": hh_size,
        "hh_type": hh_type,
        "frequency": weekly_freq,
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
    #save values of baseline in the DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET baseline_values = :val1',
        ExpressionAttributeValues={
            ':val1': values_dict
        }
    )
    """
     we get baseline values => calculate the load with the lambda fct, and claculate the 3 vals (price ..) and save them for comparison later
     save them both on DB and on session 
     TODO: add the functions to calc these vals
    """

    #generate profiles from baseline values to update usage patterns
    profiles = generate_profile(values_dict)
    appliance = session["appliance"]
    usage_patterns = session["usage_patterns"]
    usage_patterns['day_prob_profiles'][appliance] = profiles
    session["usage_patterns"] = usage_patterns

    return {}

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


def generate_profile(values_dict):
    raw_profile = np.asarray([values_dict['night']] * 2 + \
                             [values_dict['morning']] * 4 + \
                             [values_dict['midday']] * 4 + \
                             [values_dict['afternoon']] * 4 + \
                             [values_dict['evening']] * 4 + \
                             [values_dict['night']] * 6
                            )
    profile = movingaverage(raw_profile, 3) 
    return np.asarray([profile for _ in range(1000)])


@app.route('/questions_0', methods=['GET','POST'])
def questions_0():
    return render_template("questions_0.html")



@app.route('/experiment_1')
def experiment_1():
    #retrieve answers to questions_0 here
    q0_answers = request.args

    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q0_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q0_answers.to_dict()
        }
    )

    return render_template("experiment_1.html")

@app.route('/questions_1a', methods=['GET','POST'])
def questions_1a():
    return render_template("questions_1a.html")

@app.route('/questions_1b', methods=['GET','POST'])
def questions_1b():
    q1a_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q1a_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q1a_answers.to_dict()
        }
    )

    return render_template("questions_1b.html")



@app.route('/experiment_2')
def experiment_2():
    q1b_answers = request.args

    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q1b_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q1b_answers.to_dict()
        }
    )
   
    return render_template("experiment_2.html")

@app.route('/questions_2a', methods=['GET','POST'])
def questions_2a():
    return render_template("questions_2a.html")

@app.route('/questions_2b', methods=['GET','POST'])
def questions_2b():
    q2a_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q2a_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q2a_answers.to_dict()
        }
    )

    return render_template("questions_2b.html")



@app.route('/experiment_3')
def experiment_3():
    q2b_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q2b_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q2b_answers.to_dict()
        }
    )
    
    return render_template("experiment_3.html")

@app.route('/questions_3a', methods=['GET','POST'])
def questions_3a():
    return render_template("questions_3a.html")

@app.route('/questions_3b', methods=['GET','POST'])
def questions_3b():
    q3a_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q3a_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q3a_answers.to_dict()
        }
    )
    
    return render_template("questions_3b.html")



@app.route('/experiment_4')
def experiment_4():    
    q3b_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q3b_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q3b_answers.to_dict()
        }
    )
    
    return render_template("experiment_4.html")

@app.route('/questions_4a', methods=['GET','POST'])
def questions_4a():
    return render_template("questions_4a.html")

@app.route('/questions_4b', methods=['GET','POST'])
def questions_4b():    
    q4a_answers = request.args
    
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q4a_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q4a_answers.to_dict()
        }
    )
    
    return render_template("questions_4b.html")



@app.route('/conclusion')
def conclusion():
    q4b_answers = request.args
   
    #save answers to DB
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET q4b_answers = :val1',
        ExpressionAttributeValues={
            ':val1': q4b_answers.to_dict()
        }
    )

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


    #payload is the input data to the lambda function
    payload = {
        "n_residents": n_residents, 
        "household_type": household_type, 
        "usage_patterns":usage_patterns, 
        "appliance":appliance }

    #Invoke a lambda function which calculates the cost from a demod simulation    
    #TODO make checks of hh_type and hh_size to see if they match       
    result = client.invoke(FunctionName=conf.lambda_function_name,
                InvocationType='RequestResponse',                                      
                #Payload=json.dumps(payload))
                Payload=payload)
    range = result['Payload'].read()  
    print(result)
    api_response = json.loads(range) 
    """
        lamda fct returns (1440,1) -> calc vals, and then compare, and then print out difference on "show statistics"
    """
    return jsonify(api_response)


#---- MAIN CALL ----# 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)