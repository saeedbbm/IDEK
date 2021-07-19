

from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import numpy as np
import os
import shutil
import distutils.dir_util
# from distutils.dir_util import copy_tree

class CheckableComboBox(QtWidgets.QComboBox):
    # Subclass Delegate to increase item height
    class Delegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = QtWidgets.qApp.palette()
        palette.setBrush(QtGui.QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == QtCore.Qt.Checked:
                    item.setCheckState(QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(QtCore.Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == QtCore.Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QtGui.QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, QtCore.Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QtGui.QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)


    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == QtCore.Qt.Checked:
                res.append(self.model().item(i).data())
        return res

# Sorting Table with sortKey
class MyTableWidgetItem(QtWidgets.QTableWidgetItem):
    def __init__(self, text, sortKey):
            QtWidgets.QTableWidgetItem.__init__(self, text, QtWidgets.QTableWidgetItem.UserType)
            self.sortKey = sortKey

    #Qt uses a simple < check for sorting items, override this to use the sortKey
    def __lt__(self, other):
            return self.sortKey < other.sortKey

class Ui_Form(object):
    def __init__(self):
        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        print(self.upFolder)

        self.old_user = 0
        self.AlarmPosition = -1
        self.AP_range = 1
        self.AlarmHeight = -0.25
        self.AH_range = 0.1
        self.AlarmAngle = -30
        self.AA_range = 30
        self.AlarmPicSignal = 0
        self.ID1 = 1000
        self.ID2 = 2000
        self.ID3 = 3000
        self.rowCount1 = 0
        self.rowCount2 = 0
        
    def setupUi(self, Form):
        # Form.setObjectName("Form")
        # Form.resize(1400, 960)

        self.SettingArray = np.loadtxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Setting/setting.txt', delimiter=',')
        self.AutoArray = np.loadtxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Auto/Auto.txt', delimiter=',')
        # self.SettingArray = np.loadtxt('Users/'+self.OperatorName_text.text()+'/Setting/setting.txt', delimiter=',')
#         print("\n\nSSS\n\n",self.AutoArray)
        
        self.layout = QtWidgets.QGridLayout(Form)
        Width = 1560
        Height = 860
        Form.setFixedWidth(Width)
        Form.setFixedHeight(Height)

        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget(Form)
        self.tab1 = QtWidgets.QWidget(Form)
        self.tab2 = QtWidgets.QWidget(Form)
        # self.tabs.resize(960, 960)

        # Add tabs
        self.tabs.addTab(self.tab1, "Main")
        self.tabs.addTab(self.tab2, "Setting")


        # Create first tab

        VLayout_t1 = QtWidgets.QGridLayout()
        VLayout_t1.setVerticalSpacing(2)
        aLayout_t1 = QtWidgets.QHBoxLayout()
        bLayout_t1 = QtWidgets.QHBoxLayout()
        cLayout_t1 = QtWidgets.QHBoxLayout()

        VLayout_t1.addLayout(aLayout_t1,0,0)
        VLayout_t1.addLayout(bLayout_t1,1,0)
        VLayout_t1.addLayout(cLayout_t1,2,0)
        self.tab1.setLayout(VLayout_t1)

        frame11_t1=QtWidgets.QFrame()
        frame11_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        aLayout_t1.addWidget(frame11_t1,3)

        frame12_t1 = QtWidgets.QFrame()
        frame12_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        aLayout_t1.addWidget(frame12_t1,3)

        frame21_t1 = QtWidgets.QFrame()
        frame21_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bLayout_t1.addWidget(frame21_t1,3)

        frame22_t1 = QtWidgets.QFrame()
        frame22_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bLayout_t1.addWidget(frame22_t1,3)

        frame31_t1 = QtWidgets.QFrame()
        frame31_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        cLayout_t1.addWidget(frame31_t1,3)

        frame32_t1 = QtWidgets.QFrame()
        frame32_t1.setFrameShape(QtWidgets.QFrame.StyledPanel)
        cLayout_t1.addWidget(frame32_t1,3)

        frame11_t1.setMinimumHeight(350)
        frame21_t1.setMaximumHeight(200)
        frame31_t1.setMaximumHeight(100)

        frame12_t1.setMinimumHeight(350)
        frame22_t1.setMaximumHeight(200)
        frame32_t1.setMaximumHeight(100)

        # Left Section
        layout_t1 = QtWidgets.QVBoxLayout()
        frame11_t1.setLayout(layout_t1)

        groupbox1_t1 = QtWidgets.QGroupBox("Camera")
        layout_t1.addWidget(groupbox1_t1,5)

        vbox_t1 = QtWidgets.QGridLayout()
        groupbox1_t1.setLayout(vbox_t1)

        self.control_bt = QtWidgets.QPushButton("Start")
        vbox_t1.addWidget(self.control_bt,0,0)

        self.motion_check = QtWidgets.QCheckBox("Motion Detection")
        vbox_t1.addWidget(self.motion_check,0,1)

        self.face_check = QtWidgets.QCheckBox("Face Detection")
        vbox_t1.addWidget(self.face_check,0,2)

        self.camera_pic_btn = QtWidgets.QPushButton("Take Picture")
        vbox_t1.addWidget(self.camera_pic_btn,0,3)

        self.camera_vid_btn = QtWidgets.QPushButton("Start Recording")
        vbox_t1.addWidget(self.camera_vid_btn,0,4)

        groupbox2_t1 = QtWidgets.QGroupBox("Live Camera")
        layout_t1.addWidget(groupbox2_t1, 95)

        vbox_t1 = QtWidgets.QVBoxLayout()
        groupbox2_t1.setLayout(vbox_t1)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setStyleSheet("background-color: black; border: 1px solid black;")
        vbox_t1.addWidget(self.image_label)

        # Right Section
        layout2_t1 = QtWidgets.QVBoxLayout()
        frame12_t1.setLayout(layout2_t1)

        groupbox21_t1 = QtWidgets.QGroupBox("Thermal Camera")
        layout2_t1.addWidget(groupbox21_t1,10)

        vbox21_t1 = QtWidgets.QGridLayout()
        groupbox21_t1.setLayout(vbox21_t1)

        self.start_thermal_btn = QtWidgets.QPushButton("Start")
        vbox21_t1.addWidget(self.start_thermal_btn, 0, 0)

        self.thermal_pic_btn = QtWidgets.QPushButton("Take Picture")
        vbox21_t1.addWidget(self.thermal_pic_btn, 0, 3)

        self.thermal_vid_btn = QtWidgets.QPushButton("Start Recording")
        vbox21_t1.addWidget(self.thermal_vid_btn, 0, 4)

        groupbox22_t1 = QtWidgets.QGroupBox("Live Camera")
        layout2_t1.addWidget(groupbox22_t1, 90)

        vbox22_t1 = QtWidgets.QVBoxLayout()
        groupbox22_t1.setLayout(vbox22_t1)

        self.image_label2 = QtWidgets.QLabel()
        self.image_label2.setStyleSheet("background-color: black; border: 1px solid black;")
        vbox22_t1.addWidget(self.image_label2)

        # Frame 21

        layout21_t1 = QtWidgets.QGridLayout()
        frame21_t1.setLayout(layout21_t1)

        groupbox121 = QtWidgets.QGroupBox("Robot Movement")
        layout21_t1.addWidget(groupbox121,0,0)
        vbox121 = QtWidgets.QGridLayout()
        groupbox121.setLayout(vbox121)
        
        self.LED_up_btn = QtWidgets.QPushButton("LED_ON")
        vbox121.addWidget(self.LED_up_btn,0,1)
        
        self.upbutton1 = QtWidgets.QPushButton("FORWARD")
        vbox121.addWidget(self.upbutton1,0,2)
        
        self.stopbutton1 = QtWidgets.QPushButton("STOP")
        self.stopbutton1.setMaximumWidth(100)
        self.stopbutton1.setMaximumHeight(30)
        vbox121.addWidget(self.stopbutton1, 1, 2)

        self.LED_down_btn = QtWidgets.QPushButton("LED_ON")
        vbox121.addWidget(self.LED_down_btn,2,1)
        
        self.downbutton1 = QtWidgets.QPushButton("BACKWARD")
        self.downbutton1.setMaximumWidth(100)
        self.downbutton1.setMaximumHeight(30)
        vbox121.addWidget(self.downbutton1,2,2)

        groupbox1211 = QtWidgets.QGroupBox()
        layout21_t1.addWidget(groupbox1211,1,0)

        layout21_t1.setVerticalSpacing(2)

        vbox1211 = QtWidgets.QGridLayout()
        groupbox1211.setLayout(vbox1211)

        self.homebutton1 = QtWidgets.QPushButton("HOME")
        self.homebutton1.setMaximumHeight(30)
        vbox1211.addWidget(self.homebutton1,0,0)
        vbox1211.setVerticalSpacing(2)
        groupbox1211.setMaximumHeight(50)

        groupbox120 = QtWidgets.QGroupBox("Speed")
        layout21_t1.addWidget(groupbox120, 0, 1)

        vbox120 = QtWidgets.QGridLayout()
        groupbox120.setLayout(vbox120)

        self.PositionSpeed_val = QtWidgets.QLineEdit()
        self.PositionSpeed_val.setPlaceholderText("Position")
        vbox120.addWidget(self.PositionSpeed_val, 0, 0)

        self.HeightSpeed_val = QtWidgets.QLineEdit()
        self.HeightSpeed_val.setPlaceholderText("Height")
        vbox120.addWidget(self.HeightSpeed_val, 1, 0)

        self.AngleSpeed_val = QtWidgets.QLineEdit()
        self.AngleSpeed_val.setPlaceholderText("Angle")
        vbox120.addWidget(self.AngleSpeed_val, 2, 0)

        groupbox12229 = QtWidgets.QGroupBox()
        layout21_t1.addWidget(groupbox12229, 1, 1)
        vbox12229 = QtWidgets.QGridLayout()
        groupbox12229.setLayout(vbox12229)
        self.changeSpeedbutton = QtWidgets.QPushButton("Change")
        self.changeSpeedbutton.setMaximumHeight(30)
        vbox12229.addWidget(self.changeSpeedbutton, 0, 0)

        groupbox122 = QtWidgets.QGroupBox("Camera Movement")
        layout21_t1.addWidget(groupbox122, 0, 2)

        vbox122 = QtWidgets.QGridLayout()
        groupbox122.setLayout(vbox122)

        self.upbutton2 = QtWidgets.QPushButton("UP")
        self.upbutton2.setGeometry(20, 15, 10, 100) 

        vbox122.addWidget(self.upbutton2, 0, 1)

        self.leftbutton2 = QtWidgets.QPushButton("LEFT")
        vbox122.addWidget(self.leftbutton2, 1, 0)
        
        self.stopbutton2 = QtWidgets.QPushButton("STOP")
        vbox122.addWidget(self.stopbutton2, 1, 1)

        self.rightbutton2 = QtWidgets.QPushButton("RIGHT")
        vbox122.addWidget(self.rightbutton2, 1, 2)

        self.downbutton2 = QtWidgets.QPushButton("DOWN")
        vbox122.addWidget(self.downbutton2, 2, 1)

        groupbox1222 = QtWidgets.QGroupBox()
        layout21_t1.addWidget(groupbox1222,1,2)

        vbox1222 = QtWidgets.QGridLayout()
        groupbox1222.setLayout(vbox1222)

        self.homebutton2 = QtWidgets.QPushButton("HOME")
        self.homebutton1.setMaximumHeight(30)
        vbox1222.addWidget(self.homebutton2,0,0)

        # Frame 22

        layout22_t1 = QtWidgets.QGridLayout()
        frame22_t1.setLayout(layout22_t1)
        
        groupbox22_t1 = QtWidgets.QGroupBox("Planing Table")
        layout22_t1.addWidget(groupbox22_t1)

        vbox22_t1 = QtWidgets.QGridLayout()
        vbox22_t1.setVerticalSpacing(2)
        groupbox22_t1.setLayout(vbox22_t1)
        vbox22_t1.setContentsMargins(2, 2, 2, 2)

        AutoArrayRow,c = self.AutoArray.shape
#         print("**",AutoArrayRow)
        
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(AutoArrayRow)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels("Picture;Video;Program;Position;Height;Angle".split(";"))
        
        for i in range(6):
            self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)
        


        for i in range(AutoArrayRow):

            self.table.setItem(i,0, MyTableWidgetItem(str(int(self.AutoArray[i,0])), self.AutoArray[i,0]))
            self.table.setItem(i,1, MyTableWidgetItem(str(int(self.AutoArray[i,1])), self.AutoArray[i,1]))
            self.table.setItem(i,2, MyTableWidgetItem("Program "+str(int(self.AutoArray[i,2])), self.AutoArray[i,2]))
            self.table.setItem(i,3, MyTableWidgetItem(str(self.AutoArray[i,3]), self.AutoArray[i,3]))
            self.table.setItem(i,4, MyTableWidgetItem(str(self.AutoArray[i,4]), self.AutoArray[i,4]))
            self.table.setItem(i,5, MyTableWidgetItem(str(self.AutoArray[i,5]), self.AutoArray[i,5]))

        self.table.sortItems(3,QtCore.Qt.AscendingOrder)
        vbox22_t1.addWidget(self.table,0,0)

        # my_row
        groupbox23_t1 = QtWidgets.QGroupBox()
        vbox22_t1.addWidget(groupbox23_t1,1,0)

        vbox23_t1 = QtWidgets.QGridLayout()
        groupbox23_t1.setLayout(vbox23_t1)

        self.enterPic = QtWidgets.QCheckBox("Picture")
        vbox23_t1.addWidget(self.enterPic, 0, 0)
        self.enterPic.setMinimumHeight(20)
        self.enterPic.setMinimumWidth(140)

        self.enterVid = QtWidgets.QCheckBox("Video")
        vbox23_t1.addWidget(self.enterVid, 0, 1)
        self.enterVid.setMinimumHeight(20)
        self.enterVid.setMinimumWidth(140)

        self.enterProgram = QtWidgets.QComboBox()
        self.enterProgram.addItems(['Program 1', 'Program 2','Program 3', 'Program 4','Program 5', 'Program 6','Program 7', 'Program 8','Program 9'])
        vbox23_t1.addWidget(self.enterProgram,0,2)
        self.enterProgram.setMinimumHeight(20)
        self.enterProgram.setMinimumWidth(140)

        self.enterPosition = QtWidgets.QLineEdit()
        vbox23_t1.addWidget(self.enterPosition,0,3)
        self.enterPosition.setText('')
        self.enterPosition.setPlaceholderText("Position")
        self.enterPosition.setMinimumHeight(20)
        self.enterPosition.setMinimumWidth(140)

        self.enterHeight = QtWidgets.QLineEdit()
        vbox23_t1.addWidget(self.enterHeight,0,4)
        self.enterHeight.setText('')
        self.enterHeight.setPlaceholderText("Height")
        self.enterHeight.setMinimumHeight(20)
        self.enterHeight.setMinimumWidth(140)

        self.enterAngle = QtWidgets.QLineEdit()
        vbox23_t1.addWidget(self.enterAngle,0,5)
        self.enterAngle.setText('')
        self.enterAngle.setPlaceholderText("Angle")
        self.enterAngle.setMinimumHeight(20)
        self.enterAngle.setMinimumWidth(140)

        # my_row_buttons
        self.btn_save = QtWidgets.QPushButton("SAVE")
        vbox23_t1.addWidget(self.btn_save,1,1)
        
        self.btn_go = QtWidgets.QPushButton("GO")
        vbox23_t1.addWidget(self.btn_go,1,2)

        self.btn_copy = QtWidgets.QPushButton("COPY")
        vbox23_t1.addWidget(self.btn_copy,1,3)

        self.btn_add = QtWidgets.QPushButton("ADD")
        vbox23_t1.addWidget(self.btn_add,1,4)

        self.btn_delete = QtWidgets.QPushButton("DELETE")
        vbox23_t1.addWidget(self.btn_delete,1,5)

        # Left 3
        layout31_t1 = QtWidgets.QGridLayout()
        frame31_t1.setLayout(layout31_t1)

        groupbox31_t1 = QtWidgets.QGroupBox("Sensor Data")
        layout31_t1.addWidget(groupbox31_t1,0,0)

        vbox31_t1 = QtWidgets.QGridLayout()
        groupbox31_t1.setLayout(vbox31_t1)

        self.spring_radio = QtWidgets.QRadioButton("Spring")
        vbox31_t1.addWidget(self.spring_radio, 0, 0)
        self.spring_radio.setMinimumHeight(20)

        self.summer_radio = QtWidgets.QRadioButton("Summer")
        vbox31_t1.addWidget(self.summer_radio, 0, 1)
        self.summer_radio.setMinimumHeight(20)

        self.fall_radio = QtWidgets.QRadioButton("Fall")
        vbox31_t1.addWidget(self.fall_radio, 1, 0)
        self.fall_radio.setMinimumHeight(20)

        self.winter_radio = QtWidgets.QRadioButton("Winter")
        vbox31_t1.addWidget(self.winter_radio, 1, 1)
        self.winter_radio.setMinimumHeight(20)

        if self.Season_combo.currentText() == 'Spring':
            self.spring_radio.setChecked(True)
        elif self.Season_combo.currentText() == 'Summer':
            self.summer_radio.setChecked(True)
        elif self.Season_combo.currentText() == 'Fall':
            self.fall_radio.setChecked(True)
        elif self.Season_combo.currentText() == 'Winter':
            self.winter_radio.setChecked(True)

        self.label_32_11 = QtWidgets.QLabel("O2")
        vbox31_t1.addWidget(self.label_32_11, 0, 2)
        self.label_32_11.setMinimumHeight(20)

        self.text_O2 = QtWidgets.QLineEdit()
        self.text_O2.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_O2, 0, 3)
        self.text_O2.setMaximumWidth(30)
        self.text_O2.setMinimumHeight(20)
        self.label_32_11.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 12
        self.label_32_12 = QtWidgets.QLabel("Co2")
        vbox31_t1.addWidget(self.label_32_12, 0, 4)
        self.label_32_12.setMinimumHeight(20)

        self.text_Co2 = QtWidgets.QLineEdit()
        self.text_Co2.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_Co2, 0, 5)
        self.text_Co2.setMaximumWidth(30)
        self.text_O2.setMinimumHeight(20)
        self.label_32_12.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 13
        self.label_32_13 = QtWidgets.QLabel("CH4")
        vbox31_t1.addWidget(self.label_32_13, 0, 6)
        self.label_32_13.setMinimumHeight(20)

        self.text_CH4 = QtWidgets.QLineEdit()
        self.text_CH4.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_CH4, 0, 7)
        self.text_CH4.setMaximumWidth(30)
        self.text_CH4.setMinimumHeight(20)
        self.label_32_13.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # 132
        self.label_32_132 = QtWidgets.QLabel("Voltage")
        vbox31_t1.addWidget(self.label_32_132, 0, 8)
        self.label_32_132.setMinimumHeight(20)

        self.text_BatVolt = QtWidgets.QLineEdit()
        self.text_BatVolt.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_BatVolt, 0, 9)
        self.text_BatVolt.setMaximumWidth(50)
        self.text_BatVolt.setMinimumHeight(20)
        self.label_32_132.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 14
        self.label_32_14 = QtWidgets.QLabel("Humidity")
        vbox31_t1.addWidget(self.label_32_14, 1, 2)
        self.label_32_14.setMinimumHeight(20)

        self.text_Humidity = QtWidgets.QLineEdit()
        self.text_Humidity.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_Humidity, 1, 3)
        self.text_Humidity.setMaximumWidth(30)
        self.text_Humidity.setMinimumHeight(20)
        self.label_32_14.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 15
        self.label_32_15 = QtWidgets.QLabel("Temperature")
        vbox31_t1.addWidget(self.label_32_15, 1, 4)
        self.label_32_15.setMinimumHeight(20)

        self.text_Temperature = QtWidgets.QLineEdit()
        self.text_Temperature.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_Temperature, 1, 5)
        self.text_Temperature.setMaximumWidth(30)
        self.text_Temperature.setMinimumHeight(20)
        self.label_32_15.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 21
        self.label_32_16 = QtWidgets.QLabel("Battery Temp")
        vbox31_t1.addWidget(self.label_32_16, 1, 6)
        self.label_32_16.setMinimumHeight(20)

        self.text_BatTemp = QtWidgets.QLineEdit()
        self.text_BatTemp.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_BatTemp, 1, 7)
        self.text_BatTemp.setMaximumWidth(30)
        self.text_BatTemp.setMinimumHeight(20)
        self.label_32_16.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 21
        self.label_32_162 = QtWidgets.QLabel("Amperage")
        vbox31_t1.addWidget(self.label_32_162, 1, 8)
        self.label_32_162.setMinimumHeight(20)

        self.text_BatAmp = QtWidgets.QLineEdit()
        self.text_BatAmp.setPlaceholderText("0")
        vbox31_t1.addWidget(self.text_BatAmp, 1, 9)
        self.text_BatAmp.setMaximumWidth(50)
        self.text_BatAmp.setMinimumHeight(20)
        self.label_32_162.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # Right 3

        layout32_t1 = QtWidgets.QGridLayout()
        frame32_t1.setLayout(layout32_t1)

        groupbox32_t1 = QtWidgets.QGroupBox("Navigation")
        # size_1
        groupbox32_t1.setMaximumWidth(650)
        groupbox32_t1.setMaximumHeight(200)
        layout32_t1.addWidget(groupbox32_t1, 0, 0)

        vbox32_t1 = QtWidgets.QGridLayout()
        groupbox32_t1.setLayout(vbox32_t1)

        # 11
        self.InputPosition = QtWidgets.QLineEdit()
        vbox32_t1.addWidget(self.InputPosition, 0, 0)
        self.InputPosition.setText('')
        self.InputPosition.setPlaceholderText("Position")
        self.InputPosition.setMinimumHeight(20)

        self.InputHeight = QtWidgets.QLineEdit()
        vbox32_t1.addWidget(self.InputHeight, 0, 1)
        self.InputHeight.setText('')
        self.InputHeight.setPlaceholderText("Height")
        self.InputHeight.setMinimumHeight(20)

        self.InputAngle = QtWidgets.QLineEdit()
        vbox32_t1.addWidget(self.InputAngle, 0, 2)
        self.InputAngle.setText('')
        self.InputAngle.setPlaceholderText("Angle")
        self.InputAngle.setMinimumHeight(20)

        self.btn_copy2 = QtWidgets.QPushButton("COPY")
        vbox32_t1.addWidget(self.btn_copy2, 0, 3)
        self.btn_copy2.setMinimumHeight(20)


        self.Go_label_fake = QtWidgets.QLabel("")
        vbox32_t1.addWidget(self.Go_label_fake, 1, 0)

        self.Go_label = QtWidgets.QLabel("Select Programs:")
        vbox32_t1.addWidget(self.Go_label, 1, 1)
        self.Go_label.setMinimumHeight(20)

        comunes = ['Program 1', 'Program 2', 'Program 3', 'Program 4', 'Program 5', 'Program 6', 'Program 7', 'Program 8', 'Program 9']
        self.combo = CheckableComboBox()
        self.combo.addItems(comunes)
        vbox32_t1.addWidget(self.combo, 1, 2)
        self.combo.setMinimumHeight(20)

        self.btn_Automatic = QtWidgets.QPushButton("AUTO")
        vbox32_t1.addWidget(self.btn_Automatic, 1, 3)
        self.btn_Automatic.setMinimumHeight(20)

        # Create Second tab
        VLayout_t2 = QtWidgets.QVBoxLayout()
        aLayout_t2 = QtWidgets.QHBoxLayout()
        bLayout_t2 = QtWidgets.QHBoxLayout()
        VLayout_t2.addLayout(aLayout_t2,1)
        VLayout_t2.addLayout(bLayout_t2,5)
        self.tab2.setLayout(VLayout_t2)

        v1aLayout_t2 = QtWidgets.QVBoxLayout()
        v2aLayout_t2 = QtWidgets.QVBoxLayout()
        aLayout_t2.addLayout(v1aLayout_t2,1)
        aLayout_t2.addLayout(v2aLayout_t2,9)
        
        # frame top # tab 2
        frame10_t2 = QtWidgets.QFrame()
        frame10_t2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        v1aLayout_t2.addWidget(frame10_t2, 1)

        layout10_t2 = QtWidgets.QGridLayout()
        frame10_t2.setLayout(layout10_t2)
        groupbox10_t2 = QtWidgets.QGroupBox("Seasons")
        layout10_t2.addWidget(groupbox10_t2, 0, 0)
        vbox10_t2 = QtWidgets.QGridLayout()
        groupbox10_t2.setLayout(vbox10_t2)
        frame10_t2.setMaximumWidth(180)
        frame10_t2.setMaximumHeight(100)
        frame10_t2.setContentsMargins(1,1,1,1)
        groupbox10_t2.setContentsMargins(1,1,1,1)

        #11

        self.spring_radio_SET = QtWidgets.QRadioButton("Spring")
        vbox10_t2.addWidget(self.spring_radio_SET, 0, 0)

        self.summer_radio_SET = QtWidgets.QRadioButton("Summer")
        vbox10_t2.addWidget(self.summer_radio_SET, 0, 1)

        self.fall_radio_SET = QtWidgets.QRadioButton("Fall")
        vbox10_t2.addWidget(self.fall_radio_SET, 1, 0)

        self.winter_radio_SET = QtWidgets.QRadioButton("Winter")
        vbox10_t2.addWidget(self.winter_radio_SET, 1, 1)

        frame11_t2=QtWidgets.QFrame()
        frame11_t2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        v2aLayout_t2.addWidget(frame11_t2,1)

        layout11_t2 = QtWidgets.QGridLayout()
        frame11_t2.setLayout(layout11_t2)
        frame11_t2.setMaximumHeight(100)

        groupbox11_t2 = QtWidgets.QGroupBox("Setting")
        # size_2
        layout11_t2.addWidget(groupbox11_t2, 0, 0)

        vbox11_t2 = QtWidgets.QGridLayout()
        groupbox11_t2.setLayout(vbox11_t2)

        # 11
        label_11_1 = QtWidgets.QLabel("O2")
        vbox11_t2.addWidget(label_11_1,0,0)

        self.SETtext_O2 = QtWidgets.QLineEdit()
        # label_21.setFixedSize(640, 100)
        vbox11_t2.addWidget(self.SETtext_O2, 0, 1)
        self.SETtext_O2.setMaximumWidth(60)
        label_11_1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 12
        label_11_2 = QtWidgets.QLabel("Co2")
        vbox11_t2.addWidget(label_11_2, 0, 2)

        self.SETtext_Co2 = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_Co2, 0, 3)
        self.SETtext_Co2.setMaximumWidth(60)
        label_11_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 13
        label_11_3 = QtWidgets.QLabel("CH4")
        vbox11_t2.addWidget(label_11_3, 0, 4)

        self.SETtext_CH4 = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_CH4, 0, 5)
        self.SETtext_CH4.setMaximumWidth(60)
        label_11_3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 14
        label_11_4 = QtWidgets.QLabel("Humidity")
        vbox11_t2.addWidget(label_11_4, 0, 6)

        self.SETtext_Humidity = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_Humidity, 0, 7)
        self.SETtext_Humidity.setMaximumWidth(60)
        label_11_4.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 15
        label_11_5 = QtWidgets.QLabel("Temperature")
        vbox11_t2.addWidget(label_11_5, 0, 8)

        self.SETtext_Temperature = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_Temperature, 0, 9)
        self.SETtext_Temperature.setMaximumWidth(60)
        label_11_5.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # 21
        label_11_6 = QtWidgets.QLabel("Battery")
        vbox11_t2.addWidget(label_11_6, 0, 10)

        self.SETtext_BatTemp = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_BatTemp, 0, 11)
        self.SETtext_BatTemp.setMaximumWidth(60)
        label_11_6.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        
        # 211
        label_11_61 = QtWidgets.QLabel("Amperage")
        vbox11_t2.addWidget(label_11_61, 0, 12)

        self.SETtext_BatAmp = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_BatAmp, 0, 13)
        self.SETtext_BatAmp.setMaximumWidth(60)
        label_11_61.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # 212
        label_11_62 = QtWidgets.QLabel("Voltage")
        vbox11_t2.addWidget(label_11_62, 0, 14)

        self.SETtext_BatVolt = QtWidgets.QLineEdit()
        vbox11_t2.addWidget(self.SETtext_BatVolt, 0, 15)
        self.SETtext_BatVolt.setMaximumWidth(60)
        label_11_62.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # 22

        label_11_7 = QtWidgets.QLabel("   ")
        vbox11_t2.addWidget(label_11_7,0,16)
        label_11_7.setMaximumWidth(5)
        
        self.SETsave = QtWidgets.QPushButton("Save")
        vbox11_t2.addWidget(self.SETsave, 0, 17)

        # frame buttom
        frame21_t2=QtWidgets.QFrame()
        frame21_t2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        bLayout_t2.addWidget(frame21_t2,1)

        # Frame 22
        layout21_t2 = QtWidgets.QGridLayout()
        frame21_t2.setLayout(layout21_t2)

        groupbox21_t2 = QtWidgets.QGroupBox("Report")
        layout21_t2.addWidget(groupbox21_t2)

        vbox21_t2 = QtWidgets.QVBoxLayout()
        groupbox21_t2.setLayout(vbox21_t2)

        self.tableReport = QtWidgets.QTableWidget()
        self.tableReport.setRowCount(0)
        self.tableReport.setColumnCount(15)

        self.tableReport.setHorizontalHeaderLabels(" ID;Alarm;Picture;Video;Program;Position;Height;Angle;Time;O2;Co2;CH4;Humidity;Temperature;Battery".split(";"))

        for i in range(14):
            self.tableReport.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        
        self.tableReport.sortItems(2, QtCore.Qt.AscendingOrder)
        vbox21_t2.addWidget(self.tableReport)

        # my_row
        groupbox22_t2 = QtWidgets.QGroupBox()
        vbox21_t2.addWidget(groupbox22_t2)

        vbox22_t2 = QtWidgets.QGridLayout()
        groupbox22_t2.setLayout(vbox22_t2)

        # my_row_buttons

        self.program_1_check = QtWidgets.QCheckBox("Program 1")
        vbox22_t2.addWidget(self.program_1_check,0,0)

        self.program_2_check = QtWidgets.QCheckBox("Program 2")
        vbox22_t2.addWidget(self.program_2_check,0,1)

        self.program_3_check = QtWidgets.QCheckBox("Program 3")
        vbox22_t2.addWidget(self.program_3_check,0,2)

        self.program_4_check = QtWidgets.QCheckBox("Program 4")
        vbox22_t2.addWidget(self.program_4_check,0,3)

        self.program_5_check = QtWidgets.QCheckBox("Program 5")
        vbox22_t2.addWidget(self.program_5_check,0,4)

        self.program_6_check = QtWidgets.QCheckBox("Program 6")
        vbox22_t2.addWidget(self.program_6_check,0,5)

        self.program_6_check = QtWidgets.QCheckBox("Program 7")
        vbox22_t2.addWidget(self.program_6_check, 0, 6)

        self.program_6_check = QtWidgets.QCheckBox("Program 8")
        vbox22_t2.addWidget(self.program_6_check, 0, 7)

        self.program_6_check = QtWidgets.QCheckBox("Program 9")
        vbox22_t2.addWidget(self.program_6_check, 0, 8)

        self.btn_createReport = QtWidgets.QPushButton("Create Report")
        vbox22_t2.addWidget(self.btn_createReport, 0, 9)

        self.layout.addWidget(self.tabs)
        Form.setLayout(self.layout)

        QtCore.QMetaObject.connectSlotsByName(Form)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Cam view"))
        self.image_label.setText(_translate("Form", "TextLabel"))
        self.control_bt.setText(_translate("Form", "Start"))

    def inputdialog(self):
        self.inputDialog = QtWidgets.QDialog()
        self.inputDialog.setWindowTitle("Introduce Project")
        self.inputDialog.setMinimumWidth(300)
        self.inputDialog.setMinimumHeight(350)
        self.inputDialog.setMaximumHeight(350)

        self.OperatorName_Label = QtWidgets.QLabel("Operator Name", self.inputDialog)
        self.OperatorName_text = QtWidgets.QLineEdit(self.inputDialog)
        self.OperatorName_Label.move(40, 50)
        self.OperatorName_text.move(150, 50)

        self.ProjectName_Label = QtWidgets.QLabel("Project Name", self.inputDialog)
        self.ProjectName_text = QtWidgets.QLineEdit(self.inputDialog)
        self.ProjectName_Label.move(40, 100)
        self.ProjectName_text.move(150, 100)

        self.StartPoint_Label = QtWidgets.QLabel("Starting Point", self.inputDialog)
        self.StartPoint_text = QtWidgets.QLineEdit(self.inputDialog)
        self.StartPoint_Label.move(40, 150)
        self.StartPoint_text.move(150, 150)

        self.FinishPoint_Label = QtWidgets.QLabel("Finishing Point", self.inputDialog)
        self.FinishPoint_text = QtWidgets.QLineEdit(self.inputDialog)
        self.FinishPoint_Label.move(40, 200)
        self.FinishPoint_text.move(150, 200)

        self.Season_Label = QtWidgets.QLabel("Season", self.inputDialog)
        self.Season_combo = QtWidgets.QComboBox(self.inputDialog)
        self.Season_combo.addItems(['Spring','Summer','Fall','Winter'])
        self.Season_Label.move(40, 250)
        self.Season_combo.move(150, 250)

        self.submit_btn = QtWidgets.QPushButton("SUBMIT", self.inputDialog)
        self.submit_btn.move(190, 300)
        self.submit_btn.clicked.connect(self.submit_func)
        self.inputDialog.exec_()

    def errordialog(self):
        self.dialogError = QtWidgets.QDialog()
        Message_Label = QtWidgets.QLabel("Please complete the form", self.dialogError)
        Message_Label.move(20, 20)
        self.error_ok = QtWidgets.QPushButton("OK", self.dialogError)
        self.error_ok.move(100, 50)
        self.dialogError.setWindowTitle("Error")
        self.dialogError.setMinimumWidth(150)
        self.dialogError.setMaximumWidth(200)
        self.dialogError.setMinimumHeight(80)
        self.dialogError.setMaximumHeight(100)
        self.error_ok.clicked.connect(self.close_error)
        self.dialogError.exec_()

    def close_error(self):
        self.dialogError.close()
        self.inputdialog()

    def SETerrordialog(self):
        self.SETdialogError = QtWidgets.QDialog()
        SET_Message_Label = QtWidgets.QLabel("Please select a season", self.SETdialogError)
        SET_Message_Label.move(20, 20)
        self.SET_error_ok = QtWidgets.QPushButton("OK", self.SETdialogError)
        self.SET_error_ok.move(100, 50)
        self.SETdialogError.setWindowTitle("Error")
        self.SETdialogError.setMinimumWidth(150)
        self.SETdialogError.setMaximumWidth(200)
        self.SETdialogError.setMinimumHeight(80)
        self.SETdialogError.setMaximumHeight(100)
        self.SET_error_ok.clicked.connect(self.SET_close_error)
        self.SETdialogError.exec_()

    def SET_close_error(self):
        self.SETdialogError.close()

    def PDFseasonErrordialog(self):
        self.SETdialogError = QtWidgets.QDialog()
        SET_Message_Label = QtWidgets.QLabel("Please select a season in tab 1", self.SETdialogError)
        SET_Message_Label.move(20, 20)
        self.SET_error_ok = QtWidgets.QPushButton("OK", self.SETdialogError)
        self.SET_error_ok.move(100, 50)
        self.SETdialogError.setWindowTitle("Error")
        self.SETdialogError.setMinimumWidth(200)
        self.SETdialogError.setMaximumWidth(240)
        self.SETdialogError.setMinimumHeight(80)
        self.SETdialogError.setMaximumHeight(100)
        self.SET_error_ok.clicked.connect(self.SET_close_error)
        self.SETdialogError.exec_()

    def outputdialog(self):
        self.dialogOutput = QtWidgets.QDialog()
        Message_Label = QtWidgets.QLabel("Report is Ready!", self.dialogOutput)
        Message_Label.move(20, 20)
        self.output_ok = QtWidgets.QPushButton("OK", self.dialogOutput)
        self.output_ok.move(100, 50)
        self.dialogOutput.setWindowTitle("Report")
        self.dialogOutput.setMinimumWidth(200)
        self.dialogOutput.setMaximumWidth(200)
        self.dialogOutput.setMinimumHeight(100)
        self.dialogOutput.setMaximumHeight(120)
        self.output_ok.clicked.connect(self.close_output)
        self.dialogOutput.exec_()
        
    def close_output(self):
        self.dialogOutput.close()

    def submit_func(self):
