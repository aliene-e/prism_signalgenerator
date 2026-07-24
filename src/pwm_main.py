from machine import Pin, PWM, Timer

def main():
  
    while True:
        # try:
        user_input = (input("Enter target frequency in Hz (e.g. 8-10,000,000), or 'q' to quit: "))
        
        if user_input == 'q':
            print ("Exiting program.")
            break

        target_freq = int(user_input)

        if target_freq > 0 and target_freq < 8:
            out = Pin(1, Pin.OUT)
            tim = Timer(-1)
            # Toggle at 2 Hz -> one full high/low cycle per second = 1 Hz square wave
            target_freq *= 2
            tim.init(freq=target_freq, mode=Timer.PERIODIC, callback=lambda t: out.toggle())
        elif target_freq >= 8 and target_freq < 10_000_000:
            
            pwm = PWM(Pin(1))
            pwm.freq(target_freq)        # frequency in Hz
            pwm.duty_u16(32768)   # 16-bit duty: 0-65535 (32768 = 50% square wave)
        else:
            print("Out of range.")
            continue
                    
        print("CLK0 should now be " + str(target_freq) + " Hz.")

if __name__ == "__main__":
    main()


"""PWM out on GPIO 1 — Raspberry Pi Pico (MicroPython).

GP1 -> BNC center pin, GND -> BNC shield.
Output is a 3.3 V logic-level square wave (hardware PWM, runs on its own).
Save as main.py on the Pico to run at boot.
"""



# That's it — PWM is generated in hardware, so no loop is needed.
# The signal keeps running as long as the Pico is powered.

# To stop the output later:
#   pwm.deinit()



"""1 Hz square wave on GPIO 1 — Raspberry Pi Pico (MicroPython).

GP1 -> BNC center pin, GND -> BNC shield.
3.3 V logic-level output, 50% duty.

Note: the Pico's hardware PWM can't go below ~8 Hz (125 MHz clock,
max divider 256, 16-bit counter -> min ~7.5 Hz), so pwm.freq(1) would
raise ValueError. For 1 Hz we toggle the pin from a hardware timer
instead — still fully autonomous, no busy loop.

Save as main.py on the Pico to run at boot.
"""


# To stop the output later:
#   tim.deinit(); out.value(0)