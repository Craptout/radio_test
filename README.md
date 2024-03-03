Purpose
-------
Determine radio performance based on the Friis Transmission Equation using decibles for power
Pr{dB} = Pt{dB} + Gt{dBi} + Gr{dBi} + 20log10((wavelength/(4*pi*d)))
Range (m) = (10^(Pt{dBm} + Gt{dBi} + Gr{dBi} - Pr{dBm} + 180) / 20) / (41.88 * freq{Hz})

Includes class with preset variables for FS/OAS A-30 radio range test for wildland fire.

Variables
---------
Pr = Power recieved \n
Pt = Power transmitted \n
Gt = Gain of transmitting antenna = tx_ant_gain \n
Gr = Gain of receiving antenna = rx_ant_gain \n
d = separation between transmitting and receiving antennas \n
Units for wavelength and distance must be the same. \n 
SI Units are used for calculations and converted for users where needed. \n
dBi = decibles referenced to an isotropic raditor = dBd + 2.15 \n
dBd = decibles referenced to a dipole antenna = dBi - 2.15  \n
Aviation antennas are generally 0 dBd. \n
wavelength = speed_of_light / frequency \n

License
-------
See the LICENSE file for license rights and limitations (BSD-3-Clause).