#         if self.ProjectName_text.text() == '' or self.OperatorName_text.text() == '' or self.StartPoint_text.text() == '' or self.FinishPoint_text.text() == '' or self.Season_combo.currentText() == '':
        if self.ProjectName_text.text() == '' or self.OperatorName_text.text() == '' or self.Season_combo.currentText() == '':
            self.errordialog()
        else:
            self.inputDialog.close()
            current_time_dialog = QtCore.QTime.currentTime()
            self.dialog_start_time = current_time_dialog.toString('hh:mm:ss')

            path1 =  self.upFolder + '/Users/' + self.OperatorName_text.text()
            # path1 = 'Users/'+ self.OperatorName_text.text()
            if os.path.isdir(path1):
                self.old_user = 1
            else:
                pass

            path2 = self.upFolder + '/Users/' + self.OperatorName_text.text() + '/' + self.ProjectName_text.text()
            # path2 = 'Users/' + self.OperatorName_text.text() + '/' + self.ProjectName_text.text()
            if os.path.isdir(path2):
                print('This Project Name Exists')
                self.old_user = 0
                self.inputdialog()
            else:
                src2 = self.upFolder + '/SourceCode/SourceFiles/Sample_Folder/ProjectName'
                distutils.dir_util.copy_tree(src2, path2)
                if self.old_user ==0:
                    src1 = self.upFolder + '/SourceCode/SourceFiles/Sample_Folder/SettingFolder'
                    distutils.dir_util.copy_tree(src1, path1)
                    src11 = self.upFolder + '/SourceCode/SourceFiles/Sample_Folder/AutoFolder'
                    distutils.dir_util.copy_tree(src11, path1)


    def Save_Auto(self):
        print("F1\n",self.AutoArray)
        self.AutoArray = np.zeros((self.table.rowCount(),6))
        for r in range (self.table.rowCount()):
            for c in range(6):
                if c == 2:
                    program = self.table.item(r,c).text()
                    self.AutoArray[r,c] = float(program[8])
                else:
                    self.AutoArray[r,c] = float(self.table.item(r,c).text())
