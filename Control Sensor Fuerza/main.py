import medirFuerza
import time

# Constantes de control que puedo modificar
kp = 1
ki = 1
kd = 1
referencia = 75     # gramos
muestras = 100      # cantidad de muestras del sensor de fuerza

# Inicio sensor de fuerza
stepper = medirFuerza.controlStepper(kp, ki, kd, referencia, muestras)

# Variables para control del tiempo
tiempoMuestreo = 1000000    # 1 000 000 nano segundos (1 ms = 1 kHz)
tiempoPrevio = 0            # Variable para ir actualizando el tiempo del ciclo

# Ciclo de control a 1 kHz
while True:
    if time.process_time_ns() - tiempoPrevio >= tiempoMuestreo:
        
        pasos = stepper.PIDStepper()
        
        print(pasos)
        
        tiempoPrevio = time.process_time_ns()