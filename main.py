import RPi.GPIO as GPIO
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#from some_stepper_motor_library import StepperMotor
from hx711 import HX711
from stepper import Stepper
from simple_pid import PID

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
global stop_threads
stop_threads = False

# Constantes de control que puedo modificar
kp = 1
ki = 0.1
kd = 0.1
referencia = 10     # gramos
muestras = 5        # cantidad de muestras del sensor de fuerza
limControl = 40     # Límite de pasos que puede dar el control

# Setup sensor
hx = HX711(dataPin, clockPin)
hx.set_reading_format("MSB", "MSB")

# Unidad de referencia que se debe calibrar (actualmente está con incertidumbre de +2 g)
referenceUnit = 114
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

# Setup stepper
stepper = Stepper(IN1Pin, IN2Pin, IN3Pin, IN4Pin, radianesPorPaso, radioPinon)

# Sensor data acquisition thread
def sensor_data_acquisition():
    global current_force, force_measurements, stop_threads
    while not stop_threads:
        current_force = hx.get_weight(muestras)
        #print(current_force)
        #time.sleep(0.01)  # Adjust the sampling rate as needed

# PID control and motor movement thread
def pid_control_motor():
    global current_force, stop_threads, control, posicionMotor
    pid = PID(kp, ki, kd, setpoint=referencia)
    while not stop_threads:
        control = pid(current_force)
        if control >= limControl:
            control = limControl
        elif control <= -limControl:
            control = -limControl
        stepper.mover(int(control))
        posicionMotor = stepper.desplazamientoLineal
        time.sleep(1)  # Control loop rate

# Real-time plotting thread
def real_time_plotting():
    plt.ion()
    fig, ax = plt.subplots()
    x_data, y_data = [], []
    ln, = plt.plot([], [], 'r-')

    start_time = time.time()  # Record the start time

    def init():
        ax.set_xlim(0, 100)
        ax.set_ylim(-10, 10)
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Desplazamiento lineal (cm)')
        ax.set_title('PID')
        return ln,

    def update(frame):
        current_time = time.time() - start_time  # Calculate elapsed time
        x_data.append(control)
        y_data.append(stepper.desplazamientoLineal)
        ln.set_data(x_data, y_data)
        return ln,

    ani = animation.FuncAnimation(fig, update, frames=range(100), init_func=init, blit=True)
    plt.show(block=True)

sensor_thread = threading.Thread(target=sensor_data_acquisition)
pid_thread = threading.Thread(target=pid_control_motor)

sensor_thread.start()

#while current_force < referencia:
    #stepper.mover(-10)

stepper.desplazamientoLineal = 0
pid_thread.start()

try:
    while True:
        #print(posicionMotor)
        real_time_plotting()
        #time.sleep(1)
except KeyboardInterrupt:
    stop_threads = True
    sensor_thread.join()
    pid_thread.join()
    GPIO.cleanup()