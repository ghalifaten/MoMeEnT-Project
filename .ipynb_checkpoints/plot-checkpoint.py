import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import json

# Data to be written
baseline_data = {
        'Morning':{'value':20},
        'Midday':{'value':35},
        'Afternoon':{'value':30},
        'Evening':{'value':80},
       }

# Writing to sample.json
with open("data.json", "w") as outfile:
    json.dump(baseline_data, outfile)
    
def get_value(dct):
    if 'value' in dct:
        return dct['value']
    return dct

with open("data.json") as json_data:
    data = json_data.read()
    data = json.loads(data, object_hook=get_value)

# The parametrized function to be plotted
def f(x,y):
    return y

values = [v for k,v in data.items() if v!={}]
keys = [k for k,v in data.items() if v!={}]
initial_value = 40

ind = np.arange(len(keys))    # the x locations for the groups
width = 0.35       # the width of the bars: can also be len(x) sequence


fig, ax = plt.subplots(figsize=(15, 8))
plt.subplots_adjust(bottom=0.4)
bar = ax.bar(ind, values, width, color='blue')

ax.set_ylabel('Values')
ax.set_title('Change of energy consumption throughout the day')
plt.xticks(ind, keys)
ax.set_yticks(np.arange(0, np.max(values)+1, 10))

#Add Slider - morning
axfreq = fig.add_axes([0.19, 0, 0.01, 0.3]) #dimensions
morning_slider = Slider(
    ax=axfreq,
    label='',
    valmin=0,
    valmax=80,
    valinit=initial_value,
    orientation='vertical'
)

# The function to be called anytime a slider's value changes
def update(val):
    bar.set_ydata(f(x,morning_slider.val))
    fig.canvas.draw_idle()


# register the update function with each slider
morning_slider.on_changed(update)

# Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.8, 0, 0.1, 0.04])
button = Button(resetax, 'Reset', hovercolor='0.975')

def reset(event):
    morning_slider.reset()

button.on_clicked(reset)

plt.show()