#             print("TT",self.AutoArray)   
        print("F2\n",self.AutoArray)
        np.savetxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Auto/Auto.txt', self.AutoArray,delimiter=',')
    
    def SETfunc(self):
        if self.spring_radio_SET.isChecked() or self.summer_radio_SET.isChecked() or self.fall_radio_SET.isChecked() or self.winter_radio_SET.isChecked():
            if self.spring_radio_SET.isChecked():
                self.SettingArray[:,0] = np.array([int(self.SETtext_O2.text()), int(self.SETtext_Co2.text()),
                                                   int(self.SETtext_CH4.text()), int(self.SETtext_Humidity.text()),
                                                   int(self.SETtext_Temperature.text()), int(self.SETtext_BatTemp.text()),
                                                    int(self.SETtext_BatAmp.text()), int(self.SETtext_BatVolt.text())])

                np.savetxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Setting/setting.txt', self.SettingArray,delimiter=',')
                # np.savetxt('Users/'+self.OperatorName_text.text()+'/Setting/setting.txt', self.SettingArray, delimiter=',')
            elif self.summer_radio_SET.isChecked():
                self.SettingArray[:,1] = np.array([int(self.SETtext_O2.text()), int(self.SETtext_Co2.text()),
                                                   int(self.SETtext_CH4.text()), int(self.SETtext_Humidity.text()),
                                                   int(self.SETtext_Temperature.text()), int(self.SETtext_BatTemp.text()),
                                                   int(self.SETtext_BatAmp.text()), int(self.SETtext_BatVolt.text())])

                np.savetxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Setting/setting.txt', self.SettingArray,delimiter=',')
                # np.savetxt('Users/'+self.OperatorName_text.text()+'/Setting/setting.txt', self.SettingArray, delimiter=',')
            elif self.fall_radio_SET.isChecked():
                self.SettingArray[:,2] = np.array([int(self.SETtext_O2.text()), int(self.SETtext_Co2.text()),
                                                   int(self.SETtext_CH4.text()), int(self.SETtext_Humidity.text()),
                                                   int(self.SETtext_Temperature.text()), int(self.SETtext_BatTemp.text()),
                                                   int(self.SETtext_BatAmp.text()), int(self.SETtext_BatVolt.text())])

                np.savetxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Setting/setting.txt', self.SettingArray,delimiter=',')
                # np.savetxt('Users/'+self.OperatorName_text.text()+'/Setting/setting.txt', self.SettingArray, delimiter=',')
            elif self.winter_radio_SET.isChecked():
                self.SettingArray[:,3] = np.array([int(self.SETtext_O2.text()), int(self.SETtext_Co2.text()),
                                                   int(self.SETtext_CH4.text()), int(self.SETtext_Humidity.text()),
                                                   int(self.SETtext_Temperature.text()), int(self.SETtext_BatTemp.text()),
                                                   int(self.SETtext_BatAmp.text()), int(self.SETtext_BatVolt.text())])

                np.savetxt(self.upFolder +'/Users/' + self.OperatorName_text.text() + '/Setting/setting.txt', self.SettingArray,delimiter=',')
                # np.savetxt('Users/'+self.OperatorName_text.text()+'/Setting/setting.txt', self.SettingArray, delimiter=',')
        else:
            self.SETerrordialog()

    def AlarmFunc(self):
        alarmBell=np.array([0,0,0,0,0,0])
        if self.spring_radio.isChecked():
            
