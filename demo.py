#!/usr/bin/python
from ABE_ADCDACPi import ADCDACPi
import time
adcdac = ADCDACPi()
adcdac.set_adc_refvoltage(3.3)

while True:
   v = adcdac.read_adc_voltage(1)
   if (v < 2.2) :
      print v
   time.sleep(0.001)
