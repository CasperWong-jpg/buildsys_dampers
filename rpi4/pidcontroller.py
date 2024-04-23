import os
import socket
import time
from datetime import datetime
import threading

# Initialize globals. TODO: Make these attributes in Controller
current_temp = 23
occupancy = 0

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

    def calc_setpoint(self,occupancy):
        self.setpoint=max(25,20+occupancy*1)

    def update(self,current_temp):
        error = self.setpoint - current_temp
        self.integral += error
        derivative = error - self.prev_error
        output = self.kp*error + self.ki*self.integral + self.kd*derivative
        self.prev_error = error
        return output


def recv_instr():
    global current_temp
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
                current_temp = float(val)
                print("temp assigned")
            elif endpoint == '/ultrasonic':
                ultrasonic = int(val)
                print("ultrasonic assigned")
            else:
                print("Bad endpoint")
        except IndexError:
            print("Bad data")
        clientConnection.close()


def actuate(output):
    pass


def main():
    global current_temp
    # Initialize controller
    controller = Controller()
    
    # Start receiving data in a separate thread
    thread = threading.Thread(target=recv_instr)
    thread.start()
    
    while True:
        controller.calc_setpoint(occupancy)
        output = controller.update(current_temp)
        actuate(output)
        timestamp =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(timestamp)
        print(f"Current Temperature:{current_temp} degreeC")
        print(f"Current Occupancy:{occupancy}")
        print(f"Actuation output:{output}\n")
        time.sleep(10)

if __name__ == "__main__":
    main()