#             print("Setting [O2,CO,CH,Hu,T,TB,Am,Vo]")
#             print(self.SettingArray[0:5,0],self.SettingArray[5,0],self.SettingArray[6,0], self.SettingArray[7,0])
            # O2
            if int(self.text_O2.text()) < int(self.SettingArray[0][0]):
                self.label_32_11.setStyleSheet("background-color: red;")
                alarmBell[0]=1
            elif int(self.text_O2.text()) > int(self.SettingArray[0][0]):
                self.label_32_11.setStyleSheet("")
            # Co2
            if int(self.text_Co2.text()) > int(self.SettingArray[1][0]):
                self.label_32_12.setStyleSheet("background-color: red;")
                alarmBell[1]=1
            elif int(self.text_Co2.text()) < int(self.SettingArray[1][0]):
                self.label_32_12.setStyleSheet("")
            # CH4
            if int(self.text_CH4.text()) > int(self.SettingArray[2][0]):
                self.label_32_13.setStyleSheet("background-color: red;")
                alarmBell[2]=1
            elif int(self.text_CH4.text()) < int(self.SettingArray[2][0]):
                self.label_32_13.setStyleSheet("")
            # Humidity
            if int(self.text_Humidity.text()) > int(self.SettingArray[3][0]):
                self.label_32_14.setStyleSheet("background-color: red;")
                alarmBell[3]=1
            elif int(self.text_Humidity.text()) < int(self.SettingArray[3][0]):
                self.label_32_14.setStyleSheet("")
            # Temperature
            if int(self.text_Temperature.text()) > int(self.SettingArray[4][0]):
                self.label_32_15.setStyleSheet("background-color: red;")
                alarmBell[4]=1
            elif int(self.text_Temperature.text()) < int(self.SettingArray[4][0]):
                self.label_32_15.setStyleSheet("")
            # Battery
            if int(self.text_BatTemp.text()) > int(self.SettingArray[5][0]):
                self.label_32_16.setStyleSheet("background-color: red;")
                alarmBell[5]=1
            elif int(self.text_BatTemp.text()) < int(self.SettingArray[5][0]):
                self.label_32_16.setStyleSheet("")
            # Amp
            if float(self.text_BatAmp.text()) > float(self.SettingArray[6][0]):
                self.label_32_162.setStyleSheet("background-color: green;")
