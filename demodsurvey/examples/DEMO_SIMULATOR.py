import os
import sys
import json
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import time
    
module_path = os.path.dirname(os.path.dirname(__file__))
if module_path not in sys.path:
    sys.path.append(module_path)

from demod.datasets.Germany.loader import GermanDataHerus
from demod.simulators.appliance_simulators import (ActivityApplianceSimulator, 
                                                   ProbabilisticActivityAppliancesSimulator, 
                                                   AvailableOccupancyApplianceSimulator)
from demod.simulators.base_simulators import SimLogger
from demod.simulators.activity_simulators import SubgroupsIndividualsActivitySimulator, SemiMarkovSimulator, MarkovChain1rstOrder


def lambda_handler(event, context=None):
    st = time.time()
    n_residents = event['n_residents']
    household_type = event['household_type']
    n_households = 1000
    
    subgroups = [{'n_residents': n_residents, 'household_type': household_type, 'weekday':[1,2,3,4,5]}]
    
    usage_patterns = {'target_cycles':{'DISH_WASHER':np.ones(n_households)*251,
    					'WASHING_MACHINE':np.ones(n_households)*100},
    			'day_prob_profiles':{'DISH_WASHER':np.ones((n_households,24)),
    						'WASHING_MACHINE':np.ones((n_households,24))
    			}
    		}

    cost = demo_qualtrics_price(hh_subgroups=subgroups, usage_patterns=usage_patterns)

    print(time.time() - st, " seconds.")
    return {
        "cost": cost
    }
    


def demo_qualtrics_price(
        hh_subgroups : list,        
        n_hh_list : list = [1000],
        start_datetime : datetime.datetime = datetime.datetime(2014, 4, 1, 0, 0, 0),
        data = GermanDataHerus(version='v1.1'),
        usage_patterns : dict = None,
        ) -> float:
    
    
    # initialization activitity simulatore
    sim_act = SubgroupsIndividualsActivitySimulator(
        hh_subgroups,
        n_hh_list,
        subsimulator=SemiMarkovSimulator,
        data=data,
        start_datetime = start_datetime,
        use_week_ends_days=True
    )
    
    # initialization appliance simulator
    wet_appliances = np.zeros((n_hh_list[0],32), dtype=bool)
    wet_appliances[:,(-7,-6,-5)] = True
    sim_app = AvailableOccupancyApplianceSimulator(
        subgroups_list=hh_subgroups,  
        initial_active_occupancy=sim_act.get_activity_states()['other'],
        start_datetime=start_datetime,
        n_households_list=n_hh_list,
        equipped_sampling_algo="set_defined",
        equipped_set_defined=wet_appliances,
        data=data,
        usage_patterns=usage_patterns,
        logger=SimLogger('get_current_power_consumptions', aggregated=False)
    )
    
    # run the simulation for 1 day
    for i in range(144):

        for i in range(10):       
            # update load every 1 min
            sim_app.step(sim_act.get_activity_states()['other']+
                         sim_act.get_activity_states()['dishwashing']+
                         sim_act.get_activity_states()['laundry']
                         )
        # update activity every 10 min    
        sim_act.step()
    
    # retrieve the simulated load profile 
    # DIM0: min of the day, DIM1: households, DIM2: appliances
    loads = sim_app.logger.get('get_current_power_consumptions')
    
    avg_load = {}
    avg_load['DISH_WASHER'] = np.mean(loads[:,:,-7], axis=1)
    avg_load['DRYER'] = np.mean(loads[:,:,-6], axis=1)
    avg_load['WASHING_MACHINE'] = np.mean(loads[:,:,-5], axis=1)
    
    # price profile in €/kWh per each min of the day
    price = np.ones(10*6*24) * 0.4
    
    # conversion factor from Wmin/day to kWh/y
    unit_conv = 1 / 60 / 1000 * 365.25 
    
    cost = np.sum(avg_load['DISH_WASHER'] * price * unit_conv)
    
    return cost

if __name__ == "__main__":
    event = {
        "n_residents": 1,
        "household_type": 1
    }
    lambda_handler(event)