import socket
import pickle
import math

from client import *
import os
import sys

from PyQt6.QtWidgets import QApplication, QPushButton, QComboBox, QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLineEdit, QDialog, QGridLayout, QListWidget, QSizePolicy, QInputDialog, QLCDNumber, QPlainTextEdit, QTextEdit, QScrollArea, QCheckBox, QGroupBox, QMessageBox, QStackedWidget, QSpacerItem, QFrame
from PyQt6.QtCore import Qt, QSize, QLibraryInfo, QCoreApplication, QItemSelection, QItemSelectionModel, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QRegularExpressionValidator
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import cam
import event_broker

# added this class, something to hold the state after you query the database.
class Account():
    def __init__(self, build_info):
        self.win = build_info['win']
        self.display_name = build_info['display_name']
        self.given_name = build_info['given_name']
        self.surname = build_info['surname']
        self.photo_url = build_info['photo_url']
        self.role = build_info['role']
        self.affiliation = build_info['affiliation']
        self.rso = build_info['rso']
        self.created_at = build_info['created_at']
        self.last_updated_at = build_info['last_updated_at']
        self.swiped_in = build_info['swiped_in']
        self.last_access = build_info['last_access']

        # lazy loading
        # load when gui needs
        self.note = ""

class EditAccount(QWidget):
    photo_update = pyqtSignal()
    save_update = pyqtSignal()
    def __init__(self, win, client):
        super().__init__()
        self.client = client
        self.win = win
        self.role_raw = 'populate_later'
        self.setObjectName("Main")

        self.setWindowTitle("Edit Account")

        # Main layout
        main_layout = QHBoxLayout()

        main_widget = QWidget()
        main_form_layout = QFormLayout()
        main_form_layout_widget = QFrame()
        perm_vert_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Delete Layout
        delete_widget = QWidget()
        delete_layout = QVBoxLayout()
        delete_widget.setLayout(delete_layout)

        # Notes layout
        notes_widget = QWidget()
        notes_layout = QVBoxLayout()
        notes_widget.setLayout(notes_layout)

        photo_widget = QWidget()
        photo_layout = QVBoxLayout()
        photo_widget.setLayout(photo_layout)
        
        # The stacked layout of them all
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(main_widget)
        self.stacked_widget.addWidget(delete_widget)
        self.stacked_widget.addWidget(notes_widget)
        self.stacked_widget.addWidget(photo_widget)
        self.stacked_widget.setCurrentIndex(0)

        stacked_layout = QVBoxLayout()
        stacked_layout.addWidget(self.stacked_widget)

        # make the primary layout the stacked one
        self.setLayout(stacked_layout)

        # STUFF FOR MAIN LAYOUT
        self.win_box = QLineEdit()
        self.role = QComboBox()
        self.department = QComboBox()
        self.display_name = QLineEdit()
        self.given_name = QLineEdit()
        self.surname = QLineEdit()
        self.affiliation = QComboBox()
        self.rso = QLineEdit()
        self.permissions = QGroupBox()

        perm_layout = QVBoxLayout()
        perm_label = QLabel()
        perm_label.setText("Permissions")
        perm_label.setStyleSheet("QLabel { font-size:12pt}")

        perm_list = get_permissions_from_db(self.client)
        button_list = []
        for item in perm_list:
            button_list.append(QCheckBox(item.replace("_", " ")))

        for item in button_list:
            perm_layout.addWidget(item)

        self.permissions.setLayout(perm_layout)

        public_notes_button = QPushButton("Public Notes")
        private_notes_button = QPushButton("Private Notes")
        photo_button = QPushButton("Take Photo")
        save_button = QPushButton("Save")
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("QPushButton {background-color: #888888;}")

        # These need to be marked self because other methods hide/show them
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet("QPushButton {background-color: #bc0002; border: 2px solid #220000}")
        save_button.setStyleSheet("QPushButton {background-color: #08C408; border: 2px solid #005500}")
        self.swipe_button = QPushButton("Swipe out")
        self.swipe_button.setStyleSheet("QPushButton {background-color: #35B5AC;}")

        public_notes_button.clicked.connect(self.edit_notes_public)
        private_notes_button.clicked.connect(self.edit_notes_private)
        photo_button.clicked.connect(self.show_photo)
        save_button.clicked.connect(self.save_edit)
        exit_button.clicked.connect(self.close)

        self.delete_button.clicked.connect(self.delete_account)
        self.swipe_button.clicked.connect(self.swipe_toggle)

        main_label = QLabel()
        main_label.setText("Attributes")
        main_label.setStyleSheet("QLabel {font-size:12pt}")
        main_form_layout_sub = QFormLayout()
        main_form_layout_sub.addRow("WIN:", self.win_box)
        main_form_layout_sub.addRow("Role:", self.role)
        main_form_layout_sub.addRow("Display Name:", self.display_name)
        main_form_layout_sub.addRow("Given Name:", self.given_name)
        main_form_layout_sub.addRow("Surname:", self.surname)
        main_form_layout_sub.addRow("Affiliation:", self.affiliation)
        main_form_layout_sub.addRow("Department:", self.department)
        main_form_layout_sub.addRow("RSO:", self.rso)

        main_form_layout_widget.setLayout(main_form_layout_sub)
        main_form_layout_widget.setStyleSheet("QFrame {border: 2px solid #434343;} QLabel {border: none}")
        

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        main_form_layout.addWidget(main_label)
        main_form_layout.addWidget(main_form_layout_widget)
        main_form_layout.addWidget(photo_button)
        main_form_layout.addWidget(public_notes_button)
        main_form_layout.addWidget(private_notes_button)
        main_form_layout.addItem(spacer)
        main_form_layout.addWidget(self.swipe_button)
        main_form_layout.addWidget(self.delete_button)
        main_form_layout.addWidget(save_button)
        main_form_layout.addWidget(exit_button)

        perm_vert_layout.addWidget(perm_label)
        perm_vert_layout.addWidget(self.permissions)
        main_layout.addLayout(main_form_layout)
        main_layout.addLayout(perm_vert_layout)

        # TODO there needs to be some checking here to see who the attendant is. an attendant should not be able to make anyone an Administrator / Attendant
        self.role.addItem("User")
        self.role.addItem("Administrator")
        self.role.addItem("Attendant")
        self.role.addItem("Archived")
        self.role.addItem("Blacklisted")
        self.role.setPlaceholderText('Pending')
        self.role.setCurrentIndex(-1)
        self.role.currentIndexChanged.connect(self.update_raw_role)

        self.department.addItem("cs")
        self.department.addItem("edmms")
        self.department.addItem("cpe")
        self.department.addItem("cce")
        self.department.addItem("ieeem")
        self.department.addItem("mae")
        self.department.addItem("ceas")
        self.department.addItem("pcpp")
        self.department.addItem("other")

        self.affiliation.addItem("Undergrad")
        self.affiliation.addItem("Graduate")
        self.affiliation.addItem("Researcher")
        self.affiliation.addItem("Staff")
        self.affiliation.addItem("Faculty")
        self.affiliation.addItem("Other")
 
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z]+"))
        display_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z_1-9]{20}"))

        self.display_name.setValidator(display_validator)
        self.given_name.setValidator(name_validator)
        self.surname.setValidator(name_validator)
        self.affiliation.setValidator(name_validator)
        self.rso.setValidator(name_validator)

        self.rso.setPlaceholderText("Registered Student Org...")
        self.win_box.setReadOnly(True)

        # STUFF FOR DELETE LAYOUT
        delete_warning = QLabel()
        delete_warning.setText("WARNING: THIS ACTION CANNOT BE REVERSED")

        exit_from_delete = QPushButton()
        exit_from_delete.setText("Back")
        exit_from_delete.setStyleSheet("QPushButton {background-color: #888888;}")

        confirm_delete_button = QPushButton("CONFIRM DELETE")
        confirm_delete_button.setStyleSheet("QPushButton {background-color: #bc0002; border: 2px solid #220000}")
        confirm_delete_button.clicked.connect(self.confirm_delete)

        back_to_main_button = QPushButton("Back")
        back_to_main_button.setStyleSheet("QPushButton {background-color: #888888;}")
        back_to_main_button.clicked.connect(self.back_to_main)

        delete_layout.addWidget(delete_warning)
        delete_layout.addWidget(confirm_delete_button)
        delete_layout.addWidget(exit_from_delete)
        exit_from_delete.clicked.connect(self.back_to_main)

        # STUFF FOR Notes LAYOUT
        self.private_notes = QPlainTextEdit()
        self.public_notes = QPlainTextEdit()
        self.private_notes.setPlainText(get_private_account_note(self.client, self.win))
        self.public_notes.setPlainText(get_public_account_note(self.client, self.win))

        self.save_notes_button_public = QPushButton("Save")
        self.save_notes_button_private = QPushButton("Save")
        self.save_notes_button_public.clicked.connect(self.save_note_public)
        self.save_notes_button_private.clicked.connect(self.save_note_private)
        self.save_notes_button_private.setStyleSheet("QPushButton {background-color: #08C408; border: 2px solid #005500}")
        self.save_notes_button_public.setStyleSheet("QPushButton {background-color: #08C408; border: 2px solid #005500}")

        # Stuff for Picture layout
        bottom_row = QHBoxLayout()
        buttons_block = QVBoxLayout()
        self.feed_label = QLabel("Loading (If this takes more than a few seconds, ensure webcam is plugged in)")
        self.save_message = QLabel(" ")

        self.photo_button = QPushButton("Take Photo")
        self.save_photo_button = QPushButton("Save Photo")
        self.retake_button = QPushButton("Retake")
        self.back_from_photo_button = QPushButton("Back")
        self.back_from_photo_button.setStyleSheet("QPushButton {background-color: #888888;}")

        self.retake_button.hide()
        self.save_photo_button.hide()

        bottom_row.addWidget(self.save_message)
        bottom_row.addLayout(buttons_block)

        photo_layout.addWidget(self.feed_label, alignment= Qt.AlignmentFlag.AlignCenter)
        photo_layout.addLayout(bottom_row)

        buttons_block.addWidget(self.photo_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.retake_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.save_photo_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.back_from_photo_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.photo_button.clicked.connect(self.take_picture)
        self.retake_button.clicked.connect(self.retake_picture)
        self.save_photo_button.clicked.connect(self.save_photo)
        self.back_from_photo_button.clicked.connect(self.back_from_photo)

        self.cam_worker = cam.CamWorker(self.win)
        self.cam_worker.image_update.connect(self.image_update_slot)

        # add widgets to notes_layout
        notes_layout.addWidget(self.private_notes)
        notes_layout.addWidget(self.public_notes)
        notes_layout.addWidget(self.save_notes_button_public)
        notes_layout.addWidget(self.save_notes_button_private)
        notes_layout.addWidget(back_to_main_button)

        # Final setup actions
        self.swiped = False
        self.set_swipe_button_status()
        self.remove_unnecessary_buttons()

        self.initial_load()

    def update_raw_role(self):
        self.role_raw = 'updated'

    def show_photo(self):
        self.stacked_widget.setCurrentIndex(3)
        self.cam_worker.start()

    def image_update_slot(self, image):
        #Update the videofeed with the latest provided frame
        self.feed_label.setPixmap(QPixmap.fromImage(image))

    def take_picture(self):
        self.cam_worker.take_picture()
        #Hides photo button and asks if user wants to retake
        self.photo_button.hide()
        self.save_photo_button.show()
        self.retake_button.show()

    def save_photo(self):
        self.save_message.setText("Photo saved!")
        self.cam_worker.save_photo()
        self.save_photo_button.hide()
        self.retake_button.hide()
        self.photo_button.show()

        update_photo_path(self.client, self.win)

        self.save_update.emit()

    def retake_picture(self):
        self.cam_worker.retake_picture()
        self.retake_button.hide()
        self.save_photo_button.hide()
        self.photo_button.show()
        self.save_message.setText(" ")

    def back_from_photo(self, event):
        self.cam_worker.stop()
        self.stacked_widget.setCurrentIndex(0)

    def back_to_main(self):
        self.stacked_widget.setCurrentIndex(0)

    def confirm_delete(self):
        delete_acc(self.client, self.win)
        
        self.save_update.emit()
        self.close()

    def remove_unnecessary_buttons(self):
        data = get_account_data(self.client, self.win)
        # should only be able to swipe in and out if active role
        if data["role"] == "blacklisted" or data["role"] == "archived" or data["role"] == "pending":
            self.swipe_button.hide()
        else:
            self.swipe_button.show()

        if data["role"] == "blacklisted" or data["role"] == "archived":
            self.delete_button.show()
        else:
            self.delete_button.hide()

    def set_swipe_button_status(self):
        if check_if_swiped_in(self.client, self.win):
            self.swipe_button.setText("Swipe Out")
            self.swipe_button.setStyleSheet("QPushButton {background-color: #35B5AC;}")
            self.swiped = True
        else:
            self.swipe_button.setText("Swipe In")
            self.swipe_button.setStyleSheet("QPushButton {background-color: #89D5D2;}")
            self.swiped = False

    def swipe_toggle(self):
        if check_if_swiped_in(self.client, self.win):
            swipe_out_user(self.client, self.win)
        else:
            swipe_in_user(self.client, self.win)

        self.save_update.emit()
        self.set_swipe_button_status()

    def delete_account(self):
        self.stacked_widget.setCurrentIndex(1)
            
    def initial_load(self):
        acc_data = get_account_data(self.client, self.win)

        self.win_box.setText(str(acc_data['win']))
        self.display_name.setText(acc_data['display_name'])
        self.given_name.setText(acc_data['given_name'])
        self.department.setCurrentText(acc_data['department'])
        self.surname.setText(acc_data['surname'])

        if acc_data['rso'] is not None:
            self.rso.setText(acc_data['rso'])

        permissions = get_account_permissions(self.client, self.win)
        if permissions is not None:
            for item in self.permissions.findChildren(QCheckBox):
                for perm in permissions:
                    if item.text().replace(" ", "_") == perm:
                        item.setChecked(True)

        self.role_raw = acc_data['role']
        self.role.setCurrentText(acc_data['role'].capitalize())
        self.affiliation.setCurrentText(acc_data['affiliation'].capitalize())

    def save_edit(self):
        if self.role_raw == 'pending':
            err_msg = QMessageBox(self)
            err_msg.show()
            err_msg.setText("Role must be changed from pending before saving")
            return

        if self.role.currentText().lower() == "archived" and self.swiped:
            name = self.display_name.text()
            err_msg = QMessageBox(self)
            err_msg.show()
            err_msg.setText(name + " must be swiped out before archiving")
            return

        if self.role.currentText().lower() == "blacklisted" and self.swiped:
            name = self.display_name.text()
            err_msg = QMessageBox(self)
            err_msg.show()
            err_msg.setText(name + " must be swiped out before blacklisting")
            return

        data = {}
        data['win'] = self.win
        data['edit_attrs'] = {}
        
        data['edit_attrs']['display_name'] = self.display_name.text()
        data['edit_attrs']['given_name'] = self.given_name.text()
        data['edit_attrs']['surname'] = self.surname.text()
        data['edit_attrs']['win'] = self.win_box.text()
        data['edit_attrs']['affiliation'] = self.affiliation.currentText().lower()
        data['edit_attrs']['rso'] = self.rso.text()
        data['edit_attrs']['role'] = self.role.currentText().lower()
        data['edit_attrs']['department'] = self.department.currentText().lower()
        data['edit_attrs']['permissions'] = []
        data['edit_attrs']['no_permissions'] = []

        for item in self.permissions.findChildren(QCheckBox):
            if item.isChecked():
                data['edit_attrs']['permissions'].append(item.text().replace(" ", "_"))
            else:
                data['edit_attrs']['no_permissions'].append(item.text().replace(" ", "_"))

        edit_account(self.client, data)
        self.remove_unnecessary_buttons()
        self.save_update.emit()

    def save_note_public(self):
        data = {}
        data['win'] = self.win
        data['type'] = "public"
        data['text'] = self.public_notes.toPlainText()
        edit_note(self.client, data)

        self.save_update.emit()

    def save_note_private(self):
        data = {}
        data['win'] = self.win
        data['type'] = "private"
        data['text'] = self.private_notes.toPlainText()

        edit_note(self.client, data)

        self.save_update.emit()

    def edit_notes_private(self):
        self.stacked_widget.setCurrentIndex(2)
        self.public_notes.hide()
        self.save_notes_button_public.hide()

        self.private_notes.show()
        self.save_notes_button_private.show()

    def edit_notes_public(self):
        self.stacked_widget.setCurrentIndex(2)
        self.private_notes.hide()
        self.save_notes_button_private.hide()

        self.public_notes.show()
        self.save_notes_button_public.show()


    def update_photo(self):
        self.photo_update.emit()

    def update_note(self):
        self.save_update.emit()

class AddAccount(QWidget):
    save_update = pyqtSignal()
    def __init__(self, client):
        super().__init__()
        self.client = client

        self.setWindowTitle("New Account")

        layout = QFormLayout()

        self.win_box = QLineEdit()
        self.role = QComboBox()
        self.department = QComboBox()
        self.display_name = QLineEdit()
        self.given_name = QLineEdit()
        self.surname = QLineEdit()
        self.affiliation = QComboBox()
        self.rso = QLineEdit()
        self.exit_button = QPushButton("Exit")
        self.exit_button.setStyleSheet("QPushButton {background-color: #888888;}")

        create_button = QPushButton("Create Account")
        create_button.setStyleSheet("QPushButton {background-color: #08C408;border: 2px solid #005500}")

        create_button.clicked.connect(self.create_acc)
        self.exit_button.clicked.connect(self.close)

        layout.addRow("WIN:", self.win_box)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Surname:", self.surname)
        layout.addRow("Affiliation:", self.affiliation)
        layout.addRow("Department", self.department)
        layout.addRow("RSO:", self.rso)

        layout.addWidget(create_button)
        layout.addWidget(self.exit_button)

        self.setObjectName("Main")
        self.setLayout(layout)

        win_validator = QRegularExpressionValidator(QRegularExpression("[0-9]{9}"))
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z]+"))

        self.win_box.setPlaceholderText("WIN...")
        self.win_box.setValidator(win_validator)
            
        self.department.addItem("cs")
        self.department.addItem("edmms")
        self.department.addItem("cpe")
        self.department.addItem("cce")
        self.department.addItem("ieeem")
        self.department.addItem("mae")
        self.department.addItem("ceas")
        self.department.addItem("pcpp")
        self.department.addItem("other")
 
        self.display_name.setPlaceholderText("Display Name...")
        self.display_name.setValidator(name_validator)
 
        self.given_name.setPlaceholderText("Given Name...")
        self.given_name.setValidator(name_validator)
 
        self.surname.setPlaceholderText("Surname...")
        self.surname.setValidator(name_validator)

        self.affiliation.addItem("Undergrad")
        self.affiliation.addItem("Graduate")
        self.affiliation.addItem("Researcher")
        self.affiliation.addItem("Staff")
        self.affiliation.addItem("Faculty")
        self.affiliation.addItem("Other")
 
        self.rso.setPlaceholderText("Registered Student Org...")
        self.rso.setValidator(name_validator)

    # TODO add proper error handling
    # TODO ADD CHECK FOR IF WIN IS ALREADY TAKEN
    def create_acc(self):
        if self.win_box.text() == "":
            err_msg = QMessageBox(self)
            err_msg.setText('enter a valid win')
            err_msg.exec()
            return

        if check_if_win_exists(self.client, self.win_box.text()):
            err_msg = QMessageBox(self)
            err_msg.setText('an account with this win already exists')
            err_msg.exec()
            return

        if self.display_name.text() == "":
            err_msg = QMessageBox(self)
            err_msg.setText('a display name is required')
            err_msg.exec()
            return
        if self.given_name.text() == "":
            err_msg = QMessageBox(self)
            err_msg.setText('a given name is required')
            err_msg.exec()
            return
        if self.surname.text() == "":
            err_msg = QMessageBox(self)
            err_msg.setText('a surname is required')
            err_msg.exec()
            return
        data = {}
        data['win'] = self.win_box.text()
        data['edit_attrs'] = {}
        
        data['edit_attrs']['display_name'] = self.display_name.text()
        data['edit_attrs']['given_name'] = self.given_name.text()
        data['edit_attrs']['surname'] = self.surname.text()
        data['edit_attrs']['win'] = self.win_box.text()
        data['edit_attrs']['affiliation'] = self.affiliation.currentText().lower()
        data['edit_attrs']['rso'] = self.rso.text()
        data['edit_attrs']['role'] = "pending"
        data['edit_attrs']['department'] = self.department.currentText().lower()
        data['edit_attrs']['permissions'] = []

        new_account(self.client, data)

        self.second_creation_screen()

        self.save_update.emit()

    def second_creation_screen(self):
        self.w = EditAccount(self.win_box.text(), self.client)
        self.w.show()
        self.w.save_update.connect(self.update)
        self.close()

    def update(self):
        self.save_update.emit()

