#http://127.0.0.1:8080//data?appliance=WASHING_MACHINE&m=mTest&ID=IDTest&hh_size=1&hh_type=1&frequency=2&program30=1&program40=1&program60=1&program90=1
#http://www.momeent-experiment//data?appliance=WASHING_MACHINE&peer=TRUE&m=${e://Field/m}&ID=${e:/[…]rRecode/3}&program90=${q://QID194/SelectedAnswerRecode/4}
#Public IP: 35.180.87.158
#launc: http://35.180.87.158:8080/

from flask import Flask, request, render_template, jsonify, session, abort
import os, sys, json
import datetime
import numpy as np
import boto3
import conf.credentials as conf
import secrets
import math 
from decimal import Decimal


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

#secret = secrets.token_urlsafe(32) #generate secret key for the current session
secret = "something fixed"
app = Flask(__name__, template_folder='templates')
app.secret_key = secret

#---- INITIALIZE VARIABLES ----#
n_households = 1000
usage_patterns = {'target_cycles':{'DISH_WASHER':251,
                                    'WASHING_MACHINE':100},
                  'day_prob_profiles':{'DISH_WASHER':(np.ones(24)).tolist(),  
                                       'WASHING_MACHINE':(np.ones(24)).tolist()
                                       },
                    'energy_cycle': {'DISH_WASHER': 1, 'WASHING_MACHINE':1}
                }
#TODO should be read from the csv file 
#map the values to the [0-4] range (?)         
#or add another axis on the bar_chart     
price_dict = {'morning':0.467,
              'midday':0.334, 
              'afternoon':0.346, 
              'evening':0.512,
              'night':0.375
              }

RES_dict = {'morning':47.8,
              'midday':69.9, 
              'afternoon':33.3, 
              'evening':0,
              'night':0
              }

#---- FLASK ROUTES ----#

def format_app(appliance):
    if appliance == "WASHING_MACHINE":
        return "washing machine"
    elif appliance == "DISH_WASHER":
        return "dish washer"

#---- TEMPORARY MAIN
@app.route('/') 
def _index():
    #Default args
    print()
    print(session)
    print()

    m = "1"
    ID = "test"
    hh_size = 1
    hh_type = 1
    weekly_freq = 2
    appliance = "DISH_WASHER"

    session["ID"] = ID
    session["m_field"] = m
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type
    session["n_households"] = n_households
    session["appliance"] = appliance
    session["peer"] = "TRUE"
    session["weekly_freq"] = weekly_freq

    
    return render_template("index.html", appliance=format_app(appliance))
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
        peer = request.args.get('peer')
        m = request.args.get('m')
        ID = request.args.get('ID')
        hh_size = int(request.args.get('hh_size'))
        hh_type = int(request.args.get('hh_type'))
        weekly_freq = int(request.args.get('frequency'))   
        program30 = int(request.args.get('program30'))
        program40 = int(request.args.get('program40'))
        program60 = int(request.args.get('program60'))
        program90 = int(request.args.get('program90'))
    except:
        return 'Error in extracting arguments from URL. Either missing or data type not correct.'

    year_freq = weekly_freq * 52 
    usage_patterns['target_cycles'][appliance] = year_freq
    #usage_patterns['energy_cycle'][appliance] = some_function(program30, program40, program60, program90)
    
    #save args to session
    session["appliance"] = appliance
    session["peer"] = peer
    session["ID"] = ID
    session["hh_size"] = hh_size
    session["hh_type"] = hh_type
    session["n_households"] = n_households
    session["weekly_freq"] = frequency
    
    return render_template("index.html", appliance=format_app(appliance))


@app.route('/experiment_0')
def experiment_0():
    appliance = session["appliance"]
    return render_template("experiments/experiment_0.html", appliance=format_app(appliance))