#                 alarmBell[6]=1
            elif float(self.text_BatAmp.text()) > float(self.SettingArray[6][0]):
                self.label_32_162.setStyleSheet("")
            # Volt
            if float(self.text_BatVolt.text()) < float(self.SettingArray[7][0]):
                self.label_32_132.setStyleSheet("background-color: red;")
#                 alarmBell[6]=1
            elif float(self.text_BatVolt.text()) > float(self.SettingArray[7][0]):
                self.label_32_132.setStyleSheet("")
                
            if alarmBell.any():
                self.AlarmaddRow(alarmBell)

        if self.summer_radio.isChecked():
            # O2
            if int(self.text_O2.text()) < int(self.SettingArray[0][1]):
                self.label_32_11.setStyleSheet("background-color: red;")
                alarmBell[0]=1
            elif int(self.text_O2.text()) > int(self.SettingArray[0][1]):
                self.label_32_11.setStyleSheet("")
            # Co2
            if int(self.text_Co2.text()) > int(self.SettingArray[1][1]):
                self.label_32_12.setStyleSheet("background-color: red;")
                alarmBell[1]=1
            elif int(self.text_Co2.text()) < int(self.SettingArray[1][1]):
                self.label_32_12.setStyleSheet("")
            # CH4
            if int(self.text_CH4.text()) > int(self.SettingArray[2][1]):
                self.label_32_13.setStyleSheet("background-color: red;")
                alarmBell[2]=1
            elif int(self.text_CH4.text()) < int(self.SettingArray[2][1]):
                self.label_32_13.setStyleSheet("")
            # Humidity
            if int(self.text_Humidity.text()) > int(self.SettingArray[3][1]):
                self.label_32_14.setStyleSheet("background-color: red;")
                alarmBell[3]=1
            elif int(self.text_Humidity.text()) < int(self.SettingArray[3][1]):
                self.label_32_14.setStyleSheet("")
            # Temperature
            if int(self.text_Temperature.text()) > int(self.SettingArray[4][1]):
                self.label_32_15.setStyleSheet("background-color: red;")
                alarmBell[4]=1
            elif int(self.text_Temperature.text()) < int(self.SettingArray[4][1]):
                self.label_32_15.setStyleSheet("")
            # Battery
            if int(self.text_BatTemp.text()) > int(self.SettingArray[5][1]):
                self.label_32_16.setStyleSheet("background-color: red;")
                alarmBell[5]=1
            elif int(self.text_BatTemp.text()) < int(self.SettingArray[5][1]):
                self.label_32_16.setStyleSheet("")
            # Amp
            if float(self.text_BatAmp.text()) > float(self.SettingArray[6][1]):
                self.label_32_162.setStyleSheet("background-color: green;")
