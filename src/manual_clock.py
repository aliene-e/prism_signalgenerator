from machine import Pin
from utime import sleep

while True:
    pin = Pin(1, Pin.OUT)
    pin.toggle()
    sleep(1/20)
    pin.toggle()
    sleep(1/20)
