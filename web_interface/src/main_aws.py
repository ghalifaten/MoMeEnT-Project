#http://127.0.0.1:8080//data?appliance=WASHING_MACHINE&m=mTest&ID=IDTest&hh_size=1&hh_type=1&frequency=2&program30=1&program40=1&program60=1&program90=1
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
usage_patterns = {'target_cycles':{'DISH_WASHER':(np.ones(n_households)*251).tolist(),
                                    'WASHING_MACHINE':(np.ones(n_households)*100).tolist()},
                  'day_prob_profiles':{'DISH_WASHER':(np.ones((n_households,24))).tolist(),  
                                       'WASHING_MACHINE':(np.ones((n_households,24))).tolist()
                                       },
                    'energy_cycle': {'DISH_WASHER': 1, 'WASHING_MACHINE':1}
                }
price_dict = {'morning':0.200439918,
              'midday':0.264827651, 
              'afternoon':0.21111789, 
              'evening':0.220015123,
              'night':0.242899301
              }
RES_dict = {'morning':47.8,
              'midday':69.9, 
              'afternoon':33.3, 
              'evening':0,
              'night':0
              }

#---- FLASK ROUTES ----#
#---- TEMPORARY MAIN
@app.route('/') 
def _index():
    #Default args
    m = "1"
    ID = "test"
    hh_size = 1
    hh_type = 1
    weekly_freq = 2

    session["ID"] = ID
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type
    session["n_households"] = n_households
    session["appliance"] = "WASHING_MACHINE"

    #Save inputs in DB
    item = {
        "m": m,
        "ResponseID": ID,
        "hh_size": hh_size,
        "hh_type": hh_type,
        "frequency": weekly_freq,
    }
    table.put_item(Item=item)
    session.modified = True
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
        m = request.args.get('m')
        ID = request.args.get('ID')
        hh_size = int(request.args.get('hh_size'))
        hh_type = int(request.args.get('hh_type'))
        appliance = request.args.get('appliance')
        weekly_freq = int(request.args.get('frequency'))   
        program30 = int(request.args.get('program30'))
        program40 = int(request.args.get('program40'))
        program60 = int(request.args.get('program60'))
        program90 = int(request.args.get('program90'))
    except:
        return 'Error in extracting arguments from URL. Either missing or data type not correct.'

    year_freq = weekly_freq * 52 
    usage_patterns['target_cycles'][appliance] = (np.ones(n_households)*year_freq).tolist()
    #usage_patterns['energy_cycle'][appliance] = some_function(program30, program40, program60, program90)
    
    #save args to session
    session["ID"] = ID
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type
    session["n_households"] = n_households
    session["appliance"] = appliance

    #choose which table to save data
    #if appliance == "DISH_WASHER":
        #table = dynamodb.Table('MockMomeentProjectData') 
    #else if appliance == "WASHING_MASHINE":
        #table = dynamodb.Table('MockMomeentProjectData')

    #Save inputs in DB
    item = {
        "m": m,
        "ResponseID": ID,
        "hh_size": hh_size,
        "hh_type": hh_type,
        "frequency": weekly_freq,
    }
    table.put_item(Item=item)

    return render_template("index.html")


@app.route('/experiment_0')
def experiment_0():
    return render_template("experiment_0.html")

def process_data(data):
    values_dict = {}
    for d in data:
        key = d["Period"].split()[0] #remove the additional information of time between ()
        value = d["Value"]
        values_dict[key] = int(value) #values_dict has the format: {'morning': 0, 'midday': 1, 'afternoon': 2, 'evening': 3, 'night': 4}
    return values_dict

#TODO maybe change name of function
def calculate_params(load):
    price = min_profile_from_val_period(price_dict)
    unit_conv = 1 / 60 / 1000 * 365.25 
    cost = np.sum(load * price * unit_conv)
    local_generation = min_profile_from_val_period(RES_dict)
    res_share = np.sum(load * local_generation / np.sum(load))
    peak_load = np.sum(load[14*60:18*60])/np.sum(load)*100
    return (cost, res_share, peak_load)

