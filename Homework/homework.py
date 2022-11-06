import sys

import time

import logging

from PyQt5 import QtCore
from PyQt5.QtCore import (
    QObject,
    QThreadPool, 
    QRunnable, 
    pyqtSignal, 
    pyqtSlot
)

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QComboBox,
    QHBoxLayout,
    QWidget,
)

import serial
import serial.tools.list_ports


# Globals
CONN_STATUS = False
BAUDRATE = 9600
COM_PORT = "COM3"


# Logging config
logging.basicConfig(format="%(message)s", level=logging.INFO)

#########################
# SERIAL_WORKER_SIGNALS #
#########################
class SerialWorkerSignals(QObject):
    """!
    @brief Class that defines the signals available to a serialworker.

    Available signals (with respective inputs) are:
        - device_port:
            str --> port name to which a device is connected
        - status:
            str --> port name
            int --> macro representing the state (0 - error during opening, 1 - success)
    """
    device_port = pyqtSignal(str)
    status = pyqtSignal(str, int)

#################
# SERIAL_WORKER #
#################
class SerialWorker(QRunnable):
    """!
    @brief Main class for serial communication: handles connection with device.
    """
    def __init__(self, serial_port_name):
        """!
        @brief Init worker.
        """
        global BAUDRATE

        self.is_killed = False
        super().__init__()
        # init port, params and signals
        self.port = serial.Serial()
        self.port_name = serial_port_name
        self.baudrate = BAUDRATE 
        self.signals = SerialWorkerSignals()

    @pyqtSlot()
    def run(self):
        """!
        @brief Estabilish connection with desired serial port.
        """
        global CONN_STATUS

        if not CONN_STATUS:
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port.is_open:
                    CONN_STATUS = True
                    self.signals.status.emit(self.port_name, 1)
                    time.sleep(0.01)     
            except serial.SerialException:
                logging.info("Error with port {}.".format(self.port_name))
                self.signals.status.emit(self.port_name, 0)
                time.sleep(0.01)

    @pyqtSlot()
    def send(self, char):
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.write(char.encode('utf-8'))
            logging.info("Written {} on port {}.".format(char, self.port_name))
        except:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))

   
    @pyqtSlot()
    def killed(self):
        """!
        @brief Close the serial port before closing the app.
        """
        global CONN_STATUS
        if self.is_killed and CONN_STATUS:
            self.port.close()
            time.sleep(0.01)
            CONN_STATUS = False
            self.signals.device_port.emit(self.port_name)

        logging.info("Killing the process")

###############
# MAIN WINDOW #
###############
class MainWindow(QMainWindow):

    global COM_PORT

    def __init__(self):
        """!
        @brief Init MainWindow.
        """
        # define worker
        self.serial_worker = SerialWorker(None)

        super(MainWindow, self).__init__()

        # title and geometry
        self.setWindowTitle("GUI")
        width = 400
        height = 320
        self.setMinimumSize(width, height)

        # create thread handler
        self.threadpool = QThreadPool()

        self.connected = CONN_STATUS
        self.serialscan()
        self.initUI()
        self.connection()


    #####################
    # GRAPHIC INTERFACE #
    #####################
    def initUI(self):
        """!
        @brief Set up the graphical interface structure.
        """
        # layout
        button_hlay = QHBoxLayout()
        button_hlay.addWidget(self.led_on)
        button_hlay.addWidget(self.led_off)
        widget = QWidget()
        widget.setLayout(button_hlay)
        self.setCentralWidget(widget)


    ####################
    # SERIAL INTERFACE #
    ####################
    def serialscan(self):
        """!
        @brief Scans all serial ports and create a list.
        """
        """ # create the combo box to host port list
        self.COM_PORT = ""
        self.led_on = QComboBox()
        self.led_on.currentTextChanged.connect(self.port_changed)
        """
        # create the buttonS
        self.led_off = QPushButton(
            text=("LED OFF"), 
            checkable=True,
            clicked=self.switch_off
        )

        self.led_on = QPushButton(
            text=("LED ON"), 
            checkable=True,
            clicked=self.switch_on
        )
    
    ##################
    # SERIAL SIGNALS #
    ##################

    @pyqtSlot(bool)
    def switch_on(self):
        """!
        @brief Send char and switch the led on
        """
        self.serial_worker.send("b")
        self.led_on.setDisabled(True)
        self.led_off.setDisabled(False)

    @pyqtSlot(bool)
    def switch_off(self):
        """!
        @brief Send char and switch the led off
        """
        self.serial_worker.send("s")
        self.led_off.setDisabled(True)
        self.led_on.setDisabled(False)

    @pyqtSlot(bool)
    def connection(self):
        """!
        @brief Allow connection and disconnection from selected serial port.
        """
        global COM_PORT

        #if checked:
            # setup reading worker
        self.serial_worker = SerialWorker(COM_PORT) # needs to be re defined
            # connect worker signals to functions
            #self.serial_worker.signals.status.connect(self.check_serialport_status)
            #self.serial_worker.signals.device_port.connect(self.connected_device)
            # execute the worker
        self.threadpool.start(self.serial_worker)

        #else:
            # kill thread
            #self.serial_worker.is_killed = True
            #self.serial_worker.killed()


    def ExitHandler(self):
        """!
        @brief Kill every possible running thread upon exiting application.
        """
        self.serial_worker.is_killed = True
        self.serial_worker.killed()

#############
#  RUN APP  #
#############
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.ExitHandler)
    w.show()
    sys.exit(app.exec_())

