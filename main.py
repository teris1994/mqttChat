from PyQt5 import QtCore, QtGui, QtWidgets
import paho.mqtt.client as mqtt


class MqttClient(QtCore.QObject):
    Disconnected = 0
    Connecting = 1
    Connected = 2

    MQTT_3_1 = mqtt.MQTTv31
    MQTT_3_1_1 = mqtt.MQTTv311

    connected = QtCore.pyqtSignal()
    disconnected = QtCore.pyqtSignal()

    stateChanged = QtCore.pyqtSignal(int)
    hostnameChanged = QtCore.pyqtSignal(str)
    portChanged = QtCore.pyqtSignal(int)
    keepAliveChanged = QtCore.pyqtSignal(int)
    cleanSessionChanged = QtCore.pyqtSignal(bool)
    protocolVersionChanged = QtCore.pyqtSignal(int)

    messageSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(MqttClient, self).__init__(parent)

        self.m_hostname = ""
        self.m_port = 1883
        self.m_keepAlive = 60
        self.m_cleanSession = True
        self.m_protocolVersion = MqttClient.MQTT_3_1

        self.m_state = MqttClient.Disconnected

        self.m_client = mqtt.Client(clean_session=self.m_cleanSession,protocol=self.protocolVersion)

        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_disconnect = self.on_disconnect
        self.m_client.on_publish = self.on_publish

    @QtCore.pyqtProperty(int, notify=stateChanged)
    def state(self):
        return self.m_state

    @state.setter
    def state(self, state):
        if self.m_state == state: return
        self.m_state = state
        self.stateChanged.emit(state)

    @QtCore.pyqtProperty(str, notify=hostnameChanged)
    def hostname(self):
        return self.m_hostname

    @hostname.setter
    def hostname(self, hostname):
        if self.m_hostname == hostname: return
        self.m_hostname = hostname
        self.hostnameChanged.emit(hostname)

    @QtCore.pyqtProperty(int, notify=portChanged)
    def port(self):
        return self.m_port

    @port.setter
    def port(self, port):
        if self.m_port == port: return
        self.m_port = port
        self.portChanged.emit(port)

    @QtCore.pyqtProperty(int, notify=keepAliveChanged)
    def keepAlive(self):
        return self.m_keepAlive

    @keepAlive.setter
    def keepAlive(self, keepAlive):
        if self.m_keepAlive == keepAlive: return
        self.m_keepAlive = keepAlive
        self.keepAliveChanged.emit(keepAlive)

    @QtCore.pyqtProperty(bool, notify=cleanSessionChanged)
    def cleanSession(self):
        return self.m_cleanSession

    @cleanSession.setter
    def cleanSession(self, cleanSession):
        if self.m_cleanSession == cleanSession: return
        self.m_cleanSession = cleanSession
        self.cleanSessionChanged.emit(cleanSession)

    @QtCore.pyqtProperty(int, notify=protocolVersionChanged)
    def protocolVersion(self):
        return self.m_protocolVersion

    @protocolVersion.setter
    def protocolVersion(self, protocolVersion):
        if self.m_protocolVersion == protocolVersion: return
        if protocolVersion in (MqttClient.MQTT_3_1, MQTT_3_1_1):
            self.m_protocolVersion = protocolVersion
            self.protocolVersionChanged.emit(protocolVersion)

    #################################################################
    @QtCore.pyqtSlot()
    def connectToHost(self):
        if self.m_hostname:
            self.m_client.connect(self.m_hostname,
                                  port=self.port,
                                  keepalive=self.keepAlive)

            self.state = MqttClient.Connecting
            self.m_client.loop_start()

    @QtCore.pyqtSlot()
    def disconnectFromHost(self):
        self.m_client.disconnect()

    def subscribe(self, path):
        if self.state == MqttClient.Connected:
            self.m_client.subscribe(path)

    #################################################################
    # callbacks
    def on_message(self, mqttc, obj, msg):
        mstr = msg.payload.decode("ascii")
        # print("on_message", mstr, obj, mqttc)
        self.messageSignal.emit(mstr)

    def on_publish(self, *args):
        print("Message send (on_publish)")
    def on_connect(self, *args):
        # print("on_connect", args)
        self.state = MqttClient.Connected
        self.connected.emit()

    def on_disconnect(self, *args):
        # print("on_disconnect", args)
        self.state = MqttClient.Disconnected
        self.disconnected.emit()


