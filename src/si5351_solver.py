# si5351_solver.py -- parameter finder only, no hardware code.
# fout = 25 MHz * (a + b/c) / d / rdiv        (works in MicroPython or CPython)

XTAL = 25_000_000

# Determines greatest common divisor of two integers. Used to reduce the PLL fraction to lowest terms.
def _gcd(x, y): 
    while y:
        x, y = y, x % y
    return x


def solve(fout):
    """Return (a, b, c, d, rdiv, divby4) for a target frequency in Hz.

    a + b/c : PLL feedback multiplier (fractional)
    d       : MultiSynth output divider (even integer; 4 with divby4=True)
    rdiv    : final R divider (1, 2, 4 ... 128)
    Range ~2.3 kHz .. 200 MHz. Raises ValueError outside it.
    """
    # 1. R divider: multiplies target frequency by increasing powers of 2 to be over 500 kHz ... raises the MultiSynth output to at least 500 kHz (for our purposes it's always 1)
    rdiv = 1
    while fout * rdiv < 500_000 and rdiv < 128:
        rdiv *= 2
    fms = fout * rdiv

    # 2. largest even integer divider that puts the VCO in 600..900 MHz
    if fms > 150_000_000:
        d, divby4 = 4, True                # DIVBY4 mode required > 150 MHz ... if fout * rdiv > 150 MHz, then VCO will be > 600 MHz... might break at higher frequencies cuz it seems like there isn't totally an upper bound on this particularly
    else:
        d = int(900_000_000 // fms)        # Floor of 900 MHz / target (times rdiv)
        d -= d % 2                         # Makes d even
        if d > 2046:
            d = 2046                       # Max dividers is 2046
        divby4 = False
        if d < 6:
            d, divby4 = 4, True

    vco = fms * d                          # VCO (Voltage Controlled Oscillator) frequency = fout * rdiv * d = fms * d)
    if not (600_000_000 <= vco <= 900_000_000):
        raise ValueError("Out of range (~2.3 kHz to 200 MHz)")

    # 3. PLL multiplier a + b/c = vco / 25 MHz; exact fraction if it fits,
    #    else the chip's best 20-bit approximation
    if vco == int(vco): # If VCO is an integer
        a, r = divmod(int(vco), XTAL) # Divide VCO by XTAL to get integer part a and remainder r
        g = _gcd(r, XTAL) # GCD of remainder and XTAL to reduce fraction
        b, c = r // g, XTAL // g # Floor divide remainder and XTAL by GCD to get reduced fraction b/c
        if c > 1_048_575: # Upper limit for c denominator is 1,048,575 (20 bits)
            a, c = int(vco / XTAL), 1_048_575
            b = round((vco / XTAL - a) * c)
    else:
        m = vco / XTAL
        a, c = int(m), 1_048_575
        b = round((m - a) * c)
    if b == c:
        a, b, c = a + 1, 0, 1
    return a, b, c, d, rdiv, divby4


if __name__ == "__main__":
    while True:
        a, b, c, d, rdiv, divby4 = solve(float(input("Hz> ")))
        print("PLL: %d + %d/%d  (VCO %.6f MHz)" % (a, b, c, XTAL * (a + b / c) / 1e6))
        print("MS : /%d%s   R: /%d" % (d, " DIVBY4" if divby4 else "", rdiv))
        print("out: %.6f Hz" % (XTAL * (a + b / c) / d / rdiv))