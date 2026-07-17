"""
Pi Pico code to configure Si5351 clock generator for 75MHz output on CLK0

Si5351 Hardware Connections:
- Pin 5 (GP3/SCL) <-> SCL
- Pin 4 (GP2/SDA) <-> SDA
- Pin 36 (3V3 OUT) <-> VCC
- Pin 38 (GND) <-> GND

I2C Address: 0x60 (XA and XB grounded or unconnected)

For 75MHz on CLK0:
- PLLA = 800MHz (using 25MHz crystal)
- CLK0 divider = 10.666... (fractional, 32/3)
"""

from machine import Pin, I2C
import time

# I2C configuration for Pi Pico
# Using I2C0 with SCL on GP5 (Pin 7) and SDA on GP4 (Pin 6)
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)

# Si5351 I2C address (default with XA=0, XB=0)
SI5351_ADDRESS = 0x60

def si5351_write(reg, value):
    """Write a byte to Si5351 register"""
    try:
        i2c.writeto_mem(SI5351_ADDRESS, reg, bytes([value]))
        return True
    except:
        return False

def si5351_read(reg):
    """Read a byte from Si5351 register"""
    try:
        return i2c.readfrom_mem(SI5351_ADDRESS, reg, 1)[0]
    except:
        return None

def si5351_init():
    """Initialize Si5351"""
    # Reset the device
    si5351_write(177, 0x80)
    time.sleep_ms(10)
    
    # Disable all clock outputs
    si5351_write(3, 0xFF)
    
    # Configure PLLA for 800MHz (with 25MHz crystal)
    # P1 = 3584 (128*32 - 512), P2 = 0, P3 = 128
    si5351_write(25, 0x80)   # PLLA source = XTAL, P3 = 128
    si5351_write(26, 0x0E)   # P1[15:8] = 0x0E
    si5351_write(27, 0x00)   # P1[7:0] = 0x00
    si5351_write(28, 0x00)   # P3[15:8]
    si5351_write(29, 0x01)   # P3[7:0]
    si5351_write(30, 0x00)   # P2[15:8]
    si5351_write(31, 0x00)   # P2[7:0]

def configure_clk0_75mhz():
    """Configure CLK0 to output 75MHz using PLLA at 800MHz"""
    # Divider = 800MHz / 75MHz = 10.666... = 32/3
    # P1 = 128*a + b - 512 = 128*10 + 85 - 512 = 853
    # P2 = 85, P3 = 128
    
    si5351_write(16, 0x03)   # P1[15:8] = 853 >> 8 = 0x03
    si5351_write(17, 0x55)   # P1[7:0] = 853 & 0xFF = 0x55
    si5351_write(18, 0x00)   # P3[15:8] = 0x00
    si5351_write(19, 0x80)   # P3[7:0] = 0x80
    si5351_write(20, 0x00)   # P2[15:8] = 0x00
    si5351_write(21, 0x55)   # P2[7:0] = 0x55
    
    # Enable CLK0 with PLLA
    si5351_write(165, 0x00)
    
    # Enable CLK0 output
    current = si5351_read(3)
    if current is not None:
        si5351_write(3, current & 0xFE)

# Main execution
if __name__ == "__main__":
    si5351_init()
    configure_clk0_75mhz()
    print("Si5351 configured for 75MHz output on CLK0.")
