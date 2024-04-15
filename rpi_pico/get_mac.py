# Get MAC address from RPi Pico W
# Cite https://forums.raspberrypi.com/viewtopic.php?t=346400
import network
import ubinascii

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)