class QuickView(QWidget):
    save_update = pyqtSignal()
    def __init__(self, win, client):
        super().__init__()
        self.client = client
        self.win = win

        self.setObjectName("Main")

        self.setWindowTitle("Account Information")
        
        combined_layout = QHBoxLayout()
        self.setLayout(combined_layout)

        main_form_layout = QFormLayout()
        main_form_layout_widget = QFrame()

        self.win_box = QLabel()
        self.role = QLabel()
        self.department = QLabel()
        self.display_name = QLabel()
        self.given_name = QLabel()
        self.surname = QLabel()
        self.affiliation = QLabel()
        self.rso = QLabel()

        main_form_layout_sub = QFormLayout()
        main_form_layout_sub.addRow("WIN:", self.win_box)
        main_form_layout_sub.addRow("Role:", self.role)
        main_form_layout_sub.addRow("Display Name:", self.display_name)
        main_form_layout_sub.addRow("Given Name:", self.given_name)
        main_form_layout_sub.addRow("Surname:", self.surname)
        main_form_layout_sub.addRow("Affiliation:", self.affiliation)
        main_form_layout_sub.addRow("Department:", self.department)
        main_form_layout_sub.addRow("RSO:", self.rso)

        main_form_layout_widget.setLayout(main_form_layout_sub)
        main_form_layout_widget.setStyleSheet("QFrame {border: 2px solid #434343;} QLabel {border: none}")

        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("QPushButton {background-color: #888888;}")
        self.swipe_toggle_button = QPushButton("Swipe in")

        exit_button.clicked.connect(self.close)
        self.swipe_toggle_button.clicked.connect(self.swipe_toggle)

        main_label = QLabel()
        main_label.setText("Attributes")
        main_label.setStyleSheet("QLabel {font-size:12pt}")

        # Permissions stuff
        perm_label = QLabel()
        perm_label.setText("Permissions")
        perm_label.setStyleSheet("QLabel {font-size:12pt}")

        perm_vert_layout = QVBoxLayout()
        self.permissions = QGroupBox()
        self.perm_layout = QVBoxLayout()

        perm_list = get_permissions_from_db(self.client)
        button_list = []

        for item in perm_list:
            button_list.append(QCheckBox(item.replace("_", " ")))

        for item in button_list:
            self.perm_layout.addWidget(item)

        self.permissions.setLayout(self.perm_layout)

        perm_vert_layout.addWidget(perm_label)
        perm_vert_layout.addWidget(self.permissions)

        # Notes stuff
        self.notes = QPlainTextEdit()
        self.notes.setReadOnly(True)
        self.notes.setPlainText(get_public_account_note(self.client, self.win))

        self.unlock_button = QPushButton("Unlock Notes")
        self.unlock_button.setStyleSheet("QPushButton {background-color: #89D5D2;}")
        self.unlock_button.clicked.connect(self.toggle_note_lock)

        self.save_public_notes_button = QPushButton("Save notes")
        self.save_public_notes_button.setStyleSheet("QPushButton {background-color: #08C408; border: 2px solid #005500}")
        self.save_public_notes_button.clicked.connect(self.save_public_note)

        notes_layout = QVBoxLayout()
        notes_layout.addWidget(self.notes)
        notes_layout.addWidget(self.save_public_notes_button)
        notes_layout.addWidget(self.unlock_button)

        # Gluing it all together
        main_vert_layout = QVBoxLayout()
        main_vert_layout.addWidget(main_label)
        main_vert_layout.addWidget(main_form_layout_widget)
        main_vert_layout.addLayout(notes_layout)
        main_vert_layout.addWidget(self.swipe_toggle_button)
        main_vert_layout.addWidget(exit_button)

        combined_layout.addLayout(main_vert_layout)
        combined_layout.addLayout(perm_vert_layout)

        self.notes_locked_status = True

        self.set_swipe_button_status()
        self.remove_unnecessary_buttons()

        self.initial_load()

    def remove_unnecessary_buttons(self):
        data = get_account_data(self.client, self.win)
        # should only be able to swipe in and out if active role
        if data["role"] == "blacklisted" or data["role"] == "archived" or data["role"] ==          "pending":
            self.swipe_toggle_button.hide()
        else:
            self.swipe_toggle_button.show()

    def set_swipe_button_status(self):
        if check_if_swiped_in(self.client, self.win):
            self.swipe_toggle_button.setText("Swipe Out")
            self.swipe_toggle_button.setStyleSheet("QPushButton {background-color: #35B5AC;}")
        else:
            self.swipe_toggle_button.setText("Swipe In")
            self.swipe_toggle_button.setStyleSheet("QPushButton {background-color: #89D5D2;}")

    def swipe_toggle(self):
        if check_if_swiped_in(self.client, self.win):
            swipe_out_user(self.client, self.win)
        else:
            swipe_in_user(self.client, self.win)
            
        self.save_update.emit()
        self.set_swipe_button_status()

    def toggle_note_lock(self):
        if self.notes_locked_status == True:
            self.notes_locked_status = False
            self.notes.setReadOnly(False)
            self.unlock_button.setText("Lock Notes")
            self.unlock_button.setStyleSheet("QPushButton {background-color: #35B5AC;}")
        else:
            self.notes_locked_status = True
            self.notes.setReadOnly(True)
            self.unlock_button.setText("Unlock Notes")
            self.unlock_button.setStyleSheet("QPushButton {background-color: #89D5D2;}")

    def initial_load(self):
        acc_data = get_account_data(self.client, self.win)

        self.win_box.setText(str(acc_data['win']))
        self.display_name.setText(acc_data['display_name'])
        self.given_name.setText(acc_data['given_name'])
        self.surname.setText(acc_data['surname'])

        if acc_data['rso'] is not None:
            self.rso.setText(acc_data['rso'])

        permissions = get_account_permissions(self.client, self.win)
        if permissions is not None:
            for item in self.permissions.findChildren(QCheckBox):
                item.setEnabled(False)
                for perm in permissions:
                    print(f'{item.text()} on {perm}')
                    if item.text().replace(" ", "_") == perm:
                        print(f'need to check the state of {perm}')
                        item.setChecked(True)


        self.role.setText(acc_data['role'].capitalize())
        self.department.setText(acc_data['department'])
        self.affiliation.setText(acc_data['affiliation'].capitalize())

    def save_public_note(self):
        data = {}
        data['win'] = self.win
        data['type'] = "public"
        data['text'] = self.notes.toPlainText()

        edit_note(self.client, data)

        self.save_update.emit()

