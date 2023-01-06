Modbus TCP to Modbus RTU gateway (adapted for Alpha ESS)

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc/4.0/)  

This is my Modbus TCP to Modbus RTU gateway written in Python.
I run it on a [BeagleBone Black](http://beagleboard.org/black) equiped with a USB Modbus RS485 converter to communicate with my Alpha ESS. I salvaged these components from the Crowdcharge controller used with the Wallbox Quasar v2g trial.

The gateway receives a ModbusTCP frame, translates it into a ModbusRTU frame, takes the ModbusRTU response and converts that into the ModbusTCP response for the initial request.

See the file [AlphaModbus.xaml](https://github.com/simeon-simsoft/ModBusGateway/blob/master/AlphaModbus.xaml) for configuration for Home Assistant when using the Alpha ESS battery system

How to use:
```
git clone https://github.com/simeon-simsoft/ModBusGateway.git
cd ModBusGateway
python modbus-gateway.py
```

The configuration can be changed by editing the modbus-gateway.cfg file.

A more detailed description can be found on the original fork site here:
- http://blog.bouni.de/blog/2016/12/02/rs485-on-a-beaglebonegreen-plus-waveshare-cape/
- http://blog.bouni.de/blog/2016/12/10/modbus-tcp-to-modbus-rtu-gatway-on-a-beaglebone-green/
