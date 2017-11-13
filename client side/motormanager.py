
class MotorManager(object):
    def __init__(self,client):
        self.client = client
        self.rpm = [20, 20] # incorrect???
        self.stepperrev = [200, 200]

    def _sendCommand(self,command):
        client = self.client
        client.send_data(command)
        print('command sent {}'.format(command))

    def motorgo(self,motorId,val):
        if val == 0 :
            return
        step = abs(val)
        direction = int(val/step)
        self.position[motorId] += val
        command = 'motorgo{},{},{}'.format(motorId+1,step,direction)
        self._sendCommand(command)
    def setParam(self,rpm1,rpm2,stepperrev1,stepperrev2):
        command = 'setparam,{},{},{},{}'.format(rpm1,rpm2,stepperrev1,stepperrev2)
        self._sendCommand(command)
    def powerOn(self):
        command = 'powerOn'
        self._sendCommand(command)
    def powerOff(self):
        command = 'powerOff'
        self._sendCommand(command)