class MainWindow(QMainWindow):
    def __init__(self, client_connection):
        super().__init__()
        self.client_connection = client_connection

        self.items_per_page = 5
        self.page_number = 1
        self.max_page = 0
        self.total_users_in_query = 0
        self.total_users_in_query_search = 0
        self.page_number_search = 1
        self.items_per_page_search = 5
        self.max_page_search = 0

        self.setWindowTitle("Student Projects Lab User Management System")
        self.setMinimumSize(QSize(1280, 720))

        self.main_widget = QStackedWidget()
        self.home_screen = QWidget()
        self.main_widget.setObjectName("Main")

        self.layout_main = QVBoxLayout()
        self.main_widget.addWidget(self.home_screen)
        self.setCentralWidget(self.main_widget)
        self.home_screen.setLayout(self.layout_main)

        # initialize as empty for now
        self.accounts = []

        button_dim=[100, 80]
        button_icon_dim=[50, 50]

        # digit width, dimensions, digit value
        self.headcount_display = self.initialize_lcd(2, [button_dim[0]-30, button_dim[1]-25], 0)

        self.add_button = self.initialize_button("Add Account", "./splums/images/add.jpeg", self.add_account, button_dim, button_icon_dim)
        self.edit_button = self.initialize_button("Edit Account", "./splums/images/modify.jpeg", self.edit_account, button_dim, button_icon_dim)
        self.search_button = self.initialize_button("Search", "./splums/images/search.jpeg", self.search, button_dim, button_icon_dim)
        self.signout_button = self.initialize_button("Sign Out", "./splums/images/signout.jpeg", self.sign_out, button_dim, button_icon_dim)
        self.next_page_button = self.initialize_button("Next Page", "./splums/images/forward.jpeg", self.next_page, button_dim, button_icon_dim)
        self.prev_page_button = self.initialize_button("Previous Page", "./splums/images/back.jpeg", self.prev_page, button_dim, button_icon_dim)

        layout_topsplit = QHBoxLayout()
        self.layout_main.addLayout(layout_topsplit)

        button_bar = QHBoxLayout()
        button_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_bar.addWidget(self.add_button)
        button_bar.addWidget(self.edit_button)
        button_bar.addWidget(self.signout_button)
        button_bar.addWidget(self.search_button)
        layout_topsplit.addLayout(button_bar)

        total_users_layout = QVBoxLayout()
        total_users_lab = QLabel()
        total_users_lab.setText("Total Users")
        self.total_users = QLabel()
        self.total_users.setText(str(self.total_users_in_query))
        total_users_layout.addWidget(self.total_users)
        total_users_layout.addWidget(total_users_lab)

        page_label_layout = QVBoxLayout()
        self.page_label = QLabel()
        page_label_lab = QLabel()
        page_label_lab.setText("Current Page")
        self.page_label.setText(str(self.page_number))
        page_label_layout.addWidget(self.page_label)
        page_label_layout.addWidget(page_label_lab)

        max_page_label_layout = QVBoxLayout()
        max_page_label_lab = QLabel()
        max_page_label_lab.setText("Max Page")
        self.max_page_label = QLabel()
        self.max_page_label.setText(str(self.max_page))
        max_page_label_layout.addWidget(self.max_page_label)
        max_page_label_layout.addWidget(max_page_label_lab)

        select_page_bar = QHBoxLayout()
        select_page_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        select_page_bar.addWidget(self.prev_page_button)
        select_page_bar.addLayout(page_label_layout)
        select_page_bar.addLayout(max_page_label_layout)
        select_page_bar.addLayout(total_users_layout)
        select_page_bar.addWidget(self.next_page_button)
        
        topright_bar = QHBoxLayout()
        topright_bar.setAlignment(Qt.AlignmentFlag.AlignRight)
        headcount_label_and_lcd = QVBoxLayout()
        headcount_header = QLabel(" Headcount")
        headcount_header.setStyleSheet("font-weight: bold;")
        headcount_header.setObjectName("HeadcountHeader")
        headcount_label_and_lcd.addWidget(headcount_header)
        headcount_label_and_lcd.addWidget(self.headcount_display)
        topright_bar.addLayout(headcount_label_and_lcd)
        layout_topsplit.addLayout(topright_bar)

        self.account_table = self.initialize_account_table()
        self.account_table.setUpdatesEnabled(True)

        layout_accounts = QHBoxLayout()
        self.layout_main.addLayout(layout_accounts)
        self.layout_main.addLayout(select_page_bar)

        layout_accounts.addWidget(self.account_table)

        self.accounts_load_swiped()
        self.render_accounts_to_screen()
        self.show()

        self.account_table.selectRow(-1)

        ### SECOND SEARCH LAYOUT
        self.add_button_search = self.initialize_button("Add Account", "./splums/images/add.jpeg", self.   add_account, button_dim, button_icon_dim)
        self.edit_button_search = self.initialize_button("Edit Account", "./splums/images/modify.jpeg", self.edit_account_search, button_dim, button_icon_dim)
        self.signout_button_search = self.initialize_button("Sign Out", "./splums/images/signout.jpeg",    self.sign_out, button_dim, button_icon_dim)


        self.back_button = self.initialize_button("Back", "./splums/images/back.jpeg", self.back_to_main, button_dim, button_icon_dim)

        self.next_page_button_search = self.initialize_button("Next Page", "./splums/images/forward.jpeg",    self.next_page_search, button_dim, button_icon_dim)
        self.prev_page_button_search = self.initialize_button("Previous Page", "./splums/images/back.jpeg", self.prev_page_search, button_dim, button_icon_dim)

        total_users_layout_search = QVBoxLayout()
        total_users_lab_search = QLabel()
        total_users_lab_search.setText("Total Users")
        self.total_users_search = QLabel()
        self.total_users_search.setText(str(self.total_users_in_query_search))
        total_users_layout_search.addWidget(self.total_users_search)
        total_users_layout_search.addWidget(total_users_lab_search)

        page_label_layout_search = QVBoxLayout()
        self.page_label_search = QLabel()
        page_label_lab_search = QLabel()
        page_label_lab_search.setText("Current Page")
        self.page_label_search.setText(str(self.page_number_search))
        page_label_layout_search.addWidget(self.page_label_search)
        page_label_layout_search.addWidget(page_label_lab_search)

        max_page_label_layout_search = QVBoxLayout()
        max_page_label_lab_search = QLabel()
        max_page_label_lab_search.setText("Max Page")
        self.max_page_label_search = QLabel()
        self.max_page_label_search.setText(str(self.max_page_search))
        max_page_label_layout_search.addWidget(self.max_page_label_search)
        max_page_label_layout_search.addWidget(max_page_label_lab_search)

        select_page_bar_search = QHBoxLayout()
        select_page_bar_search.setAlignment(Qt.AlignmentFlag.AlignLeft)
        select_page_bar_search.addWidget(self.prev_page_button_search)
        select_page_bar_search.addLayout(page_label_layout_search)
        select_page_bar_search.addLayout(max_page_label_layout_search)
        select_page_bar_search.addLayout(total_users_layout_search)
        select_page_bar_search.addWidget(self.next_page_button_search)

        self.search_accounts = []

        self.topright_bar_search = QHBoxLayout()
        self.topright_bar_search.setAlignment(Qt.AlignmentFlag.AlignRight)

        search_name_layout = QFormLayout()
        self.search_text = QLineEdit()
        self.search_text.setMaximumWidth(170)
        self.search_text_private = QLineEdit()
        self.search_text_private.setMaximumWidth(170)

        self.search_name = QLineEdit()
        self.search_name.setMaximumWidth(170)
        search_name_layout.addRow("Names/RSO:", self.search_name)
        search_name_layout.addRow("Public notes:", self.search_text)
        search_name_layout.addRow("Private notes:", self.search_text_private)
        search_name_container = QFrame()
        search_name_container.setStyleSheet("QFrame { border: 2px solid #434343; } QLabel{ border: none;}")
        search_name_container.setMaximumWidth(250)
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-za-z0-9_]+"))

        self.search_name.setPlaceholderText("...")
        self.search_text.setPlaceholderText("...")
        self.search_text_private.setPlaceholderText("...")
        self.search_name.setValidator(name_validator)
        
        self.status_search = QComboBox()
        self.status_search.setMaximumWidth(150)
        self.status_search.addItem("Active Accounts")
        self.status_search.addItem(" ↳Swiped in")
        self.status_search.addItem("Pending")
        self.status_search.addItem("Archived")
        self.status_search.addItem("Blacklisted")

        self.status_search.currentIndexChanged.connect(self.update_permbox_style)
        
        reset_button = QPushButton("Reset")
        reset_button.clicked.connect(self.reset_filters)
        reset_button.setStyleSheet("QPushButton {background-color: #FF4500;border: 2px solid #550000}")

        vert_reset_and_filter = QVBoxLayout()
        vert_reset_and_filter.addWidget(reset_button)
        vert_reset_and_filter.addWidget(self.status_search)

        self.privilege_group = QGroupBox()
        self.privilege_group.setMaximumWidth(130)
        self.privilege_layout = QVBoxLayout()
        self.privilege_layout.setSpacing(0)
        privilege_type_list = []
        self.privilege_types = [ "Unprivileged", "Attendant", "Administrator" ] 
        for item in self.privilege_types:
            privilege_type_list.append(QCheckBox(item))

        for item in privilege_type_list:
            self.privilege_layout.addWidget(item)

        self.privilege_group.setLayout(self.privilege_layout)
        self.privilege_group.setStyleSheet("QGroupBox { border: 2px solid #434343; }")

        self.affiliation_group = QGroupBox()
        self.affiliation_group.setMaximumWidth(200)
        self.affiliation_layout_1 = QVBoxLayout()
        self.affiliation_layout_1.setSpacing(0)
        self.affiliation_layout_2 = QVBoxLayout()
        self.affiliation_layout_2.setSpacing(0)
        affiliation_type_list_1 = []
        affiliation_type_list_2 = []
        affiliation_types_1 = [ "Undergrad", "Graduate", "Researcher" ] 
        affiliation_types_2 = [ "Staff", "Faculty", "Other" ] 
        for item in affiliation_types_1:
            affiliation_type_list_1.append(QCheckBox(item))

        for item in affiliation_types_2:
            affiliation_type_list_2.append(QCheckBox(item))

        for item in affiliation_type_list_1:
            self.affiliation_layout_1.addWidget(item)

        for item in affiliation_type_list_2:
            self.affiliation_layout_2.addWidget(item)

        self.combined_affiliation_layout = QHBoxLayout()
        self.combined_affiliation_layout.addLayout(self.affiliation_layout_1)
        self.combined_affiliation_layout.addLayout(self.affiliation_layout_2)

        self.affiliation_group.setLayout(self.combined_affiliation_layout)
        self.affiliation_group.setStyleSheet("QGroupBox { border: 2px solid #434343; }")

        search_name_container.setLayout(search_name_layout)
        self.topright_bar_search.addLayout(vert_reset_and_filter)
        self.topright_bar_search.addWidget(search_name_container)
        self.topright_bar_search.addWidget(self.affiliation_group)
        self.topright_bar_search.addWidget(self.privilege_group)

        self.layout_search = QVBoxLayout()
        layout_topsplit_search = QHBoxLayout()
        self.layout_search.addLayout(layout_topsplit_search)

        button_bar_search = QHBoxLayout()
        button_bar_search.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_bar_search.addWidget(self.add_button_search)
        button_bar_search.addWidget(self.edit_button_search)
        button_bar_search.addWidget(self.signout_button_search)
        button_bar_search.addWidget(self.back_button)
        layout_topsplit_search.addLayout(button_bar_search)
        layout_topsplit_search.addLayout(self.topright_bar_search)

        self.search_widget = QWidget()
        self.search_widget.setLayout(self.layout_search)

        self.account_table_search = self.initialize_account_table()
        self.account_table_search.setUpdatesEnabled(True)
        self.account_table_search.selectRow(-1)

        self.layout_accounts_search = QHBoxLayout()
        self.layout_accounts_search.addWidget(self.account_table_search)
        self.layout_search.addLayout(self.layout_accounts_search)
        self.layout_search.addLayout(select_page_bar_search)

        self.main_widget.addWidget(self.search_widget)

        for item in self.privilege_group.findChildren(QCheckBox):
            item.stateChanged.connect(self.search)
            item.setChecked(True)

        for item in self.affiliation_group.findChildren(QCheckBox):
            item.stateChanged.connect(self.search)
            item.setChecked(True)

        self.status_search.currentIndexChanged.connect(self.search)
        self.search_name.textChanged.connect(self.search)
        self.search_text.textChanged.connect(self.search)
        self.search_text_private.textChanged.connect(self.search)

        self.account_table.doubleClicked.connect(self.attendant_blurb_swiped)
        self.account_table_search.doubleClicked.connect(self.attendant_blurb_search)

        self.main_widget.setCurrentIndex(0)

    def make_icon(self, path):
        new_label = QLabel()
        pixmap = QPixmap(path)
        new_label.setPixmap(pixmap)
        return new_label
        
    def update_permbox_style(self):
        current_text = self.status_search.currentText()
        gray_outs = ["Pending", "Archived", "Blacklisted"]

        if current_text in gray_outs:
            for box in self.privilege_group.findChildren(QCheckBox):
                box.setText("N/A")
                box.setChecked(False)
                box.setEnabled(False)
        else:
            i = 0
            for box in self.privilege_group.findChildren(QCheckBox):
                box.setText(self.privilege_types[i])
                box.setChecked(True)
                box.setEnabled(True)
                i += 1

    def reset_filters(self):
        self.search_name.setText("")
        self.search_text.setText("")
        self.search_text_private.setText("")
        self.status_search.setCurrentIndex(0)
        for box in self.affiliation_group.findChildren(QCheckBox):
            box.setChecked(True)

        for box in self.privilege_group.findChildren(QCheckBox):
            box.setChecked(True)

    def attendant_blurb_swiped(self):
        selected_row = self.account_table.currentRow()

        if selected_row == -1:
            err_msg = QMessageBox(self)
            err_msg.setText('click to select the account you want to view')
            err_msg.exec()
            return

        self.w = QuickView(self.accounts[selected_row].win, self.client_connection)
        self.w.show()

        self.w.save_update.connect(self.update_save)

    def attendant_blurb_search(self):
        selected_row = self.account_table_search.currentRow()

        if selected_row == -1:
            err_msg = QMessageBox(self)
            err_msg.setText('click to select the account you want to view')
            err_msg.exec()
            return

        self.w = QuickView(self.search_accounts[selected_row].win, self.client_connection)
        self.w.show()

        # connect signal to pressing the save button 
        self.w.save_update.connect(self.update_save)

    def search(self):
        self.search_accounts.clear()
        # jump back to the first page
        self.page_number_search = 1
        self.page_label_search.setText(str(self.page_number_search))
        self.main_widget.setCurrentIndex(1)
        self.accounts_load_search()
        self.render_accounts_to_screen_search()

    def back_to_main(self):
        self.main_widget.setCurrentIndex(0)

    def prev_page_search(self):
        if self.page_number_search > 1:
            self.page_number_search -= 1
            self.page_label_search.setText(str(self.page_number_search))

        self.search_accounts.clear()
        self.accounts_load_search()
        self.render_accounts_to_screen_search()

    def prev_page(self):
        if self.page_number > 1:
            self.page_number -= 1
            self.page_label.setText(str(self.page_number))

        self.accounts.clear()
        self.accounts_load_swiped()
        self.render_accounts_to_screen()

    def next_page_search(self):
        if self.items_per_page_search * self.page_number_search < self.total_users_in_query_search:
            self.page_number_search += 1
            self.page_label_search.setText(str(self.page_number_search))

        self.search_accounts.clear()
        self.accounts_load_search()
        self.render_accounts_to_screen_search()

    def next_page(self):
        if self.items_per_page * self.page_number < self.total_users_in_query:
            self.page_number += 1
            self.page_label.setText(str(self.page_number))

        self.accounts.clear()
        self.accounts_load_swiped()
        self.render_accounts_to_screen()
    # sends the win of the account that you want to edit to the widget as well as the client
    # connection. from there it grabs and edits the data how it wants.
    def edit_account(self):
        selected_row = self.account_table.currentRow()

        if selected_row == -1:
            err_msg = QMessageBox(self)
            err_msg.setText('click to select the account you want to edit')
            err_msg.exec()
            return

        self.w = EditAccount(self.accounts[selected_row].win, self.client_connection)
        self.w.show()

        # connect signal to pressing the save button 
        self.w.photo_update.connect(self.update_photos)
        self.w.save_update.connect(self.update_save)

    def edit_account_search(self):
        selected_row = self.account_table_search.currentRow()

        if selected_row == -1:
            err_msg = QMessageBox(self)
            err_msg.setText('click to select the account you want to edit')
            err_msg.exec()
            return

        self.w = EditAccount(self.search_accounts[selected_row].win, self.client_connection)
        self.w.show()

        # connect signal to pressing the save button 
        self.w.photo_update.connect(self.update_photos)
        self.w.save_update.connect(self.update_save)

    def update_save(self):
        self.accounts.clear()
        self.accounts_load_swiped()
        self.render_accounts_to_screen()

        self.search_accounts.clear()
        self.accounts_load_search()
        self.render_accounts_to_screen_search()

    def update_photos(self):
        row = 0
        # for each acc loaded into the gui
        for acc in self.accounts:
            account_photo = QLabel()
            account_photo.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))

            self.account_table.setCellWidget(row, 0, account_photo)
            row += 1

        row = 0
        for acc in self.search_accounts:
            account_photo = QLabel()
            account_photo.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))

            self.account_table_search.setCellWidget(row, 0, account_photo)
            row += 1

    def add_account(self):
        self.w = AddAccount(self.client_connection)
        self.w.show()

        self.w.save_update.connect(self.update_save)

    def sign_out(self):
        print("Signing out")

    def initialize_button(self, title, icon_path, function, button_dim, button_icon_dim):
        new_button = QToolButton(self)
        new_button.setText(title)
        new_button.setIcon(QIcon(icon_path))
        new_button.clicked.connect(function)
        new_button.setFixedSize(QSize(button_dim[0], button_dim[1]))
        new_button.setIconSize(QSize(button_icon_dim[0], button_icon_dim[1]))
        new_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        return new_button

    def initialize_lcd(self, digit_count, button_dim, digit):
        new_lcd = QLCDNumber(self)
        new_lcd.setDigitCount(digit_count)
        new_lcd.setFixedSize(QSize(button_dim[0], button_dim[1]))
        new_lcd.display(digit)
        return new_lcd

    def initialize_account_table(self):
        new_account_table = QTableWidget()
        new_account_table.verticalHeader().setVisible(False)

        new_account_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        new_account_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        new_account_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        new_account_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        new_account_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode(0))

        new_account_table.setColumnCount(5)

        new_account_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        new_account_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        new_account_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        column_labels = ["Photo", "Status", "Account", "Permissions", "Notes"]
        new_account_table.setHorizontalHeaderLabels(column_labels)
        new_account_table.setColumnWidth(1, 55)
        new_account_table.setColumnWidth(2, 350)

        return new_account_table

    def render_accounts_to_screen_search(self):
        self.account_table_search.setRowCount(len(self.search_accounts))

        row = 0
        # for each acc loaded into the gui
        for acc in self.search_accounts:
            # Account Image
            account_photo = QLabel()
            account_photo.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))

            self.account_table_search.setCellWidget(row, 0, None)
            self.account_table_search.setCellWidget(row, 0, account_photo)

            # Account Name
            account_name_cell = QTableWidgetItem(acc.display_name)
            account_name_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table_search.setItem(row, 2, account_name_cell)

            icon_widget = QWidget()
            icon_list = QVBoxLayout()

            icon_list.addWidget(self.make_icon('./splums/images/icons/' + acc.affiliation + '.jpg'))

            icon_list.addWidget(self.make_icon('./splums/images/icons/' + acc.role + '.jpg'))


            # add the swiped status
            if acc.swiped_in:
                icon_list.addWidget(self.make_icon('./splums/images/icons/swiped_in.jpg'))
            else:
                icon_list.addWidget(self.make_icon('./splums/images/icons/swiped_out.jpg'))

            icon_list.setContentsMargins(12, 2, 12, 2)
            icon_list.setSpacing(0)
            icon_widget.setLayout(icon_list)

            self.account_table_search.setCellWidget(row, 1, icon_widget)
            
            perms = get_account_permissions(self.client_connection, acc.win)


            if perms is not None:
                perms = sorted(perms)
                for i in range(len(perms)):
                    perms[i] = perms[i].replace('(', '')
                    perms[i] = perms[i].replace(')', '')
                    perms[i] = perms[i].replace(',', '')

                icon_grid = QGridLayout()
                perm_widget = QWidget()
                i = 0
                for icon_row in range(3):
                    for col in range(7):
                        if i > len(perms) - 1:
                            break
                        icon = self.make_icon('./splums/images/icons/perms/' + perms[i] + '.jpg')
                        icon_grid.addWidget(icon, icon_row, col)
                        i += 1

                icon_grid.setHorizontalSpacing(20)
                icon_grid.setContentsMargins(20,2,20,2)
                icon_grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
                perm_widget.setLayout(icon_grid)

                self.account_table_search.setCellWidget(row, 3, perm_widget)

            
            note_text_cell = QTextEdit(acc.note)
            note_text_cell.setReadOnly(True)
            note_text_cell.setStyleSheet("font-size: 12pt;")
            note_text_cell.setFixedHeight(100)
            note_text_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.account_table_search.setCellWidget(row, 4, note_text_cell)

            row += 1

        # Resize rows and first column to fit images
        self.account_table_search.resizeRowsToContents()
        self.account_table_search.resizeColumnToContents(0)
        

    def render_accounts_to_screen(self):
        self.account_table.setRowCount(len(self.accounts))
        self.headcount_display.display(len(self.accounts))

        row = 0
        # for each acc loaded into the gui
        for acc in self.accounts:
            # Account Image
            account_photo = QLabel()
            account_photo.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))

            self.account_table.setCellWidget(row, 0, None)
            self.account_table.setCellWidget(row, 0, account_photo)

            # Account Name
            account_name_cell = QTableWidgetItem(acc.display_name)
            account_name_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table.setItem(row, 2, account_name_cell)

            icon_widget = QWidget()
            icon_list = QVBoxLayout()
            icon_list.addWidget(self.make_icon('./splums/images/icons/graduate.jpg'))
            icon_list.addWidget(self.make_icon('./splums/images/icons/user.jpg'))
            if acc.swiped_in:
                icon_list.addWidget(self.make_icon('./splums/images/icons/swiped_in.jpg'))
            else:
                icon_list.addWidget(self.make_icon('./splums/images/icons/swiped_out.jpg'))

            icon_list.setContentsMargins(12, 2, 12, 2)
            icon_list.setSpacing(0)
            icon_widget.setLayout(icon_list)
            self.account_table.setCellWidget(row, 1, icon_widget)


            perms = get_account_permissions(self.client_connection, acc.win)

            perms = sorted(perms)

            if perms is not None:
                for i in range(len(perms)):
                    perms[i] = perms[i].replace('(', '')
                    perms[i] = perms[i].replace(')', '')
                    perms[i] = perms[i].replace(',', '')

                icon_grid = QGridLayout()
                perm_widget = QWidget()
                i = 0
                for icon_row in range(3):
                    for col in range(7):
                        if i > len(perms) - 1:
                            break
                        icon = self.make_icon('./splums/images/icons/perms/' + perms[i] + '.jpg')
                        icon_grid.addWidget(icon, icon_row, col)
                        i += 1

                icon_grid.setHorizontalSpacing(20)
                icon_grid.setContentsMargins(20,2,20,2)
                icon_grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
                perm_widget.setLayout(icon_grid)

                self.account_table.setCellWidget(row, 3, perm_widget)

            # horizontal row of buttons for each note this is the layout for the actual notewidget
            note_text_cell = QTextEdit(acc.note)
            note_text_cell.setReadOnly(True)
            note_text_cell.setStyleSheet("font-size: 12pt;")
            note_text_cell.setFixedHeight(100)
            note_text_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.account_table.setCellWidget(row, 4, note_text_cell)

            row += 1

        # Resize rows and first column to fit images
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnToContents(0)

    def accounts_load_search(self):
        event_data = {"page_number": self.page_number_search, 
                      "items_per_page": self.items_per_page_search,
                      "swiped_users": False,
                     }

        event_data['privilege'] = []
        for item in self.privilege_group.findChildren(QCheckBox):
            if item.isChecked() is False:
                if item.text() == "N/A": 
                    continue
                # just done use User in code
                if item.text() == "Unprivileged":
                    event_data['privilege'].append("user")
                else:
                    event_data['privilege'].append(item.text().lower())

        event_data['affiliation'] = []
        for item in self.affiliation_group.findChildren(QCheckBox):
            print(f"CHECKING affiliation {item.text()}")
            if item.isChecked() is False:
                # just done use User in code
                event_data['affiliation'].append(item.text().lower())

        event_data['status'] = self.status_search.currentText().lower().replace(" ", "_")
        if event_data['status'] ==  '_↳swiped_in':
            event_data['status'] = 'swiped_in'

        if event_data['status'] != "blacklisted":
            event_data['privilege'].append("blacklisted")
        if event_data['status'] != "archived":
            event_data['privilege'].append("archived")

        event_data['name'] = self.search_name.text()
        event_data['text'] = self.search_text.text()
        event_data['text_private'] = self.search_text_private.text()

        res = get_users_paginated_filtered(self.client_connection, event_data)
        if res is None:
            return

        self.total_users_in_query_search = res["total_users"]
        self.total_users_search.setText(str(self.total_users_in_query_search))
        self.max_page_label_search.setText(str(math.ceil(self.total_users_in_query_search / self.items_per_page_search)))
        print("AFTER GET USERS CALL")
        for c in res["users"]:
            print(c)
            self.search_accounts.append(Account(c))

        # load notes for each account
        for acc in self.search_accounts:
            res = get_public_account_note(self.client_connection, acc.win)
            print(f"res: {res}")
            acc.note = res

    def accounts_load_swiped(self):
        event_data = {"page_number": self.page_number, "items_per_page": self.items_per_page}
                      
        event_data['privilege'] = "ignore"
        event_data['status'] = "swiped_in"
        event_data['affiliation'] = "ignore"
        event_data['name'] = "ignore"
        event_data['text'] = "ignore"
        event_data['text_private'] = "ignore"

        res = get_users_paginated_filtered(self.client_connection, event_data)
        self.total_users_in_query = res["total_users"]
        self.total_users.setText(str(self.total_users_in_query))
        self.max_page_label.setText(str(math.ceil(self.total_users_in_query / self.items_per_page)))
        for c in res["users"]:
            print(c)
            self.accounts.append(Account(c))

        # load notes for each account
        for acc in self.accounts:
            res = get_public_account_note(self.client_connection, acc.win)
            print(f"res: {res}")
            acc.note = res