#                 alarmBell[6]=1
            elif float(self.text_BatAmp.text()) > float(self.SettingArray[6][1]):
                self.label_32_162.setStyleSheet("")
            # Volt
            if float(self.text_BatVolt.text()) < float(self.SettingArray[7][1]):
                self.label_32_132.setStyleSheet("background-color: red;")
#                 alarmBell[6]=1
            elif float(self.text_BatVolt.text()) > float(self.SettingArray[7][1]):
                self.label_32_132.setStyleSheet("")
                
            if alarmBell.any():
                self.AlarmaddRow(alarmBell)

        if self.fall_radio.isChecked():
            # O2
            if int(self.text_O2.text()) < int(self.SettingArray[0][2]):
                self.label_32_11.setStyleSheet("background-color: red;")
                alarmBell[0]=1
            elif int(self.text_O2.text()) > int(self.SettingArray[0][2]):
                self.label_32_11.setStyleSheet("")
            # Co2
            if int(self.text_Co2.text()) > int(self.SettingArray[1][2]):
                self.label_32_12.setStyleSheet("background-color: red;")
                alarmBell[1]=1
            elif int(self.text_Co2.text()) < int(self.SettingArray[1][2]):
                self.label_32_12.setStyleSheet("")
            # CH4
            if int(self.text_CH4.text()) > int(self.SettingArray[2][2]):
                self.label_32_13.setStyleSheet("background-color: red;")
                alarmBell[2]=1
            elif int(self.text_CH4.text()) < int(self.SettingArray[2][2]):
                self.label_32_13.setStyleSheet("")
            # Humidity
            if int(self.text_Humidity.text()) > int(self.SettingArray[3][2]):
                self.label_32_14.setStyleSheet("background-color: red;")
                alarmBell[3]=1
            elif int(self.text_Humidity.text()) < int(self.SettingArray[3][2]):
                self.label_32_14.setStyleSheet("")
            # Temperature
            if int(self.text_Temperature.text()) > int(self.SettingArray[4][2]):
                self.label_32_15.setStyleSheet("background-color: red;")
                alarmBell[4]=1
            elif int(self.text_Temperature.text()) < int(self.SettingArray[4][2]):
                self.label_32_15.setStyleSheet("")
            # Battery
            if int(self.text_BatTemp.text()) > int(self.SettingArray[5][2]):
                self.label_32_16.setStyleSheet("background-color: red;")
                alarmBell[5]=1
            elif int(self.text_BatTemp.text()) < int(self.SettingArray[5][2]):
                self.label_32_16.setStyleSheet("")
            # Amp
            if float(self.text_BatAmp.text()) > float(self.SettingArray[6][2]):
                self.label_32_162.setStyleSheet("background-color: green;")
#                 alarmBell[6]=1
            elif float(self.text_BatAmp.text()) > float(self.SettingArray[6][2]):
                self.label_32_162.setStyleSheet("")
            # Volt
            if float(self.text_BatVolt.text()) < float(self.SettingArray[7][2]):
                self.label_32_132.setStyleSheet("background-color: red;")
#                 alarmBell[6]=1
            elif float(self.text_BatVolt.text()) > float(self.SettingArray[7][2]):
                self.label_32_132.setStyleSheet("")
                
            if alarmBell.any():
                self.AlarmaddRow(alarmBell)
            
        if self.winter_radio.isChecked():
            # O2
            if int(self.text_O2.text()) < int(self.SettingArray[0][3]):
                self.label_32_11.setStyleSheet("background-color: red;")
                alarmBell[0]=1
            elif int(self.text_O2.text()) > int(self.SettingArray[0][3]):
                self.label_32_11.setStyleSheet("")
            # Co2
            if int(self.text_Co2.text()) > int(self.SettingArray[1][3]):
                self.label_32_12.setStyleSheet("background-color: red;")
                alarmBell[1]=1
            elif int(self.text_Co2.text()) < int(self.SettingArray[1][3]):
                self.label_32_12.setStyleSheet("")
            # CH4
            if int(self.text_CH4.text()) > int(self.SettingArray[2][3]):
                self.label_32_13.setStyleSheet("background-color: red;")
                alarmBell[2]=1
            elif int(self.text_CH4.text()) < int(self.SettingArray[2][3]):
                self.label_32_13.setStyleSheet("")
            # Humidity
            if int(self.text_Humidity.text()) > int(self.SettingArray[3][3]):
                self.label_32_14.setStyleSheet("background-color: red;")
                alarmBell[3]=1
            elif int(self.text_Humidity.text()) < int(self.SettingArray[3][3]):
                self.label_32_14.setStyleSheet("")
            # Temperature
            if int(self.text_Temperature.text()) > int(self.SettingArray[4][3]):
                self.label_32_15.setStyleSheet("background-color: red;")
                alarmBell[4]=1
            elif int(self.text_Temperature.text()) < int(self.SettingArray[4][3]):
                self.label_32_15.setStyleSheet("")
            # Battery
            if int(self.text_BatTemp.text()) > int(self.SettingArray[5][3]):
                self.label_32_16.setStyleSheet("background-color: red;")
                alarmBell[5]=1
            elif int(self.text_BatTemp.text()) < int(self.SettingArray[5][3]):
                self.label_32_16.setStyleSheet("")
            # Amp
            if float(self.text_BatAmp.text()) > float(self.SettingArray[6][3]):
                self.label_32_162.setStyleSheet("background-color: green;")
