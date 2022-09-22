import sys
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from client import *
from des import *
from server import *
from create_thread import New_Thread

def create_dialog(title, message):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)

    msg.setText(message)
    msg.setWindowTitle(title)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

    msg.exec_()

class App(QtWidgets.QWidget, New_Thread):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.sel.clicked.connect(self.select_file)
        self.ui.send.clicked.connect(self.send_file)
        self.ui.get.clicked.connect(self.get_file)
        self.ui.pushButton.clicked.connect(self.select_folder)

    def select_file(self):
        fn, _ = QtWidgets.QFileDialog.getOpenFileName()
        self.ui.fil.setText(fn)
    
    def select_folder(self):
        fn = QtWidgets.QFileDialog.getExistingDirectory()
        pwd = get_password()
        try:
            with open(os.path.join(fn, f'{pwd}.temp'), 'w') as f: pass
        except:
            create_dialog('Error', 'Выберите другую папку')
            return
        os.remove(os.path.join(fn, f'{pwd}.temp'))
        self.ui.lineEdit.setText(fn)

    def send_file(self):
        if self.ui.fil.text() == '': return
        if self.ui.ip.text() == '': return
        fn = self.ui.fil.text()
        
        self.new_thread(Sender, (fn, self.ui.ip.text()), self.signal_handler, [lambda: self.ui.send.setDisabled(False), lambda: self.ui.get.setDisabled(False), lambda: create_dialog('OK', 'Файл успешно отправлен')])
        self.ui.filename.setText('Ожидаю подключения')
        self.ui.send.setDisabled(True)
        self.ui.get.setDisabled(True)

    def signal_handler(self, signal):
        self.ui.progressBar.setValue(signal)

    def get_file(self):
        if self.ui.lineEdit.text() == '': return

        self.new_thread(Server, (self.ui.lineEdit.text(), ), self.gsignal_handler, [lambda: self.ui.send.setDisabled(False), lambda: self.ui.get.setDisabled(False),lambda: self.ui.ip_l.setText(''),lambda: self.ui.progressBar_2.setValue(100)])
        
        self.ui.filename.setText('Ожидаю подключения')
        self.ui.send.setDisabled(True)
        self.ui.get.setDisabled(True)

    def gsignal_handler(self, signal):
        match signal[0]:
            case 'IP': self.ui.ip_l.setText(signal[1])
            case 'FN': self.ui.filename.setText(signal[1])
            case 'MAP': self.ui.progressBar_2.setValue(signal[1])
            case 'OK':
                self.ui.progressBar_2.setValue(99)
                create_dialog('OK', 'Файл успешно получен')
                

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = App()
    myapp.show()
    sys.exit(app.exec_())
