# main.py  — minimal Si5351 bring-up demo.
  # Put this next to the vendored si5351.py (both flashed to the Pico root).
  # Wiring: SDA=GP4 (phys pin 6), SCL=GP5 (phys pin 7).

from machine import Pin, I2C, PWM, Timer
from SI5351 import SI5351
from si5351_solver import solve



  # --- board / chip constants ---
SDA_PIN, SCL_PIN = 4, 5          # GP4 / GP5  (NOT physical pins 4/5)
I2C_ID           = 0             # I2C0 owns GP4/GP5
I2C_FREQ         = 400_000
SI5351_ADDR      = 0x60
XTAL_HZ          = 25_000_000

# PLLA: VCO = PLL_MULT * XTAL = 32 * 25 MHz = 800 MHz

# CLK0 target. 800 MHz / (14 + 102/107) = 53.5 MHz

def scan():
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)

    # 1. Prove the I2C link BEFORE touching any register.
    found = i2c.scan()
    print("I2C scan:", [hex(a) for a in found])
    if SI5351_ADDR not in found:
        print("Si5351 NOT found at", hex(SI5351_ADDR),
            "-> check power, GND, and that SDA/SCL are on GP4/GP5.")
        return None 
    return i2c

def configure_si(i2c):
    # 2. Construct + initialize the chip (powers down all outputs, sets xtal load).
    si = SI5351(i2c, address=SI5351_ADDR, crystalFreq=XTAL_HZ)
    si.begin()
    return si

def apply_solution(si, a, b, c, d, rdiv):    
    # 3. PLLA to 800 MHz, then CLK0 divider to hit 53.5 MHz.
    si.setupPLL(a, b, c)
    si.setupMultisynth(0, d*rdiv, 0, 1, pllsource="A")

    # 4. Latch the new dividers and turn the outputs on.
    si.PLLsoftreset()
    si.enableOutputs(True)

def bitbang(target_freq):
    out = Pin(1,Pin.OUT)
    tim = Timer(-1)
    timer_freq = 2*target_freq
    tim.init(freq=timer_freq, mode=Timer.PERIODIC, callback=lambda t: out.toggle())


def pwm(target_freq):
    pwm = PWM(Pin(1))
    pwm.freq(target_freq)        # frequency in Hz
    pwm.duty_u16(32768)   # 16-bit duty: 0-65535 (32768 = 50% square wave)

def main():

    i2c = scan()
    if not i2c: #
        print("Failed to initialize I2C.")
        return
            
    while True:
        # try:
        user_input = (input("Enter target frequency in Hz (e.g. 53.5), or 'q' to quit: "))
        
        if user_input == 'q':
            print ("Exiting program.")
            break

        target_freq = float(user_input)

        # Check if the target frequency is within the valid range (0.5 MHz to 133 MHz)
        if (target_freq < 0 or target_freq > 133_000_000):
            print("Out of range.")
            continue
        elif target_freq < 8:
            bitbang(target_freq)
        elif target_freq < 10_000_000:
            pwm(int(target_freq))
        else:
            try:
                a, b, c, d, rdiv, divby4 = solve(target_freq) # Solves for the PLL and MultiSynth parameters to achieve the target frequency.
                print("PLL: %d + %d/%d  (VCO %.6f MHz) with rdiv %d and divby4 %s" % (a, b, c, XTAL_HZ * (a + b / c) / 1e6, rdiv, "True" if divby4 else "False"))
                si = configure_si(i2c)
                apply_solution(si, a, b, c, d, rdiv)
            except ValueError as e:
                print("Error:", e)
                continue
        
        print("CLK0 should now be " + str(target_freq) + " Hz.")

if __name__ == "__main__":
    main()