#                 alarmBell[6]=1
            elif float(self.text_BatAmp.text()) > float(self.SettingArray[6][3]):
                self.label_32_162.setStyleSheet("")
            # Volt
            if float(self.text_BatVolt.text()) < float(self.SettingArray[7][3]):
                self.label_32_132.setStyleSheet("background-color: red;")
#                 alarmBell[6]=1
            elif float(self.text_BatVolt.text()) > float(self.SettingArray[7][3]):
                self.label_32_132.setStyleSheet("")
                
            if alarmBell.any():
                self.AlarmaddRow(alarmBell)

    def AlarmaddRow(self,alarmBell):

        p = float(self.InputPosition.text())
        h = float(self.InputHeight.text())
        a = float(self.InputAngle.text())
        
        if (p>=self.AlarmPosition+self.AP_range)or(p<=self.AlarmPosition-self.AP_range) or(h>=self.AlarmHeight+self.AH_range)or(h<=self.AlarmHeight-self.AH_range) or(a>=self.AlarmAngle+self.AA_range)or(a<=self.AlarmAngle-self.AA_range):
            alarmcode = str(alarmBell[0])+str(alarmBell[1])+str(alarmBell[2])+str(alarmBell[3])+str(alarmBell[4])+str(alarmBell[5])
            self.AlarmPosition = p
            self.AlarmHeight = h
            self.AlarmAngle = a
            self.AlarmPicSignal = 1
            self.FaceMotionAddRow(alarmcode)

#     def FaceAddRow(self):
#         self.addFlag = 1
#         self.MyId = 2
#         self.table.insertRow(self.table.rowCount())
#         rowCount = self.table.rowCount()
#         self.table.setItem(rowCount - 1, 0, MyTableWidgetItem('1', 1))  #Picture
#         self.table.setItem(rowCount - 1, 1, MyTableWidgetItem('1', 1))  # Video
#         alarmcode = '333333'
#         self.table.setItem(rowCount - 1, 2, MyTableWidgetItem(alarmcode, 1))  # Program
#         self.table.setItem(rowCount - 1, 4,
#                            MyTableWidgetItem(self.InputHeight.text(), float(self.InputHeight.text())))
#         self.table.setItem(rowCount - 1, 5,
#                            MyTableWidgetItem(self.InputAngle.text(), float(self.InputAngle.text())))
#         self.table.setItem(rowCount - 1, 3,
#                                MyTableWidgetItem(self.InputPosition.text(), float(self.InputPosition.text())))

    def Auto_Report(self,array):
        rowCount = self.tableReport.rowCount()
        self.tableReport.insertRow(self.tableReport.rowCount())
        
        self.rowCount1 +=1
        self.ID1 += 1
#         print("Compare",self.ID1,array[0])
        self.tableReport.setItem(rowCount , 0, MyTableWidgetItem(str(self.ID1),self.ID1))

        self.tableReport.setItem(rowCount, 1, MyTableWidgetItem(str(array[1]), array[1]))  # alarm
        self.tableReport.setItem(rowCount, 2, MyTableWidgetItem(str(array[2]), array[2]))  # pic
        self.tableReport.setItem(rowCount, 3, MyTableWidgetItem(str(array[3]), array[3]))  # vid        
        self.tableReport.setItem(rowCount, 4, MyTableWidgetItem(str(array[4]), array[4])) #program
        
        self.tableReport.setItem(rowCount, 5, MyTableWidgetItem(str(array[5]), array[5])) #position
        self.tableReport.setItem(rowCount, 6, MyTableWidgetItem(str(array[6]), array[6])) #height
        self.tableReport.setItem(rowCount, 7, MyTableWidgetItem(str(array[7]), array[7])) #angle
            
        current_time = QtCore.QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.tableReport.setItem(rowCount, 8,  MyTableWidgetItem(label_time, 1))
        self.tableReport.setItem(rowCount, 9,  MyTableWidgetItem(self.text_O2.text(),int(self.text_O2.text())))
        self.tableReport.setItem(rowCount, 10, MyTableWidgetItem(self.text_Co2.text(),int(self.text_Co2.text())))
        self.tableReport.setItem(rowCount, 11, MyTableWidgetItem(self.text_CH4.text(),int(self.text_CH4.text())))
        self.tableReport.setItem(rowCount, 12, MyTableWidgetItem(self.text_Humidity.text(),int(self.text_Humidity.text())))
        self.tableReport.setItem(rowCount, 13, MyTableWidgetItem(self.text_Temperature.text(),int(self.text_Temperature.text())))
        self.tableReport.setItem(rowCount, 14, MyTableWidgetItem(self.text_BatTemp.text(),int(self.text_BatTemp.text())))

        self.tableReport.sortItems(5, QtCore.Qt.AscendingOrder)
        
        

    def FaceMotionAddRow(self,alarmcode):
        rowCount = self.tableReport.rowCount()
        self.tableReport.insertRow(self.tableReport.rowCount())
        self.tableReport.setItem(rowCount, 2, MyTableWidgetItem('1', 1))  # pic
        self.tableReport.setItem(rowCount, 3, MyTableWidgetItem('1',1))  # vid        
        self.tableReport.setItem(rowCount, 1, MyTableWidgetItem('111',111))  # alarm
        self.tableReport.setItem(rowCount, 4, MyTableWidgetItem(str(alarmcode),alarmcode)) #program
        self.tableReport.setItem(rowCount, 6, MyTableWidgetItem(self.InputHeight.text(), float(self.InputHeight.text()))) # Height
        self.tableReport.setItem(rowCount, 7, MyTableWidgetItem(self.InputAngle.text(), float(self.InputAngle.text()))) # Angle
        self.tableReport.setItem(rowCount, 5, MyTableWidgetItem(self.InputPosition.text(), float(self.InputPosition.text()))) # Position
        self.rowCount2 +=1
        self.ID2 += 1
        print("UI_ID2",self.ID2)
        self.tableReport.setItem(rowCount , 0, MyTableWidgetItem(str(self.ID2),self.ID2))
        current_time = QtCore.QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.tableReport.setItem(rowCount, 8,MyTableWidgetItem(label_time, 1))
        self.tableReport.setItem(rowCount, 9, MyTableWidgetItem(self.text_O2.text(),int(self.text_O2.text())))
        self.tableReport.setItem(rowCount, 10, MyTableWidgetItem(self.text_Co2.text(),int(self.text_Co2.text())))
        self.tableReport.setItem(rowCount, 11, MyTableWidgetItem(self.text_CH4.text(),int(self.text_CH4.text())))
        self.tableReport.setItem(rowCount, 12, MyTableWidgetItem(self.text_Humidity.text(),int(self.text_Humidity.text())))
        self.tableReport.setItem(rowCount, 13, MyTableWidgetItem(self.text_Temperature.text(),int(self.text_Temperature.text())))
        self.tableReport.setItem(rowCount, 14, MyTableWidgetItem(self.text_BatTemp.text(),int(self.text_BatTemp.text())))
        self.tableReport.sortItems(5, QtCore.Qt.AscendingOrder)



    def OperatorAddRow(self,alarmcode):
        rowCount = self.tableReport.rowCount()
        self.tableReport.insertRow(self.tableReport.rowCount())
        self.tableReport.setItem(rowCount, 2, MyTableWidgetItem('1', 1))  # pic
        self.tableReport.setItem(rowCount, 3, MyTableWidgetItem('1',1))  # vid        
        self.tableReport.setItem(rowCount, 1, MyTableWidgetItem('111',111))  # alarm
        self.tableReport.setItem(rowCount, 4, MyTableWidgetItem(str(alarmcode),alarmcode)) #program
        self.tableReport.setItem(rowCount, 6, MyTableWidgetItem(self.InputHeight.text(), float(self.InputHeight.text()))) # Height
        self.tableReport.setItem(rowCount, 7, MyTableWidgetItem(self.InputAngle.text(), float(self.InputAngle.text()))) # Angle
        self.tableReport.setItem(rowCount, 5, MyTableWidgetItem(self.InputPosition.text(), float(self.InputPosition.text()))) # Position
        self.rowCount2 +=1
        self.ID3 += 1
        self.tableReport.setItem(rowCount , 0, MyTableWidgetItem(str(self.ID3),self.ID3))
        current_time = QtCore.QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        self.tableReport.setItem(rowCount, 8,MyTableWidgetItem(label_time, 1))
        self.tableReport.setItem(rowCount, 9, MyTableWidgetItem(self.text_O2.text(),int(self.text_O2.text())))
        self.tableReport.setItem(rowCount, 10, MyTableWidgetItem(self.text_Co2.text(),int(self.text_Co2.text())))
        self.tableReport.setItem(rowCount, 11, MyTableWidgetItem(self.text_CH4.text(),int(self.text_CH4.text())))
        self.tableReport.setItem(rowCount, 12, MyTableWidgetItem(self.text_Humidity.text(),int(self.text_Humidity.text())))
        self.tableReport.setItem(rowCount, 13, MyTableWidgetItem(self.text_Temperature.text(),int(self.text_Temperature.text())))
        self.tableReport.setItem(rowCount, 14, MyTableWidgetItem(self.text_BatTemp.text(),int(self.text_BatTemp.text())))
        self.tableReport.sortItems(5, QtCore.Qt.AscendingOrder)


        

    def addRow(self):
        self.addFlag = 1
        self.MyId = 1
        A="0"
        B="0"
        if self.enterPic.isChecked(): A="1"
        if self.enterVid.isChecked(): B="1"
        values = [ A , B , self.enterProgram.currentText(), self.enterPosition.text(), self.enterHeight.text(), self.enterAngle.text()]
        if values[2]!='' and values[3]!='' and values[4]!='' and values[5] != '':
            self.table.insertRow(self.table.rowCount())
            rowCount = self.table.rowCount()
            self.table.setItem(rowCount - 1, 0, MyTableWidgetItem(values[0],int(values[0])))
            self.table.setItem(rowCount - 1, 1, MyTableWidgetItem(values[1], int(values[1])))
            self.table.setItem(rowCount - 1, 2, MyTableWidgetItem(values[2], 1))  # Program
            self.table.setItem(rowCount - 1, 4, MyTableWidgetItem(values[4],float(values[4])))
            self.table.setItem(rowCount - 1, 5, MyTableWidgetItem(values[5],float(values[5])))
            self.table.setItem(rowCount - 1, 3, MyTableWidgetItem(values[3],float(values[3])))
            self.enterPic.setChecked(False)
            self.enterVid.setChecked(False)
            self.enterPosition.clear()
            self.enterHeight.clear()
            self.enterAngle.clear()

    def deleteRow(self):
        self.deleteFlag = 1
        if self.table.rowCount() > 0:
            indexes = self.table.selectionModel().selectedRows()
            for index in sorted(indexes):
                item = self.table.item(index.row(), 0)
                self.editActivated(item)
                item = self.table.item(index.row(), 1)
                self.editActivated(item)
                item = self.table.item(index.row(), 2)
                self.editActivated(item)
                item = self.table.item(index.row(), 4)
                self.editActivated(item)
                item = self.table.item(index.row(), 5)
                self.editActivated(item)
                item = self.table.item(index.row(), 3)
                self.editActivated(item)
                self.table.removeRow(index.row())

    def copyFunc(self):
        self.enterPosition.setText(self.InputPosition.text())
        self.enterHeight.setText(self.InputHeight.text())
        self.enterAngle.setText(self.InputAngle.text())

    def copyRow(self):
        if self.table.rowCount() > 0:

            indexes = self.table.selectionModel().selectedRows()
            for index in sorted(indexes):
                self.enterPic.setChecked(int(self.table.item(index.row(),0).text())==1)
                self.enterVid.setChecked(int(self.table.item(index.row(),1).text()) == 1)
                prog = self.table.item(index.row(), 2).text()
                self.enterProgram.setCurrentIndex(int(prog[8:])-1)
                self.enterPosition.setText(self.table.item(index.row(),3).text())
                self.enterHeight.setText(self.table.item(index.row(),4).text())
                self.enterAngle.setText(self.table.item(index.row(),5).text())

    def editActivated(self,item):
