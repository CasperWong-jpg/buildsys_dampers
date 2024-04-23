import os
import socket
import time
from datetime import datetime
import threading
import RPi.GPIO as GPIO
import time

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


class Controller:
    def __init__(self):
        self.kp = 15
        self.ki = 40
        self.kd = 120
        self.integral = 0.0
        self.prev_error = 0.0
        self.setpoint = 20
        self.current_temp = self.setpoint  # Assume temp at setpoint to start
        self.occupancy = 0  # Assume no occupants to start

    def calc_setpoint(self):
        self.setpoint=max(25,20+self.occupancy*1)

    def update(self) -> float:
        error = self.setpoint - self.current_temp
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp*error + self.ki*self.integral + self.kd*derivative
        self.prev_error = error
        return output


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
                controller.ultrasonic = int(val)
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


# Initialize controller as global between threads
controller = Controller()


def main():
    try:
        # Start receiving data in a separate thread
        thread = threading.Thread(target=recv_instr)
        thread.start()

        pwm.start(0) 
        
        while True:
            controller.calc_setpoint()
            output = controller.update()
            move_to_angle(45)
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


if __name__ == "__main__":
    main()

