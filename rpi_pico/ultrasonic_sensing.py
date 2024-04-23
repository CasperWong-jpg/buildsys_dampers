from machine import Pin
import utime

trigger_in = Pin(28, Pin.OUT)
echo_in = Pin(27, Pin.IN)

trigger_out = Pin(26, Pin.OUT)
echo_out = Pin(22, Pin.IN)

def ultra():
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
    
    # Compute time passed
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    print("The distance from object is ", distance, "cm")
    
while True:
    print("Detecting ultra...")
    ultra()
    utime.sleep_ms(100)


