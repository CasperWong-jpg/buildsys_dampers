# MPCC or MPPI
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

def base_function(t, tau, dead_band_upper):
    return dead_band_upper*np.exp(-t/tau)

def estimate_RC(temperature):
    t = np.arange(len(temperature))
    popt, pcov = curve_fit(base_function, t, temperature_data)
    return popt[0]

def chunker(temperature_data, dead_band_upper, dead_band_lower):
    pass

def is_occupied(occupancy):
    return (occupancy != 0)

def control_fn(curr_time, occupied, schedule, tau):
    if schedule[curr_time + tau] == 1:
        signal = True
    else:
        if occupied:
            signal = True
        else:
            signal = False
    return signal

def convert_to_hour(time, sampling_frequency):
    return time/(60*60*sampling_frequency)

if __name__ == '__main__':

    # say the set point is 23 celcius, assuming a 2 degree dead band (we can change it to 1 degree as well)
    dead_band_upper = 25
    dead_band_lower = 21
    sampling_frequency = 1/30 # Assuming sampling every 30 seconds
    schedule = [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
                1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,] # array of size 168 = number of hours in a week
    day, hour = 3, 22

    # temperature data is assumed to start at the dead_band_upper end and the vent is closed
    occupancy = 0 # binary value fetched from the sensor say using a get_curr_occupany from the RPI4
    temperature_data = pd.read('temperature.csv') 

    # Convert temperature_data into chunks of decaying exponentials
    chunked_temp_data = chunker(temperature_data, dead_band_upper, dead_band_lower) 
    # we can avoid this by storing the values of temperature only when the vent is closed and the temperature reached 25 outside

    # Let's assume that the temperature data fed into the estimate_RC is strictly decaying
    tau = estimate_RC(chunked_temp_data)
    tau = convert_to_hour(tau, sampling_frequency)

    # Control part of it once tau value is estimated by fitting an exponential decay function to the temperature data
    occupied = is_occupied(occupancy)
    curr_time = 24*day + hour

    control = control_fn(curr_time, occupied, schedule, tau)