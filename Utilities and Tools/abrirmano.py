import RPi.GPIO as GPIO
import time

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

# Set up PWM frequency
pwm_frequency = 50
pwm1 = GPIO.PWM(11, pwm_frequency)
pwm2 = GPIO.PWM(12, pwm_frequency)
pwm3 = GPIO.PWM(13, pwm_frequency)
pwm4 = GPIO.PWM(15, pwm_frequency)
pwm5 = GPIO.PWM(16, pwm_frequency)

# Set initial duty cycle
duty_cycle = 7.5
pwm1.start(duty_cycle)
pwm2.start(duty_cycle)
pwm3.start(duty_cycle)
pwm4.start(duty_cycle)
pwm5.start(duty_cycle)

# Open hand
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(10)
pwm3.ChangeDutyCycle(10)
pwm4.ChangeDutyCycle(10)
pwm5.ChangeDutyCycle(10)
time.sleep(1)

# Close hand
pwm1.ChangeDutyCycle(5)
pwm2.ChangeDutyCycle(5)
pwm3.ChangeDutyCycle(5)
pwm4.ChangeDutyCycle(5)
pwm5.ChangeDutyCycle(5)
time.sleep(1)

# Clean up GPIO pins
pwm1.stop()
pwm2.stop()
pwm3.stop()
pwm4.stop()
pwm5.stop()
GPIO.cleanup()