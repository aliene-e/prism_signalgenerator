# main.py  — minimal Si5351 bring-up demo.
  # Put this next to the vendored si5351.py (both flashed to the Pico root).
  # Wiring: SDA=GP4 (phys pin 6), SCL=GP5 (phys pin 7).

from machine import Pin, I2C
from SI5351 import SI5351

  # --- board / chip constants ---
SDA_PIN, SCL_PIN = 4, 5          # GP4 / GP5  (NOT physical pins 4/5)
I2C_ID           = 0             # I2C0 owns GP4/GP5
I2C_FREQ         = 400_000
SI5351_ADDR      = 0x60
XTAL_HZ          = 25_000_000

# PLLA: VCO = PLL_MULT * XTAL = 32 * 25 MHz = 800 MHz
PLL_MULT, PLL_NUM, PLL_DENOM = 32, 0, 1

# CLK0 target. 800 MHz / (14 + 102/107) = 53.5 MHz
OUT_DIV, OUT_NUM, OUT_DENOM = 14, 102, 107

def main():
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
    
    # 1. Prove the I2C link BEFORE touching any register.
    found = i2c.scan()
    print("I2C scan:", [hex(a) for a in found])
    if SI5351_ADDR not in found:
        print("Si5351 NOT found at", hex(SI5351_ADDR),
            "-> check power, GND, and that SDA/SCL are on GP4/GP5.")
        return

    # 2. Construct + initialize the chip (powers down all outputs, sets xtal load).
    si = SI5351(i2c, address=SI5351_ADDR, crystalFreq=XTAL_HZ)
    si.begin()

    # 3. PLLA to 800 MHz, then CLK0 divider to hit 53.5 MHz.
    si.setupPLL(PLL_MULT, PLL_NUM, PLL_DENOM)
    si.setupMultisynth(0, OUT_DIV, OUT_NUM, OUT_DENOM, pllsource="A")

    # 4. Latch the new dividers and turn the outputs on.
    si.PLLsoftreset()
    si.enableOutputs(True)

    print("CLK0 should now be 53.5 MHz. Scope GP-side CLK0 to confirm.")


if __name__ == "__main__":
    main()