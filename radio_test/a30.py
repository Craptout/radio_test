"""Extremely simple radio range calculator
This version is only for FS/OAS A-30 radio testing
"""

import sys
import math


class SimpleA30:
    def __init__(self):
        self.accuracy = 2  # Test set rf level accuracy in dBm. Set by admin.

    def loss(self, separation):  # enter separation in feet
        self.separation = separation * 0.3048  # converts to meters for calculation
        if self.separation < 6.096:
            print("Separation must be 20 ft or greater")  # ensures far field
            sys.exit(1)
        self.effective_loss = (
            ((20) * math.log10(self.separation))
            + 9.940587561127312
            + self.accuracy
            + 1  # 1 dBm uncertainty added to account for minor differences such as antenna placement
        )

    def limits(self):
        # Minimum RF Level from test set needed to simulate 24 nmi range
        self.rf_24 = -65.9 + self.effective_loss
        # Minimum RF Level from test set needed to simulate 50 nmi range
        self.rf_50 = -72.27838121 + self.effective_loss

    def range(self, rf_level):
        self.rf_level = rf_level
        self.effective_rx_power = self.rf_level - self.effective_loss
        self.radio_range = (
            (math.pow(10, ((221.28 - self.effective_rx_power) / 20))) / 5148099000
        ) * 0.00053996  # converts meters to nautical miles


com1 = SimpleA30()
com1.loss(20)
com1.limits()
print(f"Test set RF Level must be at least {com1.rf_24:.2f} dBm for 24 nmi range")
print(f"Test set RF Level must be at least {com1.rf_50:.2f} dBm for 50 nmi range")
com1.range(float(input("Enter test set RF Level that opens receiver in dB: ")))
print(f"The radio's max effective range is {com1.radio_range:.1f} nmi")
