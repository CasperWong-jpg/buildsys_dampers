import network
import socket
from time import sleep
from machine import Pin, ADC

SERVER="172.26.160.113"  # RPi IP Address
PORT=8080
ssid = "CMU-DEVICE"
adc = ADC(4)  # Internal temperature sensor

# Register device - search web for "CMU Device"
# Need to acquire MAC address through Thonny (hardware address of device)

def connect():
    # Connect to WLAN and return IP address
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, security=0)
    while wlan.isconnected() == False:
        print('Waiting...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    hostname = network.hostname()
    print(f'Connected on {ip} with hostname {hostname}')
    return ip

def open_socket(ip):
    # Open a socket at this IP address
    address = (SERVER, PORT)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return(connection)

def get_temp():
    # Return temperature in Celsius
    temp = ADC(4)
    ADC_voltage = adc.read_u16() * (3.3 / (65536))  # 3.3V, 16 bit ADC
    temp_celsius = 27 - (ADC_voltage - 0.706)/0.001721
    return temp_celsius

def serve(connection):
    # Send temperature every 30 seconds to RPi
    temperature = 0
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((SERVER, PORT))
        temperature = get_temp()
        print(f"/temp {temperature}")
        client.send(str(f"/temp {temperature}"))
        client.close()
        sleep(30)
    
try:    
    ip = connect()
    
    # Turn on LED to show it is connected to internet
    led = Pin('LED', Pin.OUT)
    led(1)
    
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()


