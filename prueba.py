import RPi.GPIO as GPIO
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#from some_stepper_motor_library import StepperMotor
from hx711 import HX711
from stepper import Stepper
import csv

# PINES
# Stepper
IN1Pin = 6
IN2Pin = 13
IN3Pin = 19
IN4Pin = 26
# Celda de carga
dataPin = 17
clockPin = 27

# Global variables
force_measurements = []
current_force = 0
motor_position = 0
stop_threads = False

# Setup sensor
hx = HX711(dataPin, clockPin)
hx.set_reading_format("MSB", "MSB")

# Unidad de referencia que se debe calibrar (actualmente está con incertidumbre de +2 g)
referenceUnit = 17000
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tarado listo! Puede comenzar a medir...")

# Constantes de desplazamiento del motor
dientesPinon = 25
moduloPinon = 1
radioPinon = (dientesPinon/moduloPinon) / 2
radioPinon /= 10    # Convierto a cm
pasosPorRev = 512
radianesPorPaso = 2*np.pi/pasosPorRev

referencia = 75     # gramos
muestras = 10       # cantidad de muestras del sensor de fuerza

# Setup stepper
stepper = Stepper(IN1Pin, IN2Pin, IN3Pin, IN4Pin, radianesPorPaso, radioPinon)

# Sensor data acquisition thread
def sensor_data_acquisition():
    global current_force, force_measurements, stop_threads
    while not stop_threads:
        current_force = hx.get_weight(muestras)
        time.sleep(0.01)  # Adjust the sampling rate as needed

global stop_threads
sensor_thread = threading.Thread(target=sensor_data_acquisition)

sensor_thread.start()

datos = [['tiempo','referencia','fuerza']]
start_time = time.time()  # Record the start time

try:
    while current_force != referencia:
        stepper.mover(10)
        current_time = time.time() - start_time  # Calculate elapsed time
        datos.append([current_time,referencia,current_force])
        
except KeyboardInterrupt:
    stop_threads = True
    sensor_thread.join()
    GPIO.cleanup()
  
stop_threads = True
sensor_thread.join()
GPIO.cleanup()

with open('prueba.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    for row in datos:
        writer.writerow(row)
    
print("Prueba finalizada!\n\n")

