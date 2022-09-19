import pickle
import socket
import os

import rsa
from encryptor import *
from PyQt5 import QtCore
from netifaces import interfaces, ifaddresses, AF_INET

class Server(QtCore.QObject):
    mysignal = QtCore.pyqtSignal(list)
    fineshed = QtCore.pyqtSignal()

    def __init__(self, folder, parent=None) -> None:
        QtCore.QThread.__init__(self, parent)
        self.name = ''
        self.size = 0
        self.folder = folder
        
    def start(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addresses = []
        for ifaceName in interfaces():
            addresses += [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        self.myip = encryptor.encrypt(pickle.dumps(addresses), 'IP')
        self.server.bind(('', 2000))
        self.server.listen(0)
        self.mysignal.emit(['IP', self.myip])
        self.user, self.adres = self.server.accept()
        while True:
            try:
                key = pickle.loads(self.user.recv(1048576))
            except:
                break
            match key[0]:
                case 'NAME':
                    self.name = key[1]
                    self.mysignal.emit(['FN', self.name])
                    f = open(os.path.join(self.folder, self.name), 'w')
                case 'SIZE':
                    self.size = key[1]
                    self.user.send(pickle.dumps(''))
                case 'GET_KEY':
                    (public_key, private_key) = rsa.newkeys(512)
                    self.user.send(pickle.dumps(public_key))
                case 'PASSWORD':
                    self.password = rsa.decrypt(key[1], private_key).decode()
                case 'MAP':
                    self.mysignal.emit(['MAP', round(100/(self.size/key[2]))])
                    f.write(key[1])
                    self.user.send(pickle.dumps(''))
                case 'END':
                    self.mysignal.emit(['OK'])
                    f.close()
                    with open(os.path.join(self.folder, self.name), 'r') as f:
                        e = f.read()
                    payload = encryptor.decrypt(e, self.password)
                    with open(os.path.join(self.folder, self.name), 'wb') as f:
                        f.write(payload)
                    break
        self.server.close()
        self.fineshed.emit()