#         row = item.row()
#         col = item.column()
#         self.updateTableReport(row,col,item.text())
        self.table.sortItems(3, QtCore.Qt.AscendingOrder)

#     def updateTableReport(self,row,col,value):
# 
#         if self.addFlag == 1:
#             self.cntAddFlag += 1
#             rowCount = self.tableReport.rowCount()
#             if self.cntAddFlag == 1:
#                 self.tableReport.insertRow(self.tableReport.rowCount())
#                 self.picVal=MyTableWidgetItem(value,int(value)).text()
#                 self.tableReport.setItem(rowCount, 2, MyTableWidgetItem(self.picVal, int(self.picVal)))  # pic
#             elif self.cntAddFlag == 2:
#                 self.vidVal = MyTableWidgetItem(value,int(value)).text()
#                 self.tableReport.setItem(rowCount - 1, 3, MyTableWidgetItem(self.vidVal, int(self.vidVal)))  # pic
#                 if int(self.picVal) == 0 and int(self.vidVal)==0 : var="100"
#                 if int(self.picVal) == 1 and int(self.vidVal) == 0: var = "110"
#                 if int(self.picVal) == 0 and int(self.vidVal) == 1: var = "101"
#                 if int(self.picVal) == 1 and int(self.vidVal) == 1: var = "111"
#                 self.tableReport.setItem(rowCount - 1, 1, MyTableWidgetItem(var,int(var)))  # alarm
#             elif self.cntAddFlag == 3:
#                 self.tableReport.setItem(rowCount - 1, 4, MyTableWidgetItem(value,1)) #program
#             elif self.cntAddFlag == 4:
#                 self.tableReport.setItem(rowCount - 1, 6, MyTableWidgetItem(value,float(value)))
#             elif self.cntAddFlag == 5:
#                 self.tableReport.setItem(rowCount - 1, 7, MyTableWidgetItem(value,float(value)))
#             elif self.cntAddFlag == 6:
#                 self.tableReport.setItem(rowCount - 1, 5, MyTableWidgetItem(value,float(value)))
#                 # add ID and Sensors
#                 if self.MyId == 1:
#                     self.rowCount1 +=1
# #                     self.ID= rowCount + 1000
#                     self.ID1 += 1
#                     self.tableReport.setItem(rowCount - 1, 0, MyTableWidgetItem(str(self.ID1),self.ID1))
#                 elif self.MyId == 2:
#                     self.rowCount2 +=1
# #                     self.ID= rowCount + 2000
#                     self.ID2 += 1
#                     self.tableReport.setItem(rowCount - 1, 0, MyTableWidgetItem(str(self.ID2),self.ID2))
# #                 self.tableReport.setItem(rowCount - 1, 0, MyTableWidgetItem(str(self.ID),self.ID))
# 
#                 current_time = QtCore.QTime.currentTime()
#                 label_time = current_time.toString('hh:mm:ss')
#                 self.tableReport.setItem(rowCount - 1, 8,MyTableWidgetItem(label_time, 1))
#                 self.tableReport.setItem(rowCount - 1, 9, MyTableWidgetItem(self.text_O2.text(),int(self.text_O2.text())))
#                 self.tableReport.setItem(rowCount - 1, 10, MyTableWidgetItem(self.text_Co2.text(),int(self.text_Co2.text())))
#                 self.tableReport.setItem(rowCount - 1, 11, MyTableWidgetItem(self.text_CH4.text(),int(self.text_CH4.text())))
#                 self.tableReport.setItem(rowCount - 1, 12, MyTableWidgetItem(self.text_Humidity.text(),int(self.text_Humidity.text())))
#                 self.tableReport.setItem(rowCount - 1, 13, MyTableWidgetItem(self.text_Temperature.text(),int(self.text_Temperature.text())))
#                 self.tableReport.setItem(rowCount - 1, 14, MyTableWidgetItem(self.text_Battery.text(),int(self.text_Battery.text())))
# 
#                 self.tableReport.sortItems(5, QtCore.Qt.AscendingOrder)
#         elif self.deleteFlag == 1:
#             self.cntDeleteFlag += 1
#             if self.cntDeleteFlag == 4:
#                 self.tableReport.removeRow(row)
#         else:
#             self.tableReport.setItem(row, col+1, MyTableWidgetItem(value,float(value)))
#             self.tableReport.sortItems(2, QtCore.Qt.AscendingOrder)
# 