def process_data(data):
    values_dict = {}
    for d in data:
        key = d["Period"].split()[0] #remove the additional information of time between ()
        value = d["Value"]
        values_dict[key] = int(value) #values_dict has the format: {'morning': 0, 'midday': 1, 'afternoon': 2, 'evening': 3, 'night': 4}
    return values_dict

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
    n_residents = session["hh_size"]
    household_type = session["hh_type"]
    n_households = session["n_households"]
    appliance = session["appliance"]

    #generate profile from baseline values and update usage_patterns
    data = request.get_json()['baseline_data']
    values_dict = process_data(data)
    profile = generate_profile(values_dict) #ndarray(1000,24)
    usage_patterns["day_prob_profiles"][appliance] = profile.tolist()

    #invoke lambda function to calculate load
    payload = {
        "n_residents": n_residents, 
        "household_type": household_type, 
        "usage_patterns":usage_patterns, 
        "appliance":appliance,
        "n_households":n_households}
    load = get_load(payload) 

    #claculate (baseline) cost, share, and peak
    (cost, res_share, peak_load) = calculate_params(load)

    session["baseline_cost"] = cost
    session["baseline_peak_load"] = peak_load
    session["baseline_res_share"] = res_share

    response = {
        "b_cost":cost,
        "b_peak":peak_load,
        "b_share":res_share
    }
    return jsonify(response)

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
    raw_profile = np.asarray([values_dict['night']] * 6 * 6 + \
                             [values_dict['morning']] * 4 * 6 + \
                             [values_dict['midday']] * 4 * 6 + \
                             [values_dict['afternoon']] * 4 * 6 + \
                             [values_dict['evening']] * 4 * 6 + \
                             [values_dict['night']] * 2 * 6
                            )
    return raw_profile 

def min_profile_from_val_period(period_dict):
    profile = np.asarray([period_dict['night']] * 6 * 60 + \
                        [period_dict['morning']] * 4 * 60 + \
                        [period_dict['midday']] * 4 * 60+ \
                        [period_dict['afternoon']] * 4 * 60+ \
                        [period_dict['evening']] * 4 * 60+ \
                        [period_dict['night']] * 2 * 60
                        )
    return profile

@app.route('/questions_0', methods=['GET','POST'])
def questions_0():
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_0.html".format(app=appliance)
    return render_template(file_path)

@app.route('/tutorial')
def tutorial():
    return render_template("tutorial.html")

@app.route('/experiment_1')
def experiment_1():
    #retrieve answers to questions_0 here
    q0_answers = request.args
    session["q0_answers"] = q0_answers.to_dict()

    appliance = session["appliance"]
    peer = session["peer"]

    baseline_cost = session["baseline_cost"]

    data = {
        "appliance": format_app(appliance), 
        "group": peer, 
        "old_cost": math.trunc(baseline_cost)
    }
    return render_template("experiments/experiment_1.html", data=data)

@app.route('/get-diff', methods=['POST'])
def get_diff():
    n_residents = session["hh_size"]
    household_type = session["hh_type"]
    n_households = session["n_households"]
    appliance = session["appliance"]

    #generate profile from baseline values and update usage_patterns
    data = request.get_json()['data']
    values_dict = process_data(data)
    profile = generate_profile(values_dict) #ndarray(1000,24)
    usage_patterns["day_prob_profiles"][appliance] = profile.tolist()

    #invoke lambda function to calculate load
    payload = {
        "n_residents": n_residents, 
        "household_type": household_type, 
        "usage_patterns":usage_patterns, 
        "appliance":appliance,
        "n_households":n_households}
    load = get_load(payload) 

    #claculate cost, share, and peak
    (cost, res_share, peak_load) = calculate_params(load)

    baseline_cost = session["baseline_cost"]
    baseline_peak = session["baseline_peak_load"]
    baseline_share = session["baseline_res_share"]

    #Compute the % of in-decrease
    diff_cost = cost - baseline_cost
    diff_share = res_share - baseline_share
    diff_peak = peak_load - baseline_peak

    response = {
        "diff_cost": math.trunc(diff_cost), 
        "cost": math.trunc(cost),
        "diff_peak": math.trunc(diff_peak),
        "peak_load": math.trunc(peak_load),
        "res_share": math.trunc(res_share),
        "diff_share": math.trunc(diff_share)
        }

    return jsonify(response)

@app.route('/questions_1a', methods=['GET','POST'])
def questions_1a():
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_1a.html".format(app=appliance)
    return render_template(file_path)

@app.route('/questions_1b', methods=['GET','POST'])
def questions_1b():
    q1a_answers = request.args
    session["q1a_answers"] = q1a_answers.to_dict()
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_1b.html".format(app=appliance)
    return render_template(file_path)

