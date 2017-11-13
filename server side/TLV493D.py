import smbus
import time
import math
import threading
import os

# Register and other configuration values:
I2C_ADDRESS = 0x5e

class TLV493D():
     """Base functionality for TLV493D 3-axis hall sensors."""
     bus = smbus.SMBus(1)
     def __init__(self):
          self.field = [0,0,0]     # x,y,z (mT)
          self.mag = 0
          self.theta = 0
          self.phi = 0
          self.bus.write_block_data(I2C_ADDRESS,0,[0,5]) # enable INT; Low power mode
          time.sleep(.1)
          thread = threading.Thread(target=self.update)
          thread.start()
     def bit2mT(self,bit):
          msb = bit >> 11
          val = bit & 0x7ff
          if msb == 0b01:
               val = val - 2048
          val = val * 0.098
          return val
     def update(self):
          buffer = self.bus.read_i2c_block_data(I2C_ADDRESS,0x00,6)
          x_bit = (buffer[0] << 4) + (buffer[4] >> 4)
          y_bit = (buffer[1] << 4) + (buffer[4] & 0x0f)
          z_bit = (buffer[2] << 4) + (buffer[5] & 0x0f)
          x_mT = self.bit2mT(x_bit)
          y_mT = self.bit2mT(y_bit)
          z_mT = self.bit2mT(z_bit)
          self.field = [x_mT,y_mT,z_mT]
          self.mag = math.sqrt(x_mT**2 + y_mT**2 + z_mT**2)
          self.theta = math.atan2(y_mT,x_mT) / math.pi * 180
          self.phi = math.acos(z_mT/self.mag) / math.pi * 180
          print(self.field)
          thread = threading.Timer(1,self.update)
          thread.start()

if __name__ == "__main__":
     sensor = TLV493D()
##     for i in range(5000):
##          sensor.update()
##          print(sensor.field)
##          print('magnitude{}'.format(sensor.mag))
##          print('theta{}'.format(sensor.theta))
##          print('phi{}'.format(sensor.phi))
##          time.sleep(0.2)