@app.route('/get-baseline-values', methods=['POST'])
def get_baseline_values():
    data = request.get_json()['baseline_data']
    values_dict = process_data(data)
    
    #generate profile from baseline values and update usage_patterns
    profile = generate_profile(values_dict) #ndarray(1000,24)
    usage_patterns["day_prob_profiles"]["WASHING_MACHINE"] = profile.tolist()

    n_residents = session["hh_size"]
    household_type = session["hh_type"]
    appliance = session["appliance"]
    n_households = session["n_households"]

    payload = {
        "n_residents": n_residents, 
        "household_type": household_type, 
        "usage_patterns":usage_patterns, 
        "appliance":appliance,
        "n_households":n_households}

    load = get_load(payload) 

    #claculate (baseline) cost, share, and peak
    (cost, res_share, peak_load) = calculate_params(load)

    #save baseline parameters to session for later comparison
    session["baseline_cost"] = str(cost)
    session["baseline_res_share"] = str(res_share)
    session["baseline_peak_load"] = str(peak_load)

    print('The yearly bill is {:0.1f}€'.format(cost))
    print('The share of local generation is {:0.1f}%'.format(res_share)) 
    print('The share of energy consumed during peak period is {:0.1f}%'.format(peak_load)) 

    #save values of baseline in DB
    #Float64 is not supported in DynamoDB. Values are stored as string
    table.update_item(
        Key={
            'ResponseID': session["ID"]
        },
        UpdateExpression='SET baseline_values = :val1, cost = :val2, res_share = :val3, peak_load = :val4',
        ExpressionAttributeValues={
            ':val1': values_dict,
            ':val2': str(cost),
            ':val3': str(res_share),
            ':val4': str(peak_load)
        }
    )
    session.modified = True
    print()
    print(session.keys())
    print()
    return load


def get_load(payload):   
    result = client.invoke(
                FunctionName=conf.lambda_function_name,
                InvocationType='RequestResponse',                                      
                Payload=json.dumps(payload)
                )
    range = result['Payload'].read()  
    response = json.loads(range) 
    return response['load']

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
    return np.asarray([profile for _ in range(n_households)])

def min_profile_from_val_period(period_dict):
    profile = np.asarray([period_dict['night']] * 2 * 60 + \
                        [period_dict['morning']] * 4 * 60 + \
                        [period_dict['midday']] * 4 * 60+ \
                        [period_dict['afternoon']] * 4 * 60+ \
                        [period_dict['evening']] * 4 * 60+ \
                        [period_dict['night']] * 6 * 60
                        )
    return profile

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

@app.route('/get-cost', methods=['POST'])
def get_cost():
    print()
    print(session.keys())
    print()
    data = request.get_json()['data']
    values_dict = process_data(data)
    
    #generate profile from baseline values and update usage_patterns
    profile = generate_profile(values_dict) #ndarray(1000,24)
    usage_patterns["day_prob_profiles"]["WASHING_MACHINE"] = profile.tolist()

    n_residents = session["hh_size"]
    household_type = session["hh_type"]
    appliance = session["appliance"]
    n_households = session["n_households"]

    payload = {
        "n_residents": n_residents, 
        "household_type": household_type, 
        "usage_patterns":usage_patterns, 
        "appliance":appliance,
        "n_households":n_households}

    load = get_load(payload) 

    #claculate (baseline) cost, share, and peak
    (cost, res_share, peak_load) = calculate_params(load)

    #Compare with baseline values

    diff_cost = session["baseline_cost"] - cost
    diff_res = session["baseline_res_share"] - res_share
    diff_peak = session["baseline_peak_load"] - peak_load

    print('The yearly bill is {:0.1f}€'.format(diff_cost))
    print('The share of local generation is {:0.1f}%'.format(diff_res)) 
    print('The share of energy consumed during peak period is {:0.1f}%'.format(diff_peak)) 
    return {"diff_cost": diff_cost, "diff_res": diff_res, "diff_peak": diff_peak}

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




#---- MAIN CALL ----# 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)