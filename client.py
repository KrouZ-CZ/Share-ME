import os
import pickle
import random
import socket
import string
import sys

import rsa
from encryptor import *
from PyQt5 import QtCore

def get_password(rang=10) -> str:
    chars = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
    pwd = [random.choice(chars) for _ in range(rang)]
    return ''.join(pwd)

class Sender(QtCore.QObject):
    mysignal = QtCore.pyqtSignal(int)
    fineshed = QtCore.pyqtSignal()

    def __init__(self, name, ip, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.name = name
        self.ip = pickle.loads(encryptor.decrypt(ip, 'IP'))

    class Client:
        def __init__(self, client) -> None:
            self.client = client

        def send(self, msg) -> None:
            self.client.send(pickle.dumps(msg))

        def recv(self) -> any:
            return pickle.loads(self.client.recv(1024))

    def run(self) -> None:
        ok = False
        for item in self.ip:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((item, 2000))
                ok = True
                break
            except:
                pass
        if ok == False:
            self.fineshed.emit()
            return
        c = self.Client(client)

        name = self.name
        with open(name, 'rb') as f:
            opayload = f.read()

        c.send(['GET_KEY'])
        key = c.recv()

        password = get_password()
        self.mysignal.emit(1)
        en_pwd = rsa.encrypt(password.encode(), key)
        c.send(['PASSWORD', en_pwd])

        payload = encryptor.encrypt(opayload, password)

        size = sys.getsizeof(payload)
        c.send(['NAME', os.path.basename(name)])
        c.send(['SIZE', size])
        c.recv()
        for i in range(0, len(payload), 35000):
            try:
                c.send(['MAP', payload[i:i+35000], i if i != 0 else 1])
            except:
                c.send(['MAP', payload[i:-1]])
            self.mysignal.emit(round(100/(size/i if i != 0 else 1)))
            c.recv()
        self.mysignal.emit(100)
        c.send(['END'])
        c.client.close()
        self.fineshed.emit()