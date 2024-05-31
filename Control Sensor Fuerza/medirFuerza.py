import RPi.GPIO as GPIO
from hx711 import HX711

class controlStepper:
    def __init__(self, kp, ki, kd, referencia, muestras):
        # Constantes de control
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.sumaError = 0
        self.errorAnterior = 0

        self.referencia = referencia     # Fuerza en gramos que queremos ejercer al cartón de huevos
        self.muestras = muestras      # Cantidad de muestras que se quieren tomar del sensor de fuerza
     
        # Inicio el sensor, para tararlo, y que pueda comenzar a medir
        self.hx = HX711(17, 27)
        
        self.hx.set_reading_format("MSB", "MSB")
        
        # Unidad de referencia que se debe calibrar (actualmente está con incertidumbre de +2 g)
        self.referenceUnit = 17000
        self.hx.set_reference_unit(self.referenceUnit)
        self.hx.reset()
        self.hx.tare()
        print("Tarado listo! Puede comenzar a medir...")
            
    def PIDStepper(self):
        medicion = self.hx.read_average(self.muestras)
        error = self.referencia - medicion
        self.sumaError += error
        self.diferenciaError = error - self.errorAnterior
        self.errorAnterior = error
    
        pasos = self.kp*error + self.ki*self.sumaError + self.kd*self.diferenciaError
        
        return pasos
    