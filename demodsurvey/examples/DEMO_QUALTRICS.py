"""
DEMO FILE FOR QUALTRICS API INTEGRATION
"""

import os
import sys

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import datetime
from datetime import timedelta
import time

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)


from demod.datasets.Germany.loader import GermanDataHerus

from DEMO_SIMULATOR import demo_qualtrics_price


#%% INPUTS & INITIALIZATION

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

# subgroups = [{'n_residents': 1, 'household_type': 1, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 2, 'household_type': 2, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 2, 'household_type': 3, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 3, 'household_type': 3, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 3, 'household_type': 4, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 4, 'household_type': 4, 'weekday':[1,2,3,4,5]},
#              {'n_residents': 5, 'household_type': 4, 'weekday':[1,2,3,4,5]}]
# hh_subgroups = [subgroups[0]]
# n_hh_list = [n_households]
# type of hh: 1 single, 2 couple without children, 3 single parent, 4 couple with childrens

# household socio-demographic
n_households = 1000
subgroups = [{'n_residents': 1, 'household_type': 1, 'weekday':[1,2,3,4,5]}]

# appliance usage pattern 
usage_patterns = {'target_cycles':{'DISH_WASHER':np.ones(n_households)*251,
                                    'WASHING_MACHINE':np.ones(n_households)*100},
                  'day_prob_profiles':{'DISH_WASHER':np.ones((n_households,24)),
                                       'WASHING_MACHINE':np.ones((n_households,24))
                                       }
                  }


#%% SIMULATION

# run the simulation
start = time.time()

cost = demo_qualtrics_price(
        hh_subgroups = subgroups,        
        n_hh_list = [n_households],
        start_datetime = datetime.datetime(2014, 4, 1, 0, 0, 0),
        data = GermanDataHerus(version='v1.1'),
        usage_patterns = usage_patterns,
        )

print(f'The yearly bill is {cost} €')

end = time.time()
print(f'The simulation took {end - start} s')


