import time
import socket
import threading

# Cite https://net-informations.com/python/net/socket.htm

SERVER="172.26.160.113"
PORT=8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER, PORT))
server.listen(1)
print("Server started")

def recv_instr():
    global temperature
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
                temperature = float(val)
                print("temp assigned")
            elif endpoint == '/ultrasonic':
                ultrasonic = int(val)
                print("ultrasonic assigned")
            else:
                print("Bad endpoint")
        except IndexError:
            print("Bad data")
        clientConnection.close()


thread = threading.Thread(target=recv_instr)
thread.start()

temperature = 0
while True:
    print(f"temperature: {temperature}")
    time.sleep(1)


