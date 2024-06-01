import RPi.GPIO as GPIO
import threading
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#from some_stepper_motor_library import StepperMotor
from hx711 import HX711
from simple_pid import PID

# Global variables
force_measurements = []
current_force = 0
motor_position = 0
stop_threads = False

# Constantes de control que puedo modificar
kp = 1
ki = 0.1
kd = 0.05
referencia = 75     # gramos
muestras = 10       # cantidad de muestras del sensor de fuerza

# Setup sensor
hx = HX711(17,27)
hx.set_reading_format("MSB", "MSB")

# Unidad de referencia que se debe calibrar (actualmente está con incertidumbre de +2 g)
referenceUnit = 17000
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tarado listo! Puede comenzar a medir...")

# Sensor data acquisition thread
def sensor_data_acquisition():
    global current_force, force_measurements, stop_threads
    while not stop_threads:
        current_force = hx.get_weight(muestras)
        time.sleep(0.01)  # Adjust the sampling rate as needed

# PID control and motor movement thread
def pid_control_motor():
    global current_force, motor_position, stop_threads
    #motor = StepperMotor()
    pid = PID(kp, ki, kd, setpoint=referencia)
    while not stop_threads:
        control = pid(current_force)
        print(control)
        #motor.move(control)
        motor_position += control
        #print(motor_position)
        time.sleep(0.01)  # Control loop rate

# Real-time plotting thread
def real_time_plotting():
    global motor_position
    plt.ion()
    fig, ax = plt.subplots()
    x_data, y_data = [], []
    ln, = plt.plot([], [], 'r-')

    start_time = time.time()  # Record the start time

    def init():
        ax.set_xlim(0, 100)
        #ax.set_ylim(0, 100)
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Señal de control')
        ax.set_title('PID')
        return ln,

    def update(frame):
        current_time = time.time() - start_time  # Calculate elapsed time
        x_data.append(current_time)
        y_data.append(motor_position)
        ln.set_data(x_data, y_data)
        return ln,

    ani = animation.FuncAnimation(fig, update, frames=range(100), init_func=init, blit=True)
    plt.show(block=True)

# Main function to start threads
def main():
    global stop_threads
    sensor_thread = threading.Thread(target=sensor_data_acquisition)
    pid_thread = threading.Thread(target=pid_control_motor)

    sensor_thread.start()
    pid_thread.start()

    try:
        while True:
            #real_time_plotting()
            time.sleep(1)
    except KeyboardInterrupt:
        stop_threads = True
        sensor_thread.join()
        pid_thread.join()

if __name__ == "__main__":
    main()