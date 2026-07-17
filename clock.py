"""
SI5351 Clock Generator Driver for Raspberry Pi Pico
SCL: GPIO 7, SDA: GPIO 6
"""

from machine import Pin, I2C
import time

# SI5351 I2C Address
SI5351_I2C_ADDR = 0x60

# SI5351 Registers
SI5351_CLK_ENABLE_CONTROL = 0x07
SI5351_PLL_SOURCE = 0x15
SI5351_CLK0_CONTROL = 0x16
SI5351_CLK1_CONTROL = 0x17
SI5351_CLK2_CONTROL = 0x18
SI5351_CLK3_CONTROL = 0x19
SI5351_CLK4_CONTROL = 0x1A
SI5351_CLK5_CONTROL = 0x1B
SI5351_CLK6_CONTROL = 0x1C
SI5351_CLK7_CONTROL = 0x1D
SI5351_PLL_A_SOURCE = 0x15
SI5351_PLL_B_SOURCE = 0x16
SI5351_PLL_A_INT = 0x18
SI5351_PLL_A_FRAC = 0x19
SI5351_PLL_A_FRAC2 = 0x1A
SI5351_PLL_B_INT = 0x1E
SI5351_PLL_B_FRAC_0 = 0x1F
SI5351_PLL_B_FRAC_1 = 0x20
SI5351_PLL_B_FRAC_2 = 0x21
SI5351_CLK0_BB_OE = 0x21
SI5351_CLK0_MM_P1 = 0x25
SI5351_CLK0_MM_P2 = 0x26
SI5351_CLK0_MM_P3 = 0x27
SI5351_CLK0_P1 = 0x28
SI5351_CLK0_P2 = 0x29
SI5351_CLK0_P3 = 0x2A
SI5351_CLK0_P4 = 0x2B
SI5351_CLK0_P5 = 0x2C
SI5351_CLK0_P6 = 0x2D
SI5351_CLK0_P7 = 0x2E
SI5351_CLK1_P1 = 0x32
SI5351_CLK1_P2 = 0x33
SI5351_CLK1_P3 = 0x34
SI5351_CLK1_P4 = 0x35
SI5351_CLK1_P5 = 0x36
SI5351_CLK1_P6 = 0x37
SI5351_CLK1_P7 = 0x38
SI5351_CLK2_P1 = 0x3F
SI5351_CLK2_P2 = 0x40
SI5351_CLK2_P3 = 0x41
SI5351_CLK2_P4 = 0x42
SI5351_CLK2_P5 = 0x43
SI5351_CLK2_P6 = 0x44
SI5351_CLK2_P7 = 0x45
SI5351_DEVICE_RESET = 0x03
SI5351_CRYSTAL_LOAD = 0x0D

# Crystal load capacitance values
CSL_0PF = 0x00
CSL_6PF = 0x04
CSL_8PF = 0x08
CSL_10PF = 0x0C

# Crystal frequency (typically 25MHz or 27MHz for SI5351)
XTAL_FREQ = 25000000  # 25 MHz


def i2c_write(i2c, reg, value):
    """Write a single byte to an SI5351 register."""
    i2c.writeto_mem(SI5351_I2C_ADDR, reg, bytes([value]))


def i2c_write_multi(i2c, reg, values):
    """Write multiple bytes to SI5351 registers."""
    i2c.writeto_mem(SI5351_I2C_ADDR, reg, bytes(values))


