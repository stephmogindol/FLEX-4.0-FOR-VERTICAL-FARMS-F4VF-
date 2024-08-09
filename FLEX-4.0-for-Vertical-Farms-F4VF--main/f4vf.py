# F4VF FULL SCRIPT

import sys
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QComboBox, QLabel
from PyQt5.QtWidgets import QDialog, QRadioButton, QPushButton, QVBoxLayout, QHBoxLayout, QPlainTextEdit
from PyQt5.QtGui import QPixmap, QImage
from enum import Enum

MINIMUM_GENERAL_SCORE = 72.6
MINIMUM_SPECIFIC_SCORE = 178.2

class RoomCommand(Enum):
    ADD = 'Add new room'
    EDIT = 'Edit room data'
    REMOVE = 'Remove a room'


def showMessage(msg):
    QMessageBox.question(None, 'Message', msg, QMessageBox.Ok)


class RadioDialog(QDialog):
    def __init__(self, parent=None, title='', label=''):
        super(RadioDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon('images/favicon.ico'))
        self.setFixedSize(400, 200)

        v_layout = QVBoxLayout()

        self.label = QtWidgets.QLabel(label)
        v_layout.addWidget(self.label)

        self.radioButton1 = QRadioButton('1 (worst)')
        self.radioButton1.setChecked(True)
        self.radioButton2 = QRadioButton('2')
        self.radioButton3 = QRadioButton('3')
        self.radioButton4 = QRadioButton('4 (best)')

        self.prev_button = QPushButton('Prev')
        self.next_button = QPushButton('Next')
        self.prev_button.clicked.connect(self.accept)
        self.next_button.clicked.connect(self.reject)

        v_layout.addWidget(self.radioButton1)
        v_layout.addWidget(self.radioButton2)
        v_layout.addWidget(self.radioButton3)
        v_layout.addWidget(self.radioButton4)
        v_layout.addWidget(self.prev_button)
        v_layout.addWidget(self.next_button)

        self.setLayout(v_layout)

    def getSelectedOption(self):
        if self.radioButton1.isChecked():
            return 1
        elif self.radioButton2.isChecked():
            return 2
        elif self.radioButton3.isChecked():
            return 3
        elif self.radioButton4.isChecked():
            return 4
        else:
            return None


class RoomDialog(QDialog):
    def __init__(self, parent=None, title='', room_details={}):
        super(RoomDialog, self).__init__(parent)

        self.setWindowTitle(title)
        self.setWindowIcon(QtGui.QIcon('images/favicon.ico'))
        self.setFixedSize(400, 200)

        self.room_data = room_details
        self.command = title
        self.room_index = None

        main_layout = QVBoxLayout()

        if self.command != RoomCommand.ADD.value:
            room_number_layout = QHBoxLayout()
            self.label = QtWidgets.QLabel('Select Room number:')
            room_number_layout.addWidget(self.label)
            self.room_number_list = QComboBox()
            for room in room_details.keys():
                self.room_number_list.addItem('{}'.format(room))
                room_number_layout.addWidget(self.room_number_list)

            main_layout.addLayout(room_number_layout)
            self.room_number_list.currentIndexChanged.connect(self.room_changed)
        else:
            if len(self.room_data) == 0:
                self.room_index = '1'
            else:
                all_rooms = [int(x) for x in self.room_data.keys()]
                self.room_index = str(max(all_rooms) + 1)
            label = QLabel('Room {}'.format(self.room_index))
            main_layout.addWidget(label)

        width_layout = QHBoxLayout()
        self.width_label = QtWidgets.QLabel('Width  (ft):')
        width_layout.addWidget(self.width_label)
        self.user_width = QPlainTextEdit('0')
        self.user_width.setFixedHeight(25)
        width_layout.addWidget(self.user_width)
        main_layout.addLayout(width_layout)

        length_layout = QHBoxLayout()
        self.length_label = QtWidgets.QLabel('Length (ft):')
        length_layout.addWidget(self.length_label)
        self.user_length = QPlainTextEdit('0')
        self.user_length.setFixedHeight(25)
        length_layout.addWidget(self.user_length)
        main_layout.addLayout(length_layout)

        height_layout = QHBoxLayout()
        self.height_label = QtWidgets.QLabel('Height (ft):')
        height_layout.addWidget(self.height_label)
        self.user_height = QPlainTextEdit('0')
        self.user_height.setFixedHeight(25)
        height_layout.addWidget(self.user_height)
        main_layout.addLayout(height_layout)

        self.cancel_button = QPushButton('Cancel')
        if self.command == RoomCommand.REMOVE.value:
            self.save_button = QPushButton('Remove')
        else:
            self.save_button = QPushButton('Save')
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.process_input)

        main_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.save_button)

        self.setLayout(main_layout)

        if self.command != RoomCommand.ADD.value:
            self.room_changed()

    def process_input(self):
        if self.command == RoomCommand.REMOVE.value:
            del self.room_data[self.room_index]
        else:
            width = self.user_width.toPlainText()
            height = self.user_height.toPlainText()
            length = self.user_length.toPlainText()
            if float(height) < 5:
                showMessage("Height should be greater than 5(ft).")
                return
            self.room_data[self.room_index] = {'width': width, 'height': height, 'length': length}

        self.accept()
    
    def getSelectedOption(self):
        #print(self.room_data)
        return self.room_data
    
    def room_changed(self):
        self.room_index = self.room_number_list.currentText()
        self.user_width.setPlainText(str(self.room_data[self.room_index]['width']))
        self.user_height.setPlainText(str(self.room_data[self.room_index]['height']))
        self.user_length.setPlainText(str(self.room_data[self.room_index]['length']))


