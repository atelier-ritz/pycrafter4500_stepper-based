import time
# ==================================
# Class Gimbal
# ==================================
class Gimbal(object):

    def __init__(self,yaw,pitch,spi1,spi2):
        self.yaw = yaw
        self.pitch = pitch
        self.pauseYaw = 0
        self.pausePitch = 0
        self.spi = [spi1, spi2]

    def writeSpi(self,channel,val):
        cmd = 0x11
        self.spi[channel].write([cmd, val])

    def yawGoto(self,value):
        value = 360 - value
        oldYaw = self.yaw
        code = -value/1.445+253 # manual calibration
        code = min(max(int(code), 3), 253)
        self.writeSpi(0,code)
        self.yaw = -(code-253)*1.445
        self.pauseYaw = 2 + 30 / 180 * abs(self.yaw - oldYaw)

    def pitchGoto(self,value):
        oldPitch = self.pitch
        code = -value/1.447 + 128.41 # manual calibration
        code = min(max(int(code), 4), 252)
        self.writeSpi(1,code)
        self.pitch = -(code-128.41)*1.447
        self.pausePitch = 2 + 30 / 180 * abs(self.pitch - oldPitch)

    def goto(self,yawVal,pitchVal):
        self.pitchGoto(pitchVal)
        self.yawGoto(yawVal)
        self.wait_until_finished()

    def wait_until_finished(self):
        wait = max(self.pauseYaw, self.pausePitch)
        self.pauseYaw = 0
        self.pausePitch = 0
        time.sleep(wait)
