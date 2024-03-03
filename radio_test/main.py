"""Determine radio performance based on the Friis Transmission Equation using decibles for power"
Pr{dB} = Pt{dB} + Gt{dBi} + Gr{dBi} + 20log10((wavelength/(4*pi*d)))
Range (m) = (10^(Pt{dBm} + Gt{dBi} + Gr{dBi} - Pr{dBm} + 180) / 20) / (41.88 * freq{Hz})

variables
---------
Pr = Power recieved
Pt = Power transmitted
Gt = Gain of transmitting antenna = tx_ant_gain
Gr = Gain of receiving antenna = rx_ant_gain
d = separation between transmitting and receiving antennas
Units for wavelength and distance must be the same. 
SI Units are used for calculations and converted for users where needed.
dBi = decibles referenced to an isotropic raditor = dBd + 2.15
dBd = decibles referenced to a dipole antenna = dBi - 2.15 
Aviation antennas are generally 0 dBd.
wavelength = speed_of_light / frequency
"""

import sys
import math
from pint import UnitRegistry
from pint import DimensionalityError


ureg = UnitRegistry(autoconvert_offset_to_baseunit=True) #baseunit required for dBm conversion
# defines dBi and dBd
ureg.load_definitions("my_def.txt")
Q_ = ureg.Quantity
# speed of light
c = Q_("299,792,458 m/s")


class RadioTest:
    def __init__(self, separation, freq, tx_ant_gain, rx_ant_gain, power_transmitted):
        try: 
            self.separation = Q_(separation).to("m")
            self.freq = Q_(freq).to("Hz")            
            self.wavelength = (c / self.freq).to("m") # Converts frequency to wavelength
            self.far_field = 2 * self.wavelength             
            self.tx_ant_gain = Q_(tx_ant_gain).to("dBi")
            self.rx_ant_gain = Q_(rx_ant_gain).to("dBi")
            self.power_transmitted = Q_(power_transmitted).to("dBm")
            self.accuracy = Q_("2 dB") # IFR 4000 RF level accuracy. Provide setting/admin edit.
            self.uncertainty = Q_("1 dB") # Built in error to account for minor differences such as antenna placement
        except DimensionalityError:
            print("You must enter values with units, e.g. 127 MHz or 0 dBd")
            sys.exit(1)

    def field(self):
        if self.separation < self.far_field:
            print(f"The test set is too close. The antennas must be at least {self.far_field.to("ft"):.1f~P} ({self.far_field:.1f~P}) apart.")
            sys.exit(1)
    
    def loss(self):
        self.path_loss = (
            (20 * math.log10(self.separation.magnitude))
            + (20 * math.log10(self.freq.magnitude))
            + (20 * (math.log10((4 * math.pi) / c.magnitude)))
            - self.tx_ant_gain.magnitude                
            - self.rx_ant_gain.magnitude                
        ) * ureg("dB")
        self.effective_loss = (self.path_loss.magnitude 
        + self.accuracy.magnitude 
        + self.uncertainty.magnitude) * ureg("dB")    
          
    def limits(self):
        self.radio_rf_24nmi = (
            self.power_transmitted.magnitude
            + self.tx_ant_gain.magnitude
            + self.rx_ant_gain.magnitude
            + (20 * math.log10((self.wavelength.magnitude / (4 * math.pi * 44448))))
        ) * ureg(
            "dBm"
        )
        self.radio_rf_50nmi = (
            self.power_transmitted.magnitude
            + self.tx_ant_gain.magnitude
            + self.rx_ant_gain.magnitude
            + (20 * math.log10((self.wavelength.magnitude / (4 * math.pi * 92600))))
        ) * ureg(
            "dBm"
        )  
        self.test_set_rf_24nmi = (self.radio_rf_24nmi.magnitude + self.effective_loss.magnitude) * ureg("dBm")
        self.test_set_rf_50nmi = (self.radio_rf_50nmi.magnitude + self.effective_loss.magnitude) * ureg("dBm")
            
    def range(self, test_set_rf):
        try:
            self.test_set_rf = Q_(test_set_rf).to("dBm")
        except DimensionalityError:
            print("You must enter a value with units, e.g. -50 dBm")
            sys.exit(1)
        self.power_received = (self.test_set_rf.magnitude                            
            - self.effective_loss.magnitude            
        ) * ureg("dBm")        
        self.radio_range = ((
            (math.pow(10, (self.power_transmitted.magnitude 
                            + self.tx_ant_gain.magnitude 
                            + self.rx_ant_gain.magnitude 
                            - self.power_received.magnitude                            
                            + 180) 
                            / 20))
                            / (41.88 * self.freq.magnitude)
        ) * ureg("m")).to("nmi")        
        
    def rx_pwr(self, radio_range):
        try:
            self.radio_range = Q_(radio_range).to("m")
        except DimensionalityError:
            print("You must enter a value with units, e.g. 20 miles")
            sys.exit(1)
        self.power_received = (
            self.power_transmitted.magnitude 
            + self.rx_ant_gain.magnitude 
            + self.tx_ant_gain.magnitude 
            + (20 * math.log10((self.wavelength.magnitude/(4 * math.pi * self.radio_range.magnitude))))
        ) * ureg("dBm")    
    
    def tx_pwr(self, radio_range, power_received):
        try:
            self.radio_range = Q_(radio_range).to("m")
            self.power_received = Q_(power_received).to("dBm")
        except DimensionalityError:
            print("You must enter a value with units, e.g. 20 miles or -50 dBm")
            sys.exit(1)
        self.power_transmitted = ((
            self.power_received.magnitude
            - self.tx_ant_gain.magnitude
            - self.rx_ant_gain.magnitude
            - (20 * math.log10((self.wavelength.magnitude/(4 * math.pi * self.radio_range.magnitude))))            
        ) * ureg("dBm")).to("W")     
    
    def tx_gain(self, radio_range, power_received):
        try:
            self.radio_range = Q_(radio_range).to("m")
            self.power_received = Q_(power_received).to("dBm")
        except DimensionalityError:
            print("You must enter a value with units, e.g. 20 miles or -50 dBm")
            sys.exit(1)
        self.tx_ant_gain = (
            self.power_received.magnitude
            - self.power_transmitted.magnitude
            - self.rx_ant_gain.magnitude
            - (20 * math.log10((self.wavelength.magnitude/(4 * math.pi * self.radio_range.magnitude))))            
        ) * ureg("dBi")        
    
    def rx_gain(self, radio_range, power_received):
        try:
            self.radio_range = Q_(radio_range).to("m")
            self.power_received = Q_(power_received).to("dBm")
        except DimensionalityError:
            print("You must enter a value with units, e.g. 20 miles or -50 dBm")
            sys.exit(1)
        self.rx_ant_gain = (
            self.power_received.magnitude
            - self.power_transmitted.magnitude
            - self.tx_ant_gain.magnitude
            - (20 * math.log10((self.wavelength.magnitude/(4 * math.pi * self.radio_range.magnitude))))            
        ) * ureg("dBi")                                
                
