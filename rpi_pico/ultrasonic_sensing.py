from machine import Pin
import utime

# Define constants
threshold = 100  # TODO: Modify depending on doorway distance

# Define global variables 
num_occupants = 0
prev_distance_in = 0
prev_distance_out = 0
rising_edge_in = False
rising_edge_out = False

# Define GPIO pins
trigger_in = Pin(28, Pin.OUT)  # Marked with clip
echo_in = Pin(27, Pin.IN)

trigger_out = Pin(26, Pin.OUT)
echo_out = Pin(22, Pin.IN)


def ultra(trigger, echo):
    # Emit an ultrasound
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    
    # Wait for ultrasound echo
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
    
    # Compute time passed and distance
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    
    return distance
    

while True:
    distance_in = ultra(trigger_in, echo_in)
    distance_out = ultra(trigger_out, echo_out)
    
    if (prev_distance_in - distance_in) > threshold:
        if rising_edge_out:
            print("Occupant entered room")
            num_occupants += 1
            rising_edge_out = False
        else:
            rising_edge_in = True
    if (prev_distance_out - distance_out) > threshold:
        if rising_edge_in:
            print("Occupant exited room")
            num_occupants = max(num_occupants - 1, 0)
            rising_edge_in = False
        else:
            rising_edge_out = True
    utime.sleep_ms(100)
    
    prev_distance_in = distance_in
    prev_distance_out = distance_out
    
    print(f"Num occupants: {num_occupants}")
    # print(f"distance_in: {distance_in}, distance_out: {distance_out}")
    # print(f"rising_edge_in: {rising_edge_in}, rising_edge_out: {rising_edge_out}")