def edit_account(client, edit_data):
    event = Event(EventTypes.EDIT_ACCOUNT, edit_data)

    res = client.call_server(event)

def new_account(client, edit_data):
    event = Event(EventTypes.CREATE_ACCOUNT, edit_data)

    res = client.call_server(event)

def edit_note(client, edit_data):
    event = Event(EventTypes.EDIT_NOTE_FOR_USER, edit_data)

    res = client.call_server(event)

def get_users_paginated_filtered(client, event_data):
    event = Event(EventTypes.GET_USERS_PAGINATED_FILTERED, event_data)

    res = client.call_server(event)

    return res

def check_if_win_exists(client, account_win):
    event_data = {}
    event_data['win'] = account_win
    event = Event(EventTypes.CHECK_IF_WIN_EXISTS, event_data)

    res = client.call_server(event)

    if res["win"]:
        return True
    else:
        return False

def get_account_data(client, account_win):
    event = Event(event_type=EventTypes.GET_DATA_FOR_USER, data = {'win': account_win})

    res = client.call_server(event)
    if res is None:
        return None

    return res

def get_permissions_from_db(client):
    event = Event(event_type=EventTypes.GET_ALL_PERMS, data = {'win': ''})

    res = client.call_server(event)
    if res is None:
        return None

    return res

