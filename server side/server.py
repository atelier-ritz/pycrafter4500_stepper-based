import socket
import threading
import time

class Server(object):
    def __init__(self,motormanager,host='192.168.31.118',port=9997):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        self.sock.bind((host, port))
        self.sock.listen(1) # backlog: specifies the maximum number of queued connections
        self.client = [] # [con, address]
        self.mm = motormanager

    def str2list(self,commandStr):
        return commandStr.split(',')
    def start(self):
        print('Host: {}, Port: {}'.format(self.host, self.port))
        print('Waiting for client connection ...')
        con, address = self.sock.accept()
        print("[Connected] {}".format(address))
        self.client.append((con, address))
        handle_thread = threading.Thread(target=self._handler, args=(con, address), daemon=True)
        handle_thread.start()
    def remove_conection(self,con,address):
        print('[Terminated] {}'.format(address))
        con.close()
        self.client.remove((con, address))
        # self.cmd = 'quit'

        print('Waiting for client connection ...')
        con, address = self.sock.accept()
        print("[Connected] {}".format(address))
        self.client.append((con, address))
        handle_thread = threading.Thread(target=self._handler, args=(con, address), daemon=True)
        handle_thread.start()

    def _handler(self,con,address):
        while True:
            try:
                data = con.recv(1024)
            except ConnectionResetError:
                self.remove_conection(con, address)
                break
            else:
                if not data:
                    self.remove_conection(con, address)
                    break
                else:
                    command = data.decode("utf-8")
                    print("[Received] {} - {}".format(address, command))
                    if not command  == ['']:
                        commandList = self.str2list(command)
                        print(commandList)
                        self.analyzecmd(commandList)
                    # self.client[0][0].sendto('received'.encode(), self.client[0][1])

    def analyzecmd(self,cmd):
        mm = self.mm
        if cmd[0] == 'powerOn':
            mm.power_on()
        if cmd[0] == 'powerOff':
            mm.power_off()
        if cmd[0] == 'setparam':
            mm.set_param(int(cmd[3]),int(cmd[4]),int(cmd[1]),int(cmd[2]))
        if cmd[0] == 'motorgo1':
            mm.motor_run(1,int(cmd[1]),int(cmd[2]),wait=False)
        if cmd[0] == 'motorgo2':
            mm.motor_run(2,int(cmd[1]),int(cmd[2]),wait=False)
        if cmd[0] == 'phigo':
            mm.motor1_toPhi(int(cmd[1]))
        if cmd[0] == 'thetago':
            mm.motor2_toTheta(int(cmd[1]))
        if cmd[0] == 'fieldgo':
            mm.motor12_choose_strategy(int(cmd[1]),int(cmd[2]))
        if cmd[0] == 'setphisingularity':
            mm.set_phiSingularity(int(cmd[1]))
        if cmd[0] == 'macro1':
            mm.macro1()
