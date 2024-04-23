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

# Function to convert angle to PWM duty cycle
def angle_to_duty_cycle(angle):
    duty_cycle = (angle / 90.0) * (PWM_duty_max - PWM_duty_min) + PWM_duty_min
    return duty_cycle

# Function to move the servo to a specified angle
def move_to_angle(angle):
    duty_cycle = angle_to_duty_cycle(angle)
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)  # Adjust this delay as needed for your servo
    # pwm.ChangeDutyCycle(0)  # Stop sending PWM signal

# Main function
if __name__ == '__main__':
    try:
        # Start PWM with 0 duty cycle (servo at neutral position)
        pwm.start(0)

        while True:
            # Prompt the user to input the desired angle
            target_angle = float(input("Enter the desired angle (0-90): "))
            
            # Move the servo to the specified angle
            move_to_angle(target_angle)

    except KeyboardInterrupt:
        # Cleanup GPIO on interruption
        pwm.stop()
        GPIO.cleanup()