def get_account_permissions(client, account_win):
    event = Event(event_type=EventTypes.GET_PERMS_FOR_USER, data = {'win': account_win})

    res = client.call_server(event)
    if res is None:
        return None

    return res

def get_private_account_note(client, account_win):
    note = ""
    event = Event(event_type=EventTypes.GET_NOTE_FOR_USER, data = {'win': account_win, 'type': 'private'})

    res = client.call_server(event)
    if res is None:
        return note

    note = res

    return note
def get_public_account_note(client, account_win):
    note = ""
    event = Event(event_type=EventTypes.GET_NOTE_FOR_USER, data = {'win': account_win, 'type': 'public'})

    res = client.call_server(event)
    if res is None:
        return note

    note = res

    return note

def check_if_swiped_in(client, account_win):
    event = Event(event_type=EventTypes.CHECK_IF_SWIPED_IN, data = {'win': account_win})
    res = client.call_server(event)
    if res["swiped_in"] == True:
        return True
    else:
        return False

def update_photo_path(client, account_win):
    edit_attrs = {}
    edit_attrs['photo_path'] = './images/' + str(account_win) + '.jpg'
    event = Event(event_type=EventTypes.EDIT_ACCOUNT, data = {'win': account_win, 'edit_attrs': edit_attrs})
    res = client.call_server(event)

def delete_acc(client, account_win):
    event = Event(event_type=EventTypes.DELETE_ACCOUNT, data = {'win': account_win})
    res = client.call_server(event)

def swipe_out_user(client, account_win):
    event = Event(event_type=EventTypes.SWIPE_OUT, data = {'win': account_win})
    res = client.call_server(event)

def swipe_in_user(client, account_win):
    event = Event(event_type=EventTypes.SWIPE_IN, data = {'win': account_win})
    res = client.call_server(event)

def get_swiped_in_users(client):
    event = Event(event_type=EventTypes.GET_SWIPED_IN_USERS, data = {'': ''})

    res = client.call_server(event)
    return res

if __name__ == '__main__':
    client_connection = client_connection('127.0.0.1', 7373)
    attendant_gui = QApplication(sys.argv)

    qssfile="./splums/qss/style.qss"
    with open(qssfile,"r") as f:
        attendant_gui.setStyleSheet(f.read())

    window = MainWindow(client_connection)

    attendant_gui.exec()
