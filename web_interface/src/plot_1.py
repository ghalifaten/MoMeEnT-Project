import os
import sys

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta

import base64
from io import BytesIO

module_path = os.path.abspath(os.path.join('../../demod_survey')) #TODO change this
if module_path not in sys.path:
    sys.path.append(module_path)


from demod.datasets.Germany.loader import GermanDataHerus

from demod.simulators.appliance_simulators import (ActivityApplianceSimulator, 
                                                   ProbabilisticActivityAppliancesSimulator, 
                                                   OccupancyApplianceSimulator,
                                                   )
from demod.simulators.base_simulators import SimLogger
from demod.simulators.activity_simulators import SubgroupsIndividualsActivitySimulator, SemiMarkovSimulator

def plot_function(n_households = 5):

    #%% INPUTS & INITIALIZATION

    # inputs
    start_datetime = datetime.datetime(2014, 4, 1, 0, 0, 0)
    day = ['MO','TU','WE','TH','FR','SA','SU'][start_datetime.weekday()]

    """
    For the time being, we can simplify the problem and consider only the type of 
    household and the number of residents as input. The input dictionary is as follows:
        - 'n_residents' : int from 1 to 5
        - 'household_type' : int from 1 to 5
            1 = One person household
            2 = Couple without kid
            3 = Single Parent with at least one kid under 18 and the other under 27
            4 = Couple with at least one kid under 18 and the other under 27
            5 = Others
    """
    n_residents = 1
    household_type = 1
    hh_subgroups = [{'n_residents':n_residents, 'household_type':household_type}] # , 
    n_hh_list = [n_households]
    power_consumption = {} #important to keep this outside the function to avoid incrementation with every http request

    data = GermanDataHerus(version='v1.1')

    # initialization

    # Simulates household activities
    sim_bott = SubgroupsIndividualsActivitySimulator(
        hh_subgroups,
        n_hh_list,
        logger=SimLogger('get_occupancy', 'get_active_occupancy', 'get_activity_states'),
        subsimulator=SemiMarkovSimulator,
        data=data,
        start_datetime = start_datetime,
        use_week_ends_days=True
    )

    # Simulates activity-based appliances 
    sim_app_bott = ActivityApplianceSimulator(
        n_households, initial_activities_dict=sim_bott.get_activity_states(),
        data=data,
        start_datetime = start_datetime,
        equipped_sampling_algo="set_defined", # basic, subgroup, set_defined
        equipped_set_defined=np.ones((n_households,10), dtype=bool), # pass the available appliances
        subgroups_list=hh_subgroups,
        n_households_list=n_hh_list,
        logger=SimLogger('get_current_power_consumptions', aggregated=False)
    )

    # Simulates probablitstics appliances 
    sim_prob_app_bott = ProbabilisticActivityAppliancesSimulator(
        n_households, initial_activities_dict=sim_bott.get_activity_states(),
        data=data,
        start_datetime = start_datetime,
        equipped_sampling_algo="set_defined", # basic, subgroup, set_defined
        equipped_set_defined=np.ones((n_households,22), dtype=bool), # pass the available appliances
        subgroups_list=hh_subgroups,
        n_households_list=n_hh_list,
        logger=SimLogger('get_current_power_consumptions', aggregated=False)
    )

    
    #%% SIMULATION 

    # run the simulation for 1 day
    updated_appliance_set = None
    for i in range(144):
        for i in range(10):   
            # update electricity consumption every min
            sim_app_bott.step(sim_bott.get_activity_states())
            sim_prob_app_bott.step(sim_bott.get_activity_states())
        # update household activitiesevery 10 min  
        sim_bott.step()

    # store the results
    occupancy_states = sim_bott.logger.get('get_occupancy')
    active_occupancy_states = sim_bott.logger.get('get_active_occupancy')
    power_consumption['activity dependent'] = sim_app_bott.logger.get('get_current_power_consumptions') 
    power_consumption['probabilistic'] = sim_prob_app_bott.logger.get('get_current_power_consumptions')


    #%% PLOTTING

    fig, ax = plt.subplots()

    x = range(144*10)

    ax.plot(x, power_consumption['activity dependent'].sum(axis=(1,2)) + power_consumption['probabilistic'].sum(axis=(1,2)),
            label='total activity-based',
            color='dodgerblue'
            ) 
    #ax.set_xlim(0,143)
    ax.set_title('Aggregated total')
    ax.legend()

    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    plot = base64.b64encode(buf.getbuffer()).decode("ascii")
    #return f"<img src='data:image/png;base64,{data}'/>"
    return plot 