@app.route('/experiment_2')
def experiment_2():
    q1b_answers = request.args
    session["q1b_answers"] = q1b_answers.to_dict()

    peer = session["peer"]
    appliance = session["appliance"]

    baseline_peak = session["baseline_peak_load"]

    data = {
        "appliance": format_app(appliance), 
        "group": peer, 
        "old_peak": math.trunc(baseline_peak)
    }

    return render_template("experiments/experiment_2.html", data=data)

@app.route('/questions_2a', methods=['GET','POST'])
def questions_2a():
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_2a.html".format(app=appliance)
    return render_template(file_path)

@app.route('/questions_2b', methods=['GET','POST'])
def questions_2b():
    q2a_answers = request.args
    session["q2a_answers"] = q2a_answers.to_dict()
    appliance = session["appliance"]

    file_path = "questions/{app}/questions_2b.html".format(app=appliance)
    return render_template(file_path)

@app.route('/experiment_3')
def experiment_3():
    q2b_answers = request.args
    session["q2b_answers"] = q2b_answers.to_dict()

    appliance = session["appliance"] 
    peer = session["peer"]
    baseline_share = session['baseline_res_share']

    data = {
        "appliance": format_app(appliance), 
        "group": peer, 
        "old_share": math.trunc(baseline_share)
    }
    return render_template("experiments/experiment_3.html", data=data)

@app.route('/questions_3a', methods=['GET','POST'])
def questions_3a():
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_3a.html".format(app=appliance)
    return render_template(file_path)

@app.route('/questions_3b', methods=['GET','POST'])
def questions_3b():
    q3a_answers = request.args
    session["q3a_answers"] = q3a_answers.to_dict()
    appliance = session["appliance"]

    file_path = "questions/{app}/questions_3b.html".format(app=appliance)
    return render_template(file_path)

@app.route('/experiment_4')
def experiment_4():    
    appliance = session["appliance"]

    q3b_answers = request.args
    session["q3b_answers"] = q3b_answers.to_dict()
    
    peer = session["peer"]

    baseline_cost = session["baseline_cost"]
    baseline_peak = session["baseline_peak_load"]
    baseline_share = session["baseline_res_share"]

    data = {
        "appliance": format_app(appliance), 
        "group": peer, 
        "old_cost": math.trunc(baseline_cost),
        "old_peak": math.trunc(baseline_peak),
        "old_share": math.trunc(baseline_share)
    }

    return render_template("experiments/experiment_4.html", data=data)

@app.route('/questions_final_a', methods=['GET','POST'])
def questions_final_a():  
    appliance = session["appliance"]
    file_path = "questions/{app}/questions_final_a.html".format(app=appliance)
    return render_template(file_path)

@app.route('/questions_final_b', methods=['GET','POST'])
def questions_final_b():    
    final_answers_a = request.args
    session["final_answers_a"] = final_answers_a.to_dict()
    appliance = session["appliance"]

    file_path = "questions/{app}/questions_final_b.html".format(app=appliance)
    return render_template(file_path)

@app.route('/conclusion')
def conclusion():
    final_answers_b = request.args
    session["final_answers_b"] = final_answers_b.to_dict()

    m_field = session["m_field"]
    appliance = session["appliance"]
    
    #choose table depending on appliance
    table = dynamodb.Table("MomeentData-"+appliance) 

    #Save inputs in DB
    item = {
        "m": m_field,
        "ResponseID": session["ID"],
        "hh_size": session["hh_size"],
        "hh_type": session["hh_type"],
        "frequency": session["weekly_freq"],
        "baseline_cost": session["baseline_cost"],
        "baseline_peak_load": session["baseline_peak_load"],
        "baseline_res_share": session["baseline_res_share"],
        "q0_answers" : session["q0_answers"],
        "q1a_answers" : session["q1a_answers"],
        "q1b_answers" : session["q1b_answers"],
        "q2a_answers" : session["q2a_answers"],
        "q2b_answers" : session["q2b_answers"],
        "q3a_answers" : session["q3a_answers"],
        "q3b_answers" : session["q3b_answers"],
        "final_answers_a" : session["final_answers_a"],
        "final_answers_b" : session["final_answers_b"]
    }

    item = json.loads(json.dumps(item), parse_float=Decimal)
    table.put_item(Item=item)

    return render_template("conclusion.html", appliance=format_app(appliance), m_field=m_field)


#---- MAIN CALL ----# 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)