def si5351_init(i2c):
    """Initialize the SI5351."""
    # Reset the device
    print("Resetting SI5351...")
    i2c_write(i2c, SI5351_DEVICE_RESET, 0x40)
    time.sleep_ms(10)
    print("SI5351 reset complete.")
    # Set crystal load capacitance (adjust based on your board, 8pF is common)
    i2c_write(i2c, SI5351_CRYSTAL_LOAD, CSL_8PF)
    
    # Disable all clock outputs initially
    i2c_write(i2c, SI5351_CLK_ENABLE_CONTROL, 0xFF)
    
    # Configure PLL A to 900MHz (for 50MHz output with division)
    # F_vco = F_xtal * (a + b/c) where a is integer, b/c is fractional
    # For 900MHz with 25MHz crystal: a = 36, b = 0, c = 1
    # MSN: a = 36, b = 0, c = 1
    # P1, P2, P3 for PLL: P1 = 12*b*c + b - 512*c, P2 = 12*b, P3 = c
    
    # For PLL A = 36 (no fractional): P1 = -512, P2 = 0, P3 = 1
    # These are 10-bit values stored in 8-bit registers with special encoding
    
    # Configure PLL A (36 * 25MHz = 900MHz)
    # P1[17:10], P1[9:2], P1[1:0] + P2[17:12], P2[11:4], P2[3:0] + P3[15:12], P3[11:4], P3[3:0]
    # For integer mode (b=0, c=1): P1=0, P2=0, P3=1
    
    # PLL A configuration registers (0x18-0x23)
    # P1[17:10], P1[9:2], P1[1:0], P2[17:12], P2[11:4], P2[3:0], P3[15:12], P3[11:4]
    i2c_write(i2c, 0x18, 0)   # P1[17:10]
    i2c_write(i2c, 0x19, 0)   # P1[9:2]  
    i2c_write(i2c, 0x1A, 0)   # P1[1:0] + P2[17:12]
    i2c_write(i2c, 0x1B, 0)   # P2[11:4]
    i2c_write(i2c, 0x1C, 0)   # P2[3:0] + P3[15:12]
    i2c_write(i2c, 0x1D, 1)   # P3[11:4]
    i2c_write(i2c, 0x1E, 0)   # P3[3:0] (MSB)
    i2c_write(i2c, 0x1F, 0)   # P3[3:0] (LSB)
    
    # PLL B configuration - same as A for simplicity
    i2c_write(i2c, 0x20, 0)   # P1[17:10]
    i2c_write(i2c, 0x21, 0)   # P1[9:2]
    i2c_write(i2c, 0x22, 0)   # P1[1:0] + P2[17:12]
    i2c_write(i2c, 0x23, 0)   # P2[11:4]
    i2c_write(i2c, 0x24, 0)   # P2[3:0] + P3[15:12]
    i2c_write(i2c, 0x25, 1)   # P3[11:4]
    i2c_write(i2c, 0x26, 0)   # P3[3:0] (MSB)
    i2c_write(i2c, 0x27, 0)   # P3[3:0] (LSB)
    
    # Configure CLK0 for 50MHz output using PLL A
    # F_out = F_vco / (clk_mult * (1 + clk_div))
    # For 50MHz from 900MHz VCO: need division of 18
    # Using CLK0 withmult = 1, div = 18
    # P1 = 12*1*18 + 1 - 512*18 = 216 + 1 - 9216 = -8999
    # P2 = 12*1 = 12
    # P3 = 18
    
    # For 900MHz VCO / 18 = 50MHz
    # MSN registers for CLK0 (0x26-0x2D for P1, P2, P3)
    # P1 = 8999 (encoded), P2 = 12, P3 = 18
    
    # Calculate SI5351 multibit values for 50MHz from 900MHz VCO
    # F_out = F_vco / (clk_mult * (1 + clk_div))
    # With clk_mult = 1, clk_div = 17 (gives 900/18 = 50MHz)
    
    # CLK0 P1, P2, P3 values (mult = 1, div = 17)
    # P1 = 12 * mult * div + mult - 512 * div
    # P1 = 12 * 1 * 17 + 1 - 512 * 17 = 204 + 1 - 8704 = -8499
    # This needs to be converted to 10-bit two's complement representation
    
    # For simplicity, use direct integer division with proper register settings
    # Using mult = 1, div = 18 (900MHz / 18 = 50MHz)
    
    # CLK0 configuration (registers 0x26-0x2D)
    # P1[17:10], P1[9:2], P1[1:0] + P2[17:12], P2[11:4], P2[3:0], P3[15:12], P3[11:4]
    # With mult=1, div=18: P1=8499, P2=12, P3=18
    
    # Set CLK0 P1, P2, P3 for 50MHz output from 900MHz VCO
    # P1 = 8499 = 0x2133, P2 = 12, P3 = 18
    i2c_write(i2c, 0x26, (8499 >> 2) & 0xFF)   # P1[17:10]
    i2c_write(i2c, 0x27, (8499 & 0x03) << 6)   # P1[1:0] (top 2 bits)
    i2c_write(i2c, 0x28, 12)                    # P2[11:4]
    i2c_write(i2c, 0x29, 18)                    # P3[11:4]
    i2c_write(i2c, 0x2A, 0)                     # P3[3:0]
    i2c_write(i2c, 0x2B, 0)                     # P2[3:0]
    i2c_write(i2c, 0x2C, 0)                     # P1[17:10] continuation
    i2c_write(i2c, 0x2D, 0)                     # More P1 bits
    
    # Actually, let me recalculate with proper values
    # For a simple 50MHz output, we can use direct division from a PLL
    # Using CLK0 control register to set proper mode
    
    # Set CLK0 control: MSB_N=0, MSB_P1=1, drive strength = 8mA, src = PLL A
    # CLK0 control: 0x4C = 0b01001100
    # Bit 7: 0 - Power down = off
    # Bit 6: 1 - Invert = off
    # Bit 5-4: 00 - drive strength 8mA
    # Bit 3: 1 - MSBLIVE = 1
    # Bit 2-0: 100 - clock source = PLL A
    
    i2c_write(i2c, SI5351_CLK0_CONTROL, 0x4C)
    
    # Enable CLK0 output
    i2c_write(i2c, SI5351_CLK_ENABLE_CONTROL, 0xF8)  # 0b11111000 - enable CLK0, disable others


