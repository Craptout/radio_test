"""Determine radio performance based on the Friis Transmission Equation using decibles for power"
Pr{dB} = Pt{dB} + Gt{dBi} +Gr{dBi} + 20log10((wavelength/(4*pi*d)))
Range (m) = (10^(Pt{dBm} + Gt{dBi} + Gr{dBi} - Pr{dBm} + 180) / 20) / (41.88 * freq{Hz})

variables
---------
Pr = Power recieved
Pt = Power transmitted
Gt = Gain of transmitting antenna
Gr = Gain of receiving antenna
d = separation between transmitting and receiving antennas
Units for wavelength and distance must be the same. 
SI Units are used for calculations and converted for users where needed.
dBi = decibles referenced to an isotropic raditor
dBd = decibles referenced to a dipole antenna (Aviation antennas are generaly 0 dBd)
dBi = dBd + 2.15
dBd = dBi - 2.15
wavelength = speed_of_light / frequency
frequecny = speed_of_light / wavelength
"""

import sys
import math
from pint import UnitRegistry
from pint import DimensionalityError


ureg = UnitRegistry(autoconvert_offset_to_baseunit=True)
# defines dBi and dBd
ureg.load_definitions("my_def.txt")
Q_ = ureg.Quantity
# speed of light
c = Q_("299,792,458 m/s")


class RadioTest:
    def __init__(self):
        try:
            self.freq = Q_(input("Enter Frequency: ")).to("Hz")
        except DimensionalityError:
            print("You must enter units, e.g. Hz or MHz")
            sys.exit(1)          
        self.wavelength = (c / self.freq).to("m") # Converts frequency to wavelength
        self.far_field = 2 * self.wavelength        
        # Comment out Gt, Gr, and Pt in loss and range functions to use these for A-30
        self.Gt = Q_("2.15 dBi")  # Standard aviation antenna (0 dBd) 
        self.Gr = Q_("2.15 dBi")  # Standard aviation antenna (0 dBd)
        self.Pt = Q_("5 W")  # IA fire minimums (5W AM and 4.8W FM multiband)
        self.accuracy = Q_("2 dB") # IFR 4000 RF level accuracy
        self.uncertainty = Q_("1 dB") # Built in error to account for minor differences such as antenna placement

    def field(self):
        try:
            self.separation = Q_(
                input("Enter distance between test set and radio antennas: ")
            ).to("m")
        except DimensionalityError:
            print("You must enter units, e.g. ft or meters")
            self.field()        
        # ensures antennas are in far field
        if self.separation < self.far_field: 
            print(
                f"The test set is too close. The antennas must be greater than {self.far_field.to('ft'):.1f~P} ({self.far_field:.1f~P}) apart."
            )
            sys.exit(1)    
    
    def loss(self):
        # comment out this try/except block to lock to 0 dBd for standard aviation antennas (A-30)
        try:                
            self.Gt = Q_(input("Enter gain of the transmitting antena: ")).to("dBi")
            self.Gr = Q_(input("Enter gain of the receiving antenna: ")).to("dBi")
        except DimensionalityError:
            print("You must enter units: dBi or dBd")                
            self.loss()          
        self.path_loss = (
            (20 * math.log10(self.separation.magnitude))
            + (20 * math.log10(self.freq.magnitude))
            + (20 * (math.log10((4 * math.pi) / c.magnitude)))
            - self.Gt.magnitude                
            - self.Gr.magnitude                
        ) * ureg("dB")
        self.effective_loss = (self.path_loss.magnitude 
        + self.accuracy.magnitude 
        + self.uncertainty.magnitude) * ureg("dB")    
          
    def limits(self):
        # comment out try/except block to lock at 5W for A-30 test
        try:
            self.Pt = Q_(input("Enter power of the transmited signal: ")).to("W")
        except DimensionalityError:
            print("You must enter units, e.g. dBm or W")
            self.limits()            
        self.pr_24 = (
            self.Pt.to("dBm").magnitude
            + self.Gt.to("dBi").magnitude
            + self.Gr.to("dBi").magnitude
            + (20 * math.log10((self.wavelength.magnitude / (4 * math.pi * 44448))))
        ) * ureg(
            "dBm"
        )
        self.pr_50 = (
            self.Pt.to("dBm").magnitude
            + self.Gt.to("dBi").magnitude
            + self.Gr.to("dBi").magnitude
            + (20 * math.log10((self.wavelength.magnitude / (4 * math.pi * 92600))))
        ) * ureg(
            "dBm"
        )  
        # Minimum RF Level from test set needed to simulate 24 nmi range
        self.rf_24 = (self.pr_24.magnitude + self.effective_loss.magnitude) * ureg("dBm")
        # Minimum RF Level from test set needed to simulate 50 nmi range
        self.rf_50 = (self.pr_50.magnitude + self.effective_loss.magnitude) * ureg("dBm")
        # Display rf levels when separation is entered
        print(
            f"Test set RF Level must be at least {self.rf_24:.2f~P} for 24 nmi range"
        )
        print(
            f"Test set RF Level must be at least {self.rf_50:.2f~P} for 50 nmi range"
        )
    
    def range(self):        
        try:
            self.rf_level = Q_(input("Enter test set RF Level that opens receiver: ")).to("dBm")
        except DimensionalityError:
            print("You must enter units, e.g. dBm or W")
            self.range()
        self.Pr = (self.rf_level.magnitude                            
            - self.effective_loss.magnitude            
        ) * ureg("dBm")        
        self.radio_range = (
            (math.pow(10, (self.Pt.to("dBm").magnitude 
                            + self.Gt.magnitude 
                            + self.Gr.magnitude 
                            - self.Pr.magnitude                            
                            + 180) 
                            / 20))
                            / (41.88 * self.freq.magnitude)
        ) * ureg("m")
        print(f"The radio's max effective range is {self.radio_range.to("nmi"):.2f~P}")
        
    
com1 = RadioTest()
com1.field()
com1.loss()
com1.limits()
com1.range()