# A30 locks parameters to comply with FS/OAS A-30 testing for wildland fire.
# Frequency is locked and works throughout the AM and FM bands.
    # Changes in range from frequency differences are offset by corresponding changes in path loss.
class A30(RadioTest):
    def __init__(self, separation, freq = "122.925 MHz", tx_ant_gain = "2.15 dBi", rx_ant_gain = "2.15 dBi", power_transmitted = "5 W"):
        try: 
            self.separation = Q_(separation).to("m")
        except DimensionalityError:
            print("You must enter a distance with units, e.g. 20 ft or 5 meters")
            sys.exit(1)   
        self.freq = Q_(freq).to("Hz")            
        self.wavelength = (c / self.freq).to("m") # Converts frequency to wavelength
        self.far_field = 2 * self.wavelength             
        self.tx_ant_gain = Q_(tx_ant_gain).to("dBi")
        self.rx_ant_gain = Q_(rx_ant_gain).to("dBi")
        self.power_transmitted = Q_(power_transmitted).to("dBm")
        self.accuracy = Q_("2 dB") # IFR 4000 RF level accuracy. Provide setting/admin edit.
        self.uncertainty = Q_("1 dB") # Built in error to account for minor differences such as antenna placement       
    
    def field(self):  # Required due to single freq for A30
        if self.separation.magnitude < 6.095:
            print("The test set is too close. The antennas must be at least 20 ft (6.1 m) apart.")
            sys.exit(1)
  
# A30 max effective range
com1 = A30("20 ft")
com1.field()
com1.loss()
com1.limits()
print(f"Test set RF Level must be at least {com1.test_set_rf_24nmi:.2f~P} for 50 nmi range")
print(f"Test set RF Level must be at least {com1.test_set_rf_50nmi:.2f~P} for 50 nmi range")
com1.range(input("Enter test set rf level: "))
print(f"The radio's max effective range is {com1.radio_range:.2f~P}")

# RadioTest max effective range
com2 = RadioTest(separation="30ft", freq="170 MHz", tx_ant_gain="0dBd", rx_ant_gain="0dBd",power_transmitted="5W")
com2.field()
com2.loss()
com2.limits()
print(f"Test set RF Level must be at least {com2.test_set_rf_24nmi:.2f~P} for 50 nmi range")
print(f"Test set RF Level must be at least {com2.test_set_rf_50nmi:.2f~P} for 50 nmi range")
com2.range(input("Enter test set rf level: "))
print(f"The radio's max effective range is {com2.radio_range:.2f~P}")
