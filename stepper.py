import RPi.GPIO as GPIO
import time

class Stepper:
    def __init__(self, IN1, IN2, IN3, IN4, radianesPorPaso, radio):
        GPIO.setmode(GPIO.BOARD)
        self.ControlPin = [IN1,IN2,IN3,IN4]
        
        self.radianesPorPaso = radianesPorPaso
        self.radio = radio
        self.desplazamientoLineal = 0

        for pin in self.ControlPin:
            GPIO.setup(pin,GPIO.OUT)
            GPIO.output(pin,0)

        self.seq = [[1,0,0,0],
               [1,1,0,0],
               [0,1,0,0],
               [0,1,1,0],
               [0,0,1,0],
               [0,0,1,1],
               [0,0,0,1],
               [1,0,0,1]]

        self.npasos = 0

    def calcularDesplazamientoLineal(self, pasos):
        return self.radianesPorPaso*pasos*self.radio

    def mover(self, steps):
        if steps >= 0:
            sequence = self.seq
            self.desplazamientoLineal -= self.celcularDesplazamientoLineal(steps)
            
        else:
            sequence = self.seq[::-1]
            self.desplazamientoLineal += self.celcularDesplazamientoLineal(steps)
    
        for i in range(steps):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(self.ControlPin[pin], sequence[halfstep][pin])
                time.sleep(0.001)
        