class Ui_Dialog(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.client = MqttClient(self)
        self.client.stateChanged.connect(self.on_stateChanged)
        self.client.messageSignal.connect(self.on_messageSignal)
        self.client.hostname = "mqtt.eclipseprojects.io"
        self.client.connectToHost()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(745, 556)
        Dialog.setAutoFillBackground(True)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(False)

        self.sendButton = QtWidgets.QPushButton(Dialog)
        self.sendButton.setGeometry(QtCore.QRect(550, 480, 181, 71))
        self.sendButton.setAutoFillBackground(False)
        self.sendButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/paper-plane.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.sendButton.setIcon(icon)
        self.sendButton.setIconSize(QtCore.QSize(32, 32))
        self.sendButton.setObjectName("sendButton")

        self.plainTextChatSend = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextChatSend.setGeometry(QtCore.QRect(10, 480, 531, 71))
        self.plainTextChatSend.setObjectName("plainTextChatSend")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(550, 200, 47, 13))
        self.label_4.setObjectName("label_4")

        self.plainTextChatView = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextChatView.setGeometry(QtCore.QRect(10, 30, 531, 441))
        self.plainTextChatView.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.plainTextChatView.setAutoFillBackground(False)
        self.plainTextChatView.setInputMethodHints(QtCore.Qt.ImhMultiLine)
        self.plainTextChatView.setFrameShape(QtWidgets.QFrame.Panel)
        self.plainTextChatView.setReadOnly(True)
        self.plainTextChatView.setOverwriteMode(False)
        self.plainTextChatView.setBackgroundVisible(False)
        self.plainTextChatView.setObjectName("plainTextChatView")

        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(550, 220, 181, 251))
        self.plainTextEdit.setFrameShape(QtWidgets.QFrame.HLine)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.tabWidget = QtWidgets.QTabWidget(Dialog)
        self.tabWidget.setGeometry(QtCore.QRect(550, 30, 181, 151))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_2.setGeometry(QtCore.QRect(10, 80, 151, 20))
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.lineEdit_2.setClearButtonEnabled(True)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(10, 60, 47, 13))
        self.label_2.setObjectName("label_2")
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 10, 47, 13))
        self.label.setObjectName("label")

        self.lineEdit = QtWidgets.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 151, 20))
        self.lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")

        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/id-card.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.tabWidget.addTab(self.tab, icon1, "")
        self.tab_2_crypt = QtWidgets.QWidget()
        self.tab_2_crypt.setObjectName("tab_2_crypt")
        self.checkBox = QtWidgets.QCheckBox(self.tab_2_crypt)
        self.checkBox.setGeometry(QtCore.QRect(0, 0, 151, 17))
        self.checkBox.setObjectName("checkBox")
        self.label_3 = QtWidgets.QLabel(self.tab_2_crypt)
        self.label_3.setGeometry(QtCore.QRect(0, 20, 151, 16))
        self.label_3.setObjectName("label_3")

        self.lineEdit_3 = QtWidgets.QLineEdit(self.tab_2_crypt)
        self.lineEdit_3.setGeometry(QtCore.QRect(0, 40, 151, 20))
        self.lineEdit_3.setInputMethodHints(
            QtCore.Qt.ImhNoAutoUppercase | QtCore.Qt.ImhNoPredictiveText | QtCore.Qt.ImhSensitiveData)
        self.lineEdit_3.setInputMask("")
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.lineEdit_3.setClearButtonEnabled(True)
        self.lineEdit_3.setObjectName("lineEdit_3")

        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/icons/blackboard.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.tabWidget.addTab(self.tab_2_crypt, icon2, "")
        self.plainTextChatSend.raise_()
        self.label_4.raise_()
        self.plainTextChatView.raise_()
        self.sendButton.raise_()
        self.plainTextEdit.raise_()
        self.tabWidget.raise_()

        self.retranslateUi(Dialog)
        self.tabWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Dialog)


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "MQTT Chat"))
        self.label_4.setText(_translate("Dialog", "Logs"))
        self.label_2.setText(_translate("Dialog", "Password"))
        self.label.setText(_translate("Dialog", "Username"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Dialog", "Account"))
        self.checkBox.setText(_translate("Dialog", "Crypt Enable"))
        self.label_3.setText(_translate("Dialog", "Key"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2_crypt), _translate("Dialog", "Crypt"))


    def send_chat_message(self):
        print("Send Button clicked")
        'Get text from chat write box'
        text = self.plainTextChatSend.toPlainText()

        if len(text)>0:
            'Publish the text'
            self.client.m_client.publish(topic="chat_lefteris_special_lala",payload=str(text),qos=0)
            self.plainTextChatSend.setPlainText("")
        else:
            pass


    @QtCore.pyqtSlot(int)
    def on_stateChanged(self, state):
        if state == MqttClient.Connected:
            print(state)
            #self.client.subscribe("wx.senia.org/#")
            self.client.subscribe("chat_lefteris_special_lala/#")

    @QtCore.pyqtSlot(str)
    def on_messageSignal(self, msg):
        try:
            self.plainTextChatView.appendPlainText(msg + "\n")
        except ValueError:
            print("error: Not is number")

    @QtCore.pyqtSlot(str)
    def on_publishMessage(self, msg):
        try:
            self.client
        except ValueError:
            print("error: Not is number")
import resource_rc

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()

    ui.setupUi(Dialog)

    Dialog.show()
    #Dialog.setStyleSheet('''
    # {
    #    background-image: url(grandboss.jpg);
    #    }''')
    # This is a singal for call a fuction when click sendButton
    ui.sendButton.clicked.connect(ui.send_chat_message)

    sys.exit(app.exec_())