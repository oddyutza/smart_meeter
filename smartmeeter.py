#!/usr/bin/python3
####
## this is for Hager ECR140D so let's monitor our house power consumption
####

#let's import theese
from influxdb import InfluxDBClient
import minimalmodbus

# influx configuration
ifuser = ""
ifpass = ""
ifdb   = ""
ifhost = ""
ifport = 8086
measurement_name = ""

# modbus rs485 configuration
rs485 = minimalmodbus.Instrument('/dev/modbus', 1)
rs485.serial.baudrate = 19200
#rs485.serial.bytesize = 8
rs485.serial.parity = minimalmodbus.serial.PARITY_EVEN
rs485.serial.stopbits = 1
rs485.serial.timeout = 1
rs485.debug = False
rs485.mode = minimalmodbus.MODE_RTU
#print(rs485)

# let's read from rs485, with read address in DEC
# Instantaneous Measures
Live_Voltage = rs485.read_register(45056, functioncode=3, signed=False) / 100.0 # U16 V/100
Live_Frequency = rs485.read_register(45062, functioncode=3, signed=False ) / 100 # U16 Hz/100
Live_Current_ma = rs485.read_long(45065, functioncode=3, signed=False) # U32 mA
Live_Current_a = rs485.read_long(45065, functioncode=3, signed=False) / 1000.0 # U32 A
Live_Active_Power = rs485.read_long(45081, functioncode=3, signed=True ) * 10 #S32 W/0.1
Live_KvA = rs485.read_long(45093, functioncode=3, signed=False) / 100.0 # U32 KvA/100
#Live_PF_IEC = rs485.read_register(45099, functioncode=3, signed=False) / 1000.0 # S16 PF / 1000
Live_PF_IEE = rs485.read_register(45102, functioncode=3, signed=False) / 1000.0 # S16 PF / 1000
# Energies per Tariff #1
Sum_Active_Power = rs485.read_long(45248, functioncode=3, signed=True ) # U32 kWh

# debug below, AKA print to stdout
## Instantaneous Measures
#print('Live Voltage: {0:.2f} Volts'.format(Live_Voltage))
#print('Live Frequency: {0:.2f} Hz'.format(Live_Frequency))
#print('Live Current: {0:.0f} mAmps'.format(Live_Current))
#print('Live Current: {0:.2f} Amps'.format(Live_Current / 100.0))
#print('Live Active Power: {0:.0f} Watts'.format(Live_Active_Power))
#print('Live KvA: {0:.2f} KvA'.format(Live_KvA))
#print('Live PF IEC: {0:.2f} PowerFactor IEC'.format(Live_PF_IEC))
#print('Live PF IEE: {0:.2f} PowerFactor IEE'.format(Live_PF_IEE))
## Energies per Tariff 1
#print('Sum Active Power: {0:.0f} kWh'.format(Sum_Active_Power))


# format the data as a single measurement for influx
body = [
    {
        "measurement": measurement_name,
        "tags": { "device": "Hager ECR140D" },
        "fields": {
            "Live Voltage": int(Live_Voltage),
            "Live Frequency": int(Live_Frequency),
            "Live Current ma": int(Live_Current_ma),
            "Live Current Amp": int(Live_Current_a),
            "Live Active Power": int(Live_Active_Power),
            "Live KvA": int(Live_KvA),
            "Live Power Factor IEE Phase1": int(Live_PF_IEE),
            "Sum Active Power": int(Sum_Active_Power),
        }
    }
]

# connect to influx
ifclient = InfluxDBClient(ifhost,ifport,ifuser,ifpass,ifdb)

# write the measurement
ifclient.write_points(body)
