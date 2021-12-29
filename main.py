from network import LoRa
import socket
import time
import ubinascii
import pycom
import struct
from pysense import Pysense
from LIS2HH12 import LIS2HH12
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2 , PRESSURE

py = Pysense ()
mp = MPL3115A2 (py , mode = PRESSURE ) # Returns height in meters . Mode may ←- also be set to PRESSURE , returning a value in Pascals
si = SI7006A20 (py)
lt = LTR329ALS01 (py)
li = LIS2HH12 (py)

 # Initialise LoRa in LORAWAN mode .
 # Please pick the region that matches where you are using the device :
 # Asia = LoRa . AS923
 # Australia = LoRa . AU915
 # Europe = LoRa . EU868
 # United States = LoRa . US915

lora = LoRa ( mode = LoRa . LORAWAN , region = LoRa .EU868 , tx_retries =3 , bandwidth = LoRa . BW_500KHZ , sf = 11 , preamble = 8 , device_class = LoRa . CLASS_C )
 # create an OTAA authentication parameters
app_eui = ubinascii . unhexlify ('78373B49F88BA459')
app_key = ubinascii . unhexlify ('561149AF094A98A23D0972B5F7777477')
print (" DevEUI : %s" % ( ubinascii . hexlify ( lora . mac () ) . decode ('ascii ') ) )
print (" app_eui : %s" % ubinascii . hexlify ( app_eui ) . decode ('ascii ') . upper() )
print (" app_key : %s" % ubinascii . hexlify ( app_key ) . decode ('ascii ') . upper() )
 # join a network using OTAA ( Over the Air Activation )
lora . join ( activation = LoRa .OTAA , auth =( app_eui , app_key ) , timeout =0)
 # wait until the module has joined the network
while not lora . has_joined () :
 time . sleep (5)
 print ('Not yet joined ... ')
 print ('***** Joined ! ******* ')

 # create a LoRa socket
s = socket . socket ( socket . AF_LORA , socket . SOCK_RAW )
 # set the LoRaWAN data rate
s. setsockopt ( socket . SOL_LORA , socket .SO_DR , 0)
s. setsockopt ( socket . SOL_LORA , socket . SO_CONFIRMED , False )
while True :
 # make the socket blocking
 # ( waits for the data to be sent and for the 2 receive windows to expire )
      s. setblocking ( True )


 # ********************** Payload Data **********************

      d = []

      d. append(1) # Temperature code
      t = struct . pack ("!h",int(mp. temperature () *10) ) # temperature 1 fraction ( -3276.8 C - - >3276.7 C) (2 bytes )
      d. append (t [0])
      d. append (t [1])
      d. append (2) # Humidity code
      d. append (int (si. humidity () ) ) # Humidity data 0 -100% (1 byte )
      d. append (3) # Acceleration code
      ac=li. acceleration () # acceleration data X,Y,Z -128 --> 127 +/ -63=1 G (3 bytes )
      d. append ( struct . pack ("!b",int (ac [0]*100) ) [0]) #X parameters
      d. append ( struct . pack ("!b",int (ac [1]*100) ) [0]) #Y parameters
      d. append ( struct . pack ("!b",int (ac [2]*100) ) [0]) #Z parameters
      d. append (4) # Light code
      bt= struct . pack ("!h",int (lt. light () [0]) ) # Light data ( Blue lux ) 0 -65535 lux (2 byte )
      d. append (bt [0])
      d. append (bt [1])
      d. append (7) # Battery code
      bt= struct . pack ("!h",int (py. read_battery_voltage () *1000) ) # Battery data 0 -65535 mV( milliVolt ) (2 byte )
      d. append (bt [0])
      d. append (bt [1])
      d. append (20) # dec 14 -> pressure code
      p= struct . pack ("!i",int (mp. pressure () *10) ) # pressure data (in server side data /1000 -> mb( millibar ) or hpa ( hectopascal )) (4 byte )
      d. append (p [0])
      d. append (p [1])
      d. append (p [2])
      d. append (p [3])
      s. send ( bytes (d) )
      time . sleep (600)
 # *******************************************************
 # make the socket non - blocking
 # ( because if there ’s no data received it will block forever ...)
      s. setblocking ( False )
 # get any data received (if any ...)
      data = s. recv (64)
      print ('data')