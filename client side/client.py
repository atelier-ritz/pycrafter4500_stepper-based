import socket
import threading

class Client(object):
    def __init__(self,host='192.168.31.123',port=9997):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.threads = []
        self.isBusy = False
    def send_data(self,data):
        handle_thread = threading.Thread(target=self._handler, args=(self.sock,), daemon=True)
        handle_thread.start()
        self.sock.sendall(data.encode('utf-8'))
        if 'motorGoAndTouch' in data:
            self.isBusy = True
    def _handler(self,sock):
        while True:
            data = sock.recv(1024)
            returnedStr = data.decode("utf-8")
            print("[Reply]{}".format(returnedStr))
            if returnedStr == 'Motor is done!':
                self.isBusy = False
            return
