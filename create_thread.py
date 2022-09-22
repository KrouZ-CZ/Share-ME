from PyQt5 import QtCore

class New_Thread:
    def __init__(self):
        pass

    def new_thread(self, target, args:tuple, signal_handler, after_end=[]):
        self.thread = QtCore.QThread()
        self.signal = target(*args)
        self.signal.moveToThread(self.thread)

        self.signal.mysignal.connect(signal_handler)
        self.thread.started.connect(self.signal.run)
        self.signal.fineshed.connect(self.thread.quit)
        self.signal.fineshed.connect(self.signal.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        for item in after_end:
            self.thread.finished.connect(item)

        self.thread.start()