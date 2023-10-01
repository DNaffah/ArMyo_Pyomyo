import RPi.GPIO as GPIO
import time

# Configurar los pines GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(15, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)

# Configurar la frecuencia PWM
pwm_frequency = 50
pwm1 = GPIO.PWM(11, pwm_frequency)
pwm2 = GPIO.PWM(12, pwm_frequency)
pwm3 = GPIO.PWM(13, pwm_frequency)
pwm4 = GPIO.PWM(15, pwm_frequency)
pwm5 = GPIO.PWM(16, pwm_frequency)

# Establecer el ciclo de trabajo inicial
duty_cycle = 7.5
pwm1.start(duty_cycle)
pwm2.start(duty_cycle)
pwm3.start(duty_cycle)
pwm4.start(duty_cycle)
pwm5.start(duty_cycle)

# Mover los servos a las posiciones deseadas para el número 1
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(5)
pwm3.ChangeDutyCycle(5)
pwm4.ChangeDutyCycle(5)
pwm5.ChangeDutyCycle(5)
time.sleep(1)

# Mover los servos a las posiciones deseadas para el número 2
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(10)
pwm3.ChangeDutyCycle(5)
pwm4.ChangeDutyCycle(5)
pwm5.ChangeDutyCycle(5)
time.sleep(1)

# Mover los servos a las posiciones deseadas para el número 3
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(10)
pwm3.ChangeDutyCycle(10)
pwm4.ChangeDutyCycle(5)
pwm5.ChangeDutyCycle(5)
time.sleep(1)

# Mover los servos a las posiciones deseadas para el número 4
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(10)
pwm3.ChangeDutyCycle(10)
pwm4.ChangeDutyCycle(10)
pwm5.ChangeDutyCycle(5)
time.sleep(1)

# Mover los servos a las posiciones deseadas para el número 5
pwm1.ChangeDutyCycle(10)
pwm2.ChangeDutyCycle(10)
pwm3.ChangeDutyCycle(10)
pwm4.ChangeDutyCycle(10)
pwm5.ChangeDutyCycle(10)
time.sleep(1)

# Limpiar los pines GPIO
pwm1.stop()
pwm2.stop()
pwm3.stop()
pwm4.stop()
pwm5.stop()
GPIO.cleanup()