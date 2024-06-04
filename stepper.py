import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

ControlPin = [7,11,13,15]

for pin in ControlPin:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)

seq = [[1,0,0,0],
       [1,1,0,0],
       [0,1,0,0],
       [0,1,1,0],
       [0,0,1,0],
       [0,0,1,1],
       [0,0,0,1],
       [1,0,0,1]]

npasos = 0

def step_motor(steps, direction):
    if direction == 'forward':
        sequence = seq
    elif direction == 'backward':
        sequence = seq[::-1]
    else:
        raise ValueError("Direction must be 'forward' or 'backward'")

    for i in range(steps):
        for halfstep in range(8):
            for pin in range(4):
                GPIO.output(ControlPin[pin], sequence[halfstep][pin])
            time.sleep(0.001)

try:
    step_motor(100, 'backward')
    time.sleep(1)
    step_motor(100, 'forward')
finally:
    
    GPIO.cleanup()
# para juntarlo con el codigo lo que se puede hacer es un if,
# que si el valor se fuerza es mayor a cierto valor, se debe
# de dar un n pasos y al reves si deja de sentir fuerza

#if fuerza > 10:
#    step_motor(100, 'backward')
#    pasos += 1
#if fuerza < 8
#    step_motor(100, 'forward')
#    pasos -= 1