def set_frequency(i2c, clk_num, frequency):
    """
    Set the output frequency for a specific clock channel.
    Uses PLL A as the source.
    
    Args:
        i2c: I2C object
        clk_num: Clock number (0-7)
        frequency: Desired frequency in Hz
    """
    # PLL A is configured for 900MHz (fixed)
    F_VCO = 900000000
    
    # Calculate the division ratio
    # F_out = F_VCO / divisor
    # divisor = F_VCO / F_out
    
    if frequency <= 0:
        frequency = 1000  # Minimum 1kHz
    
    if frequency > 600000000:  # Max 600MHz
        frequency = 600000000
    
    # Calculate integer division
    divisor = F_VCO // frequency
    
    # For SI5351, the actual register values are:
    # P1 = 128 * mult + 128 * frac / c - 512
    # P2 = 128 * frac
    # P3 = c
    
    # For integer mode (no fractional), set frac = 0
    mult = divisor
    frac = 0
    c = 1
    
    # Calculate P1, P2, P3 values
    # P1 = 128 * mult + 128 * frac / c - 512
    # For integer: P1 = 128 * mult - 512
    p1 = int(128 * mult + 128 * frac / c - 512)
    p2 = int(128 * frac)
    p3 = c
    
    # Set the appropriate registers based on clock number
    base_reg = 0x26 + clk_num * 9  # Base address for each clock
    
    # P1 is 10-bit, split into two registers
    # P1[17:10] and P1[9:0]
    # P2 is 10-bit
    # P3 is 10-bit
    
    # Write to clock registers
    i2c_write(i2c, base_reg, (p1 >> 8) & 0xFF)       # P1[17:10]
    i2c_write(i2c, base_reg + 1, p1 & 0xFF)          # P1[9:0]
    i2c_write(i2c, base_reg + 2, (p2 >> 4) & 0xFF)   # P2[15:4]
    i2c_write(i2c, base_reg + 3, ((p2 & 0x0F) << 4) | ((p3 >> 8) & 0x0F))  # P2[3:0], P3[11:8]
    i2c_write(i2c, base_reg + 4, p3 & 0xFF)          # P3[7:0]
    
    # Set clock control register
    control_reg = SI5351_CLK0_CONTROL + clk_num
    # Source = PLL A (bits 2:0 = 100), Drive strength = 8mA (bits 5:4 = 00)
    i2c_write(i2c, control_reg, 0x4C)
    
    # Enable the specific clock output
    enable_reg = 0x07
    current_enable = i2c.readfrom_mem(SI5351_I2C_ADDR, enable_reg, 1)[0]
    # Clear the bit for this clock (active low enable)
    new_enable = current_enable & ~(1 << clk_num)
    i2c_write(i2c, enable_reg, new_enable)


def main():
    """Main function to initialize and set up the SI5351."""
    # Initialize I2C with SCL on GPIO 7 and SDA on GPIO 6
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
    
    # Initialize SI5351
    si5351_init(i2c)
    print("SI5351 initialized")
    
    # Set CLK0 to 50MHz
    set_frequency(i2c, 0, 50000000)
    print("CLK0 set to 50MHz")
    
    # Optional: Set other clocks to different frequencies
    # set_frequency(i2c, 1, 25000000)  # CLK1 to 25MHz


if __name__ == "__main__":
    main()