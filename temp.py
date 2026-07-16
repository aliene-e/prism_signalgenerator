import machine
import utime


adc = machine.ADC(4)
conversion_factor = 3.3 / (65535)

while True:
    try:
        reading = adc.read_u16() * conversion_factor
        temp_c = 27 - (reading - 0.706) / 0.001721
        temp_f = (temp_c * 9 / 5) + 32
        print("Temperature: {:.2f} C / {:.2f} F".format(temp_c, temp_f))
        utime.sleep(1)
    except KeyboardInterrupt:
        break
print("Finished.")
