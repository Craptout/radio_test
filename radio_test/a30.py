"""Extremely simple radio range calculator
This version is only for FS/OAS A-30 radio testing
"""

import sys
import math


class RadioTest:
    def __init__(self):
        self.accuracy = 2  # Test set rf level accuracy in dBm. Set by admin.

    def loss(self):
        try:
            # Get input for separation in feet and convert to meters for calculation.
            self.separation = (
                float(
                    input("Enter distance between test set and radio antennas (ft): ")
                )
                * 0.3048
            )
        except ValueError:
            print("You must enter a number. Please try again.")
            sys.exit(1)
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
        # Display rf levels when separation is entered
        print(
            f"Test set RF Level must be at least {self.rf_24:.2f} dBm for 24 nmi range"
        )
        print(
            f"Test set RF Level must be at least {self.rf_50:.2f} dBm for 50 nmi range"
        )

    def range(self):
        try:
            self.rf_level = float(
                input("Enter test set RF Level that opens receiver in dB: ")
            )
        except ValueError:
            print("You must enter a number. Please try again.")
            sys.exit(1)
        self.effective_rx_power = self.rf_level - self.effective_loss
        self.radio_range = (
            (math.pow(10, ((221.28 - self.effective_rx_power) / 20))) / 5148099000
        ) * 0.00053996  # converts meters to nautical miles
        print(f"The radio's max effective range is {self.radio_range:.1f} nmi")


com1 = RadioTest()
com1.loss()
com1.limits()
com1.range()
