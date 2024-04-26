# MPCC or MPPI
import numpy as np
from scipy.optimize import curve_fit
import datetime
import time
import threading
import socket
import RPi.GPIO as GPIO

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin to which the servo is connected
servo_pin = 17

# Set the PWM frequency (Hz)
PWM_freq = 50

# Set the PWM duty cycle range
PWM_duty_min = 5
PWM_duty_max = 10

# Initialize PWM pin
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, PWM_freq)

# Start server
SERVER = "172.26.160.113"
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))
server.listen(1)

def base_function(t, tau, dead_band_upper):
    return dead_band_upper*np.exp(-t/tau)

def estimate_RC(temperature):
    t = np.arange(len(temperature))
    popt, pcov = curve_fit(base_function, t, np.array(temperature))
    return popt[0]

def is_occupied(occupancy):
    return (occupancy != 0)

def control_fn(curr_time, occupied, schedule, tau, current_temp, dead_band_upper, dead_band_lower):
    if schedule[curr_time + tau] == 1:
        signal = 1
    elif current_temp < dead_band_lower:
        signal = 1
    elif occupied:
        signal = 1
    elif current_temp > dead_band_upper:
        signal = 0
    else:
        signal = 0
    return signal

def convert_to_hour(time, sampling_frequency):
    return time/(60*60*sampling_frequency)

class RC_Controller:
    def __init__(self, schedule):
        self.setpoint = 21
        self.dead_band_upper = 22
        self.dead_band_lower = 20

        self.current_temp = self.setpoint  # Assume temp at setpoint to start
        self.occupancy = 0  # Assume no occupants to start

        self.schedule = schedule
        self.hist_temperature = []

        self.sampling_frequency = 1/30
        self.tau = 10 # Initial guess of the time constant = 10hr for the room

        self.flag = 0

    def get_tau(self):
        tau = estimate_RC(self.hist_temperature)
        return tau
    
    def update(self):

        currentDateAndTime = datetime.datetime.now()
        currentTime = currentDateAndTime.hour
        currentDate = currentDateAndTime.date()
        day, hour = (currentDate.isoweekday()-1), currentTime

        curr_time = 24*day + hour
        
        if len(self.hist_temperature) > 60*(60*self.sampling_frequency): # the value of tau is only calculated and update if the hist_temperature recorded is more than an hour long
            tau = self.get_tau()
            tau = convert_to_hour(tau, self.sampling_frequency)
            self.tau = tau

        if self.current_temp >= self.dead_band_upper:
            self.flag = 1
        elif self.current_temp <= self.dead_band_lower:
            self.flag = 0

        if self.flag == 1:
            self.hist_temperature.append(self.current_temp)
        if self.flag == 0:
            self.hist_temperature = []

        occupied = is_occupied(self.occupancy)
        control = control_fn(curr_time, occupied, self.schedule, self.tau, self.current_temp, self.dead_band_upper, self.dead_band_lower)

        return control

def recv_instr():
    global controller 
    print("Waiting for client request..")
    while True:
        clientConnection, clientAddress = server.accept()
        print("Connected clinet :" , clientAddress)
        data = (clientConnection.recv(1024)).decode()
        print("From Client :" , data)
        try:
            endpoint, val = data.split()
            print(endpoint)
            if endpoint == '/temp':
                controller.current_temp = float(val)
                print("temp assigned")
            elif endpoint == '/ultrasonic':
                controller.occupancy = int(val)
                print("ultrasonic assigned")
            else:
                print("Bad endpoint")
        except IndexError:
            print("Bad data")
        clientConnection.close()


# Function to convert angle to PWM duty cycle
def angle_to_duty_cycle(angle):
    duty_cycle = (angle / 90.0) * (PWM_duty_max - PWM_duty_min) + PWM_duty_min
    return duty_cycle

# Function to move the servo to a specified angle
def move_to_angle(angle):
    assert 0 <= angle <= 90

    duty_cycle = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust this delay as needed for your servo
    # pwm.ChangeDutyCycle(0)  # Stop sending PWM signal

def main():
    # array of size 168 = number of hours in a week
    schedule = [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
                1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
                1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1]
    # Initialize controller as global between threads
    controller = RC_Controller(schedule)
    try:
        # Start receiving data in a separate thread
        thread = threading.Thread(target=recv_instr)
        thread.start()

        pwm.start(0) 
        
        while True:
            output = controller.update()
            move_to_angle(90*output) # Binary control
            timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(timestamp)
            print(f"Current Temperature:{controller.current_temp} degreeC")
            print(f"Current Occupancy:{controller.occupancy}")
            print(f"Actuation output:{output}\n")
            time.sleep(30)

    except KeyboardInterrupt:
        # Cleanup GPIO on interruption
        pwm.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
    # # say the set point is 23 celcius, assuming a 2 degree dead band (we can change it to 1 degree as well)
    # dead_band_upper = 25
    # dead_band_lower = 21
    # sampling_frequency = 1/30 # Assuming sampling every 30 seconds
    # schedule = [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
    #             1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
    #             1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,1,1,1,1,1,
    #             1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,
    #             1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,
    #             1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    #             0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,] # array of size 168 = number of hours in a week
    # day, hour = 3, 22

    # # temperature data is assumed to start at the dead_band_upper end and the vent is closed
    # occupancy = 0 # binary value fetched from the sensor say using a get_curr_occupany from the RPI4
    # temperature_data = pd.read('temperature.csv') 

    # # Convert temperature_data into chunks of decaying exponentials
    # # we can avoid this by storing the values of temperature only when the vent is closed and the temperature reached 25 outside

    # # Let's assume that the temperature data fed into the estimate_RC is strictly decaying
    # tau = estimate_RC(temperature_data)
    # tau = convert_to_hour(tau, sampling_frequency)

    # # Control part of it once tau value is estimated by fitting an exponential decay function to the temperature data
    # occupied = is_occupied(occupancy)
    # curr_time = 24*day + hour

    # control = control_fn(curr_time, occupied, schedule, tau)