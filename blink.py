from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

while True:
    # Get user input for blinking frequency
    try: 
        freq = input("Input blinking frequency in Hz (or '0' to quit): ")
    except KeyboardInterrupt:
        print("\nStopped blinking. Enter a new frequency.")
        continue

    # Validate user input
    try:
        value = float(freq)
    except ValueError:
        print("Invalid input. Please enter a number.")
        continue

    if value == 0:
        break

    if value <= 0:
        print("Frequency must be greater than 0. Please try again.")
        continue

    # Calculate period of sleeping based on frequency
    period = 1 / value
    print("Blinking at", value, "Hz. Press Ctrl+C/Stop to change frequency.")

    # inner loop: blink at this frequency until user interrupts
    while True:
        try:
            pin.toggle()
            sleep(period)
        except KeyboardInterrupt:
            print("\nStopped blinking. Enter a new frequency.")
            pin.off()
            break

pin.off()
print("Finished.")