class Ui_Dialog(QtWidgets.QWidget):
    assess_score = 0
    assess_type = None
    room_configuration = {}

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setFixedSize(1024, 600)
        Dialog.setWindowIcon(QtGui.QIcon('images/favicon.ico'))
        
        self.logo_frame = QtWidgets.QLabel(Dialog)
        self.logo_frame.setGeometry(QtCore.QRect(0, 0, 130, 130))
        self.logo_frame.setScaledContents(True)
        # self.logo_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.logo_frame.setObjectName("logo_frame")

        logo_image = QImage('images/Binary Logo.png')
        pixmap = QPixmap.fromImage(logo_image)
        self.logo_frame.setPixmap(pixmap)

        self.title_frame = QtWidgets.QLabel(Dialog)
        self.title_frame.setGeometry(QtCore.QRect(130, 0, 702, 130))
        self.title_frame.setStyleSheet("background-color: rgb(0, 0, 0);")
        self.title_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.title_frame.setText("")
        self.title_frame.setObjectName("title_frame")

        self.meta_frame = QtWidgets.QLabel(Dialog)
        self.meta_frame.setGeometry(QtCore.QRect(832, 0, 191, 130))
        self.meta_frame.setScaledContents(True)
        #self.meta_frame.setFrameShape(QtWidgets.QFrame.Box)
        self.meta_frame.setObjectName("meta_frame")

        meta_image = QImage('images/meta.png')
        meta_pixmap = QPixmap.fromImage(meta_image)
        self.meta_frame.setPixmap(meta_pixmap)

        self.title_2 = QtWidgets.QLabel(Dialog)
        self.title_2.setGeometry(QtCore.QRect(230, 60, 491, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.title_2.setFont(font)
        self.title_2.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(0, 0, 0);")
        self.title_2.setAlignment(QtCore.Qt.AlignCenter)
        self.title_2.setObjectName("title_2")

        self.title_1 = QtWidgets.QLabel(Dialog)
        self.title_1.setGeometry(QtCore.QRect(170, 10, 641, 31))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.title_1.setFont(font)
        self.title_1.setStyleSheet("background-color: rgb(0, 0, 0);\n"
"color: rgb(255, 255, 255);")
        self.title_1.setAlignment(QtCore.Qt.AlignCenter)
        self.title_1.setObjectName("title_1")

        self.first_column = QtWidgets.QGroupBox(Dialog)
        self.first_column.setGeometry(QtCore.QRect(0, 130, 421, 470))
        self.first_column.setStyleSheet("background-color: rgb(83, 83, 83);")
        self.first_column.setTitle("")
        self.first_column.setObjectName("first_column")

        # ------------------------------------ Part 1 --------------------------------------------- #
        self.col1_text = QtWidgets.QTextEdit(self.first_column)
        self.col1_text.setGeometry(QtCore.QRect(30, 40, 361, 270))
        self.col1_text.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.col1_text.setReadOnly(True)
        self.col1_text.setObjectName("col1_text")

        self.general_opt_btn = QtWidgets.QPushButton(self.first_column)
        self.general_opt_btn.setGeometry(QtCore.QRect(60, 370, 120, 30))
        font = QtGui.QFont()
        font.setFamily("System")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.general_opt_btn.setFont(font)
        self.general_opt_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.general_opt_btn.setObjectName("general_opt_btn")

        self.specific_opt_btn = QtWidgets.QPushButton(self.first_column)
        self.specific_opt_btn.setGeometry(QtCore.QRect(220, 370, 120, 30))
        font = QtGui.QFont()
        font.setFamily("System")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.specific_opt_btn.setFont(font)
        self.specific_opt_btn.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.specific_opt_btn.setObjectName("specific_opt_btn")

        self.score_label = QtWidgets.QLabel(self.first_column)
        self.score_label.setGeometry(QtCore.QRect(60, 420, 280, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.score_label.setFont(font)
        self.score_label.setStyleSheet("color: rgb(255, 255, 255);")
        self.score_label.setObjectName("score_label")

        # ------------------------------------ Part 2 --------------------------------------------- #
        self.second_column = QtWidgets.QGroupBox(Dialog)
        self.second_column.setGeometry(QtCore.QRect(420, 130, 241, 470))
        self.second_column.setStyleSheet("background-color: rgb(20, 20, 20);")
        self.second_column.setTitle("")
        self.second_column.setObjectName("second_column")

        self.label = QtWidgets.QLabel(self.second_column)
        self.label.setGeometry(QtCore.QRect(16, 40, 211, 31))
        font = QtGui.QFont()
        font.setFamily("System")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")

        self.col2_edit_btn = QtWidgets.QPushButton(self.second_column)
        self.col2_edit_btn.setGeometry(QtCore.QRect(35, 110, 75, 23))
        self.col2_edit_btn.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 75 12pt \"System\";")
        self.col2_edit_btn.setObjectName("col2_edit1_btn")

        self.col2_remove_btn = QtWidgets.QPushButton(self.second_column)
        self.col2_remove_btn.setGeometry(QtCore.QRect(125, 110, 81, 23))
        self.col2_remove_btn.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 75 12pt \"System\";")
        self.col2_remove_btn.setObjectName("col2_remove1_btn")

        self.col2_calculate_btn = QtWidgets.QPushButton(self.second_column)
        self.col2_calculate_btn.setGeometry(QtCore.QRect(105, 420, 121, 23))
        self.col2_calculate_btn.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 75 12pt \"System\";")
        self.col2_calculate_btn.setObjectName("col2_calculate_btn")

        self.col2_add_btn = QtWidgets.QPushButton(self.second_column)
        self.col2_add_btn.setGeometry(QtCore.QRect(16, 420, 75, 23))
        self.col2_add_btn.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"font: 75 12pt \"System\";")
        self.col2_add_btn.setObjectName("col2_add_btn")

        # ------------------------------------ Part 3 --------------------------------------------- #
        self.third_column = QtWidgets.QGroupBox(Dialog)
        self.third_column.setGeometry(QtCore.QRect(660, 130, 360, 640))
        self.third_column.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.third_column.setTitle("")
        self.third_column.setObjectName("third_column")

        self.vf_conf_text = QtWidgets.QPlainTextEdit(self.third_column)
        self.vf_conf_text.setReadOnly(True)
        self.vf_conf_text.setGeometry(QtCore.QRect(18, 20, 330, 400))
        self.vf_conf_text.setStyleSheet("color: rgb(0, 0, 0);\n"
"background-color: rgb(255, 255, 255);\n"
"font: 75 12pt \"System\";")
        self.vf_conf_text.setObjectName("vf_conf_text")

        self.save_btn = QtWidgets.QPushButton(self.third_column)
        self.save_btn.setGeometry(QtCore.QRect(30, 430, 300, 30))
        font = QtGui.QFont()
        font.setFamily("System")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.save_btn.setFont(font)
        self.save_btn.setObjectName("save_btn")

        self.general_opt_btn.released.connect(self.general_assessment)
        self.specific_opt_btn.released.connect(self.specific_assessment)
        self.col2_add_btn.released.connect(self.add_new_room)
        self.col2_edit_btn.released.connect(self.edit_room)
        self.col2_remove_btn.released.connect(self.remove_room)
        self.col2_calculate_btn.released.connect(self.calculate_vf)
        self.save_btn.released.connect(self.save_configuration)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "FLEX 4.0 for VERTICAL FARMS"))
        self.title_2.setText(_translate("Dialog", "FLEX 4.0 for VERTICAL FARMS."))
        self.title_1.setText(_translate("Dialog", "A study on the repurposing of abandoned buildings into urban farms."))
        self.col1_text.setHtml(_translate("Dialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'System\'; font-size:8pt; font-weight:75; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">This is the FLEX 4.0 scoring system.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">The adaptive capacity of your building will be based on the factors of site, structure, skin, facilities, and space plan.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">If your building is asessed to be suitable for repurposement, you may use the VERTICAL FARM CALCULATOR to find out the suitable Vertical Farm configurations for your building.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">You may refer to this link for parameters regarding this assessment --> https://shorturl.at/vgjVd</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">Please choose whether you would like a general or detailed assessment.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt; color:#ffffff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; color:#ffffff;\">For each factor, you may enter a score between 1 (worst) and 4 (best).</span></p></body></html>"))
        self.general_opt_btn.setText(_translate("Dialog", "GENERAL"))
        self.specific_opt_btn.setText(_translate("Dialog", "SPECIFIC"))
        self.score_label.setText(_translate("Dialog", "Score:"))
        self.label.setText(_translate("Dialog", "VERTICAL FARM CALCULATOR"))
        self.col2_edit_btn.setText(_translate("Dialog", "EDIT"))
        self.col2_remove_btn.setText(_translate("Dialog", "REMOVE"))
        self.col2_calculate_btn.setText(_translate("Dialog", "CALCULATE"))
        self.col2_add_btn.setText(_translate("Dialog", "ADD"))
        self.vf_conf_text.setPlainText(_translate("Dialog", "Suggested VF Configurations\n"
""))
        self.save_btn.setText(_translate("Dialog", "SAVE"))

    def general_assessment(self):
        assess_number = 0
        # title, label, weight
        gen_layer_names = [
            ("Currently scoring for Site", 'Expendable site / location', 1),
            ("Currently scoring for Structure", 'Surplus of building space / floor space', 4),
            ("Currently scoring for Structure", 'Surplus of free floor height', 4),
            ("Currently scoring for Structure", 'Access to building', 2),
            ("Currently scoring for Structure", 'Positioning obstacles / columns in load', 3),
            ("Currently scoring for Skin", 'Façade windows to be opened', 1),
            ("Currently scoring for Skin", 'Daylight facilities', 2),
            ("Currently scoring for Facilities", 'Customisability/controllability facilities', 3),
            ("Currently scoring for Facilities", 'Surplus of facilities shafts and ducts', 4),
            ("Currently scoring for Facilities", 'Modularity of facilities', 2),
            ("Currently scoring for Space plan", 'Distinction between support - infill', 4),
            ("Currently scoring for Space plan", 'Horizontal access to building', 3)
        ]
 
        input_value = {}
        while True:
            win_title, win_label, weight = gen_layer_names[assess_number]
            dialog = RadioDialog(title=win_title, label='Enter score for {}'.format(win_label))
            result = dialog.exec_()

            if result == QDialog.Accepted:  # prev
                score = dialog.getSelectedOption()
                res_code = 'PREV'
            else:  # Next
                score = dialog.getSelectedOption()
                res_code = 'NEXT'

            if score < 1 or score > 4:
                showMessage("Score is between 1 and 4 only. Please try again.")
            else:
                input_value[assess_number] = {
                    'score': score,
                    'weight': weight
                }

                if res_code == 'PREV':  # Prev
                    assess_number = max(0, assess_number-1)
                else:
                    assess_number = assess_number + 1
                    if assess_number >= len(gen_layer_names):
                        break
        self.assess_score = sum([x['score'] * x['weight'] for _, x in input_value.items()])
        self.assess_type = 'GENERAL'
        #print(f'{input_value=}')
        self.score_label.setText('Score: {}'.format(self.assess_score))

    def specific_assessment(self):
        assess_number = 0
        # title, label, weight
        gen_layer_names = [
            ("Currently scoring for Site", 'Surplus of site space', 4),
            ("Currently scoring for Site", 'Multifunctional site/location', 3),
            ("Currently scoring for Structure", 'Available floor space of building', 4),
            ("Currently scoring for Structure", 'Size of floor buildings', 3),
            ("Currently scoring for Structure", 'Measurement system; modular coordination', 3),
            ("Currently scoring for Structure", 'Horizontal zone division/layout', 1),
            ("Currently scoring for Structure", 'Presence of stairs/ elevators', 2),
            ("Currently scoring for Structure", 'Extension/reuse of stairs/ elevators', 1),
            ("Currently scoring for Structure", 'Surplus of load bearing capacity', 2),
            ("Currently scoring for Structure", 'Shape of columns', 1),
            ("Currently scoring for Structure", 'Positioning of facilities zones and shafts', 3),
            ("Currently scoring for Structure", 'Fire resistance main bearing construction', 3),
            ("Currently scoring for Structure", 'Extendible building/units horizontal', 2),
            ("Currently scoring for Structure", 'Extendible building/units vertical', 4),
            ("Currently scoring for Structure", 'Rejectable part of building/unit horizontal', 2),
            ("Currently scoring for Structure", 'Insulation between stories and units', 2),
            ("Currently scoring for Skin", 'Dismountable façade', 1),
            ("Currently scoring for Skin", 'Location/ shape daylight facilities', 2),
            ("Currently scoring for Skin", 'Insulation of façade', 1),
            ("Currently scoring for Facilities", 'Measure & control techniques', 4),
            ("Currently scoring for Facilities", 'Surplus capacity of facilities', 4),
            ("Currently scoring for Facilities", 'Distribution facilities', 4),
            ("Currently scoring for Facilities", 'Location sources facilities (heating, cooling)', 3),
            ("Currently scoring for Facilities", 'Disconnection of facility components', 3),
            ("Currently scoring for Facilities", 'Accessibility of facility components', 3),
            ("Currently scoring for Facilities", 'Independence of user units', 1),
            ("Currently scoring for Space plan", 'Multifunctional building', 2),
            ("Currently scoring for Space plan", 'Disconnectible, removable, relocatable units', 1),
            ("Currently scoring for Space plan", 'Disconnectible, removable, relocatable walls', 4),
            ("Currently scoring for Space plan", 'Disconnectible connection detail inner walls', 4),
            ("Currently scoring for Space plan", 'Possibility of suspended ceilings', 2),
            ("Currently scoring for Space plan", 'Possibility of raised floors', 2)
        ]
 
        input_value = {}
        while True:
            win_title, win_label, weight = gen_layer_names[assess_number]
                
            dialog = RadioDialog(title=win_title, label='Enter score for {}'.format(win_label))
            result = dialog.exec_()

            if result == QDialog.Accepted:  # prev
                score = dialog.getSelectedOption()
                res_code = 'PREV'
            else:  # Next
                score = dialog.getSelectedOption()
                res_code = 'NEXT'

            if score < 1 or score > 4:
                showMessage("Score is between 1 and 4 only. Please try again.")
            else:
                input_value[assess_number] = {
                    'score': score,
                    'weight': weight
                }

                if res_code == 'PREV':  # Prev
                    assess_number = max(0, assess_number-1)
                else:
                    assess_number = assess_number + 1
                    if assess_number >= len(gen_layer_names):
                        break
        self.assess_score = sum([x['score'] * x['weight'] for _, x in input_value.items()])
        self.assess_type = 'SPECIFIC'
        #print(f'{input_value=}')
        self.score_label.setText('Score: {}'.format(self.assess_score))

    def add_new_room(self):
        if self.assess_type == 'GENERAL' and self.assess_score < MINIMUM_GENERAL_SCORE:
              showMessage("Assessment should be evaluated to pass minimum score.")
              return
        if self.assess_type == 'SPECIFIC' and self.assess_score < MINIMUM_SPECIFIC_SCORE:
              showMessage("Assessment should be evaluated to pass minimum score.")
              return

        room_dialog = RoomDialog(title=RoomCommand.ADD.value, room_details=self.room_configuration)
        result = room_dialog.exec_()

        if result == QDialog.Accepted:  # save
            self.room_configuration = room_dialog.getSelectedOption()
    
    def edit_room(self):
        if self.assess_type == 'GENERAL' and self.assess_score < MINIMUM_GENERAL_SCORE:
              showMessage("Assessment should be evaluated to pass minimum score.")
              return
        if self.assess_type == 'SPECIFIC' and self.assess_score < MINIMUM_SPECIFIC_SCORE:
              showMessage("Assessment should be evaluated to pass minimum score.")
              return
        if len(self.room_configuration) == 0:
              showMessage("There is no room, you need to add a room first.")
              return

        room_dialog = RoomDialog(title=RoomCommand.EDIT.value, room_details=self.room_configuration)
        result = room_dialog.exec_()

        if result == QDialog.Accepted:  # save
            self.room_configuration = room_dialog.getSelectedOption()

    def remove_room(self):
        if len(self.room_configuration) == 0:
              showMessage("There is no room to be removed.")
              return

        room_dialog = RoomDialog(title=RoomCommand.REMOVE.value, room_details=self.room_configuration)
        result = room_dialog.exec_()

        if result == QDialog.Accepted:  # save
            self.room_configuration = room_dialog.getSelectedOption()

    def calculate_vf(self):
        if len(self.room_configuration) > 0:
            output1_texts = []
            output2_texts = []

            for room_id in self.room_configuration.keys():
                room_data = self.room_configuration[room_id]
                width = float(room_data['width'])
                height = float(room_data['height'])
                length = float(room_data['length'])

                user_area = width * length
                required_area = 0
                unit_price = 1
                power_unit = 1
                cost_unit = 1
                produce_unit = 1
                if 5 <= height < 6:
                    required_area = 32
                    unit_price = 2299
                    power_unit = 63
                    cost_unit = 17.29
                    produce_unit = 4.5
                elif 6 <= height < 7:
                    required_area = 32
                    unit_price = 3099
                    power_unit = 70
                    cost_unit = 21.55
                    produce_unit = 6.5
                elif 7 <= height < 11:
                    required_area = 48
                    unit_price = 4659
                    power_unit = 85
                    cost_unit = 29.2
                    produce_unit = 13
                elif height >= 11:
                    required_area = 160
                    unit_price = 30000
                    power_unit = 798
                    cost_unit = 411.05
                    produce_unit = 87
                
                N = int(user_area / required_area)
                total_unit_purchase_price = N * unit_price
                monthly_power_usage = N * power_unit
                monthly_cost = N * cost_unit
                monthly_product = N * produce_unit

                output1_texts.append('Room {} ......... {}'.format(room_id, N))
                output2_texts.append({
                    'total_unit_purchase_price': total_unit_purchase_price,
                    'monthly_power_usage': monthly_power_usage,
                    'monthly_cost': monthly_cost,
                    'monthly_product': monthly_product
                })
        
            output3_texts = []
            output3_texts.append('Total unit purchase price = RM{}'.format(sum([x['total_unit_purchase_price'] for x in output2_texts])))
            output3_texts.append('Monthly power usage = {}kWh'.format(sum([x['monthly_power_usage'] for x in output2_texts])))
            output3_texts.append('Monthly cost = RM{}'.format(sum([x['monthly_cost'] for x in output2_texts])))
            output3_texts.append('Monthly produce = {}kg'.format(sum([x['monthly_product'] for x in output2_texts])))
            output3_texts.append('\nFor more details regarding this computation, you may refer to --> https://shorturl.at/c0jZ1')

            self.vf_conf_text.setPlainText("Suggested VF Configurations:\n\n{}\n\n{}".format(
                '\n'.join(output1_texts),
                '\n'.join(output3_texts)
            ))
        else:
            showMessage("No room data for calculation.")
    
    def save_configuration(self):
        conf_text = self.vf_conf_text.toPlainText()

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_path:
            if not file_path.endswith('.txt'):
                file_path += '.txt'
            with open(file_path, 'w', encoding='utf-8') as fp:
                fp.write(conf_text + '\n\n')
                fp.write(json.dumps(self.room_configuration, indent=2))


if __name__ == "__main__": 
    app = QtWidgets.QApplication(sys.argv) 
    MainWindow = QtWidgets.QMainWindow() 
    ui = Ui_Dialog() 
    ui.setupUi(MainWindow) 
    MainWindow.show()
 
    sys.exit(app.exec_()) 
