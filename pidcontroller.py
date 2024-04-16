import os
import socket
import time
from datetime import datetime

class Controller:
	def __init__(self):
		self.kp = 15
		self.ki = 40
		self.kd = 120
		self.integral = 0.0
		self.prev_error = 0.0
		self.setpoint = 20

	def calc_setpoint(self,occupancy):
		self.setpoint=max(25,20+occupancy*1)

	def update(self,current_temp)
		error = self.setpoint - current_temp
		self.integral += error
		derivative = error - self.prev_error
		output = self.kp*error + self.ki*self.integral + self.kd*derivative
		self.prev_error = error
		return output

def preprocess_temp():
	pass

def preprocess_occu():
	pass

def actuate(output):
	pass

def main():
	controller = Controller()
	while True:
		current_temp = preprocess_temp()
		occupancy = preprocess_occu()
		controller.calc_setpoint(occupancy)
		output = controller.update(current_temp)
		actuate(output)
		timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		print(timestamp)
		print(f"Current Temperature:{current_temp} degreeC")
		print(f"Current Occupancy:{occupancy}")
		print(f"Actuation output:{output}\n")
		time.sleep(30)

 if __name__ == "main":
	main()

