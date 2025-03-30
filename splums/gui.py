import socket
import pickle

from client import *
import os
import sys

from PyQt6.QtWidgets import QApplication, QPushButton, QComboBox, QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLineEdit, QDialog, QGridLayout, QListWidget, QSizePolicy, QInputDialog, QLCDNumber, QPlainTextEdit, QTextEdit, QScrollArea, QCheckBox, QGroupBox
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
        self.created_at = build_info['created_at']
        self.last_updated_at = build_info['last_updated_at']
        self.swiped_in = build_info['swiped_in']
        self.last_access = build_info['last_access']

        # lazy loading
        # load when gui needs
        self.note = ""

class Notes(QWidget):
    save_update = pyqtSignal()
    def __init__(self, client, win):
        super().__init__()
        self.client = client
        self.win = win
        main_layout = QGridLayout(self)
        self.setWindowTitle("Notes")
        self.setObjectName("Main")
        self.setLayout(main_layout)

        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")
        
        self.text_box = QPlainTextEdit()
        self.text_box.setPlainText(get_account_note(self.client, self.win))

        save_button = QPushButton('Save')

        main_layout.addWidget(self.text_box)
        main_layout.addWidget(save_button)

        save_button.clicked.connect(self.save_note)

    def save_note(self):
        data = {}
        data['win'] = self.win
        data['edit_attrs'] = {}
        data['edit_attrs']['text'] = self.text_box.toPlainText()

        edit_note(self.client, data)

        self.save_update.emit()

class Picture(QWidget):
    photo_update = pyqtSignal()
    def __init__(self, client, win):
        super().__init__()
        self.client = client
        self.win = str(win)

        self.setWindowTitle("Take Picture")

        #Might want to find some way to ensure this is always large enough to fit webcam? at the moment assumes resolution of
        #640, 480 specified in cam.py rescaling.
        self.setMinimumSize(QSize(670, 600))

        main_layout = QVBoxLayout()
        bottom_row = QHBoxLayout()
        buttons_block = QVBoxLayout()

        self.setObjectName("Main")
        self.setLayout(main_layout)

        #The label which will contain the video feed. Initializes to loading text that is replaced when cam connection made.
        self.feed_label = QLabel("Loading (If this takes more than a few seconds, ensure webcam is plugged in)")
        #Init save confirmation space instead of hidden, makes it so picture doesn't move up and down.
        self.save_message = QLabel(" ")

        self.photo_button = QPushButton("Take Photo")
        self.save_button = QPushButton("Save Photo")
        self.retake_button = QPushButton("Retake")
        self.exit_button = QPushButton("Exit")

        self.retake_button.hide()
        self.save_button.hide()

        bottom_row.addWidget(self.save_message)
        bottom_row.addLayout(buttons_block)

        main_layout.addWidget(self.feed_label, alignment= Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(bottom_row)

        buttons_block.addWidget(self.photo_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.retake_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.save_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_block.addWidget(self.exit_button, alignment = Qt.AlignmentFlag.AlignRight)

        self.photo_button.clicked.connect(self.take_picture)
        self.retake_button.clicked.connect(self.retake_picture)
        self.save_button.clicked.connect(self.save_photo)
        self.exit_button.clicked.connect(self.close)

        #Start the camera thread
        self.cam_worker = cam.CamWorker(self.win)

        #Connect the signal being emitted from the cam worker thread to the image_update function of this window
        #Allows for the video feed of cam to be displayed in GUI
        self.cam_worker.image_update.connect(self.image_update_slot)

        #Start camera thread (this makes the thread's run function execute)
        self.cam_worker.start()

    def image_update_slot(self, image):
        #Update the videofeed with the latest provided frame
        self.feed_label.setPixmap(QPixmap.fromImage(image))

    def take_picture(self):
        self.cam_worker.take_picture()
        #Hides photo button and asks if user wants to retake
        self.photo_button.hide()
        self.save_button.show()
        self.retake_button.show()
    
    def save_photo(self):
        self.save_message.setText("Photo saved!")
        self.cam_worker.save_photo()
        self.save_button.hide()
        self.retake_button.hide()
        self.photo_button.show()

        self.photo_update.emit()

    def retake_picture(self):
        self.cam_worker.retake_picture()
        self.retake_button.hide()
        self.save_button.hide()
        self.photo_button.show()
        self.save_message.setText(" ")

    def closeEvent(self, event):
        self.cam_worker.stop()

class EditAccount(QWidget):
    photo_update = pyqtSignal()
    save_update = pyqtSignal()
    def __init__(self, win, client):
        super().__init__()
        self.client = client
        self.win = win

        print(f"editing the account of win: {win}")

        self.setWindowTitle("Edit Account")

        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        layout = QFormLayout()

        self.win_box = QLineEdit()
        self.role = QComboBox()
        self.display_name = QLineEdit()
        self.given_name = QLineEdit()
        self.surname = QLineEdit()

        self.permissions = QGroupBox()
        self.perm_layout = QVBoxLayout()

        self.drill_press = QCheckBox("Drill Press")
        self.cnc_machine = QCheckBox("CNC Machine")
        self.laser_cutter = QCheckBox("Laser Cutter")
        self.soldering_station = QCheckBox("Soldering Station")
        self.welding_station = QCheckBox("Welding Station")

        self.perm_layout.addWidget(self.drill_press)
        self.perm_layout.addWidget(self.cnc_machine)
        self.perm_layout.addWidget(self.laser_cutter)
        self.perm_layout.addWidget(self.soldering_station)
        self.perm_layout.addWidget(self.welding_station)

        self.permissions.setLayout(self.perm_layout)

        self.affiliation = QLineEdit()
        self.rso = QLineEdit()

        notes_button = QPushButton("Notes")
        photo_button = QPushButton("Take Photo")
        save_button = QPushButton("Save")

        photo_button.clicked.connect(self.show_photo)
        notes_button.clicked.connect(self.show_notes)
        save_button.clicked.connect(self.save_edit)

        layout.addRow("WIN:", self.win_box)
        layout.addRow("Role:", self.role)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Surname:", self.surname)
        layout.addRow("Permissions:", self.permissions)
        layout.addRow("Affiliation:", self.affiliation)
        layout.addRow("RSO:", self.rso)

        layout.addWidget(photo_button)
        layout.addWidget(notes_button)
        layout.addWidget(save_button)

        self.setObjectName("Main")
        self.setLayout(layout)

        win_validator = QRegularExpressionValidator(QRegularExpression("[0-9]{9}"))
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z]+"))

        self.win_box.setPlaceholderText("WIN...")
        self.win_box.setValidator(win_validator)
            
        # TODO IMPLEMENT ROLE FUNCTIONALITY
        # TODO there needs to be some checking here to see who the attendant is. an attendant should not be able to make anyone an Administrator / Attendant
        self.role.addItem("User")
        self.role.addItem("Administrator")
        self.role.addItem("Attendant")
 
        self.display_name.setPlaceholderText("Display Name...")
        self.display_name.setValidator(name_validator)
 
        self.given_name.setPlaceholderText("Given Name...")
        self.given_name.setValidator(name_validator)
 
        self.surname.setPlaceholderText("Surname...")
        self.surname.setValidator(name_validator)

        self.affiliation.setPlaceholderText("Affiliation...")
        self.affiliation.setValidator(name_validator)
 
        self.rso.setPlaceholderText("Registered Student Org...")
        self.rso.setValidator(name_validator)

        self.initial_load()
            
    def initial_load(self):
        acc_data = get_account_data(self.client, self.win)

        self.win_box.setText(str(acc_data['win']))
        self.display_name.setText(acc_data['display_name'])
        self.given_name.setText(acc_data['given_name'])
        self.surname.setText(acc_data['surname'])
        if acc_data['affiliation']is not None:
            self.affiliation.setText(acc_data['affiliation'])

        if acc_data['rso'] is not None:
            self.rso.setText(acc_data['rso'])

        permissions = get_account_permissions(self.client, self.win)
        if permissions is not None:
            for item in self.permissions.findChildren(QCheckBox):
                for perm in permissions:
                    print(f'{item.text()} on {perm}')
                    if item.text().lower().replace(" ", "_") == perm:
                        print(f'need to check the state of {perm}')
                        item.setChecked(True)

        self.role.setCurrentText(acc_data['role'].capitalize())

    # TODO add proper error handling
    def save_edit(self):
        data = {}
        data['win'] = self.win
        data['edit_attrs'] = {}
        
        data['edit_attrs']['display_name'] = self.display_name.text()
        data['edit_attrs']['given_name'] = self.given_name.text()
        data['edit_attrs']['surname'] = self.surname.text()
        data['edit_attrs']['win'] = self.win_box.text()
        data['edit_attrs']['affiliation'] = self.affiliation.text()
        data['edit_attrs']['rso'] = self.rso.text()
        data['edit_attrs']['role'] = self.role.currentText().lower()
        data['edit_attrs']['permissions'] = []
        data['edit_attrs']['no_permissions'] = []

        for item in self.permissions.findChildren(QCheckBox):
            if item.isChecked():
                data['edit_attrs']['permissions'].append(item.text().lower().replace(" ", "_"))
            else:
                data['edit_attrs']['no_permissions'].append(item.text().lower().replace(" ", "_"))

        edit_account(self.client, data)
        self.save_update.emit()

    def show_notes(self):
        self.w = Notes(self.client, self.win)
        self.w.show()
        self.w.save_update.connect(self.update_note)

    def show_photo(self):
        self.w = Picture(self.client, self.win)
        self.w.show()
        self.w.photo_update.connect(self.update_photo)

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

        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        layout = QFormLayout()

        self.win_box = QLineEdit()
        self.role = QComboBox()
        self.display_name = QLineEdit()
        self.given_name = QLineEdit()
        self.surname = QLineEdit()

        self.permissions = QGroupBox()
        self.perm_layout = QVBoxLayout()

        self.drill_press = QCheckBox("Drill Press")
        self.cnc_machine = QCheckBox("CNC Machine")
        self.laser_cutter = QCheckBox("Laser Cutter")
        self.soldering_station = QCheckBox("Soldering Station")
        self.welding_station = QCheckBox("Welding Station")

        self.perm_layout.addWidget(self.drill_press)
        self.perm_layout.addWidget(self.cnc_machine)
        self.perm_layout.addWidget(self.laser_cutter)
        self.perm_layout.addWidget(self.soldering_station)
        self.perm_layout.addWidget(self.welding_station)

        self.permissions.setLayout(self.perm_layout)

        self.affiliation = QLineEdit()
        self.rso = QLineEdit()

        photo_button = QPushButton("Take Photo")
        save_button = QPushButton("Save")

        photo_button.clicked.connect(self.show_photo)
        save_button.clicked.connect(self.save_edit)

        layout.addRow("WIN:", self.win_box)
        layout.addRow("Role:", self.role)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Surname:", self.surname)
        layout.addRow("Permissions:", self.permissions)
        layout.addRow("Affiliation:", self.affiliation)
        layout.addRow("RSO:", self.rso)

        layout.addWidget(photo_button)
        layout.addWidget(save_button)

        self.setObjectName("Main")
        self.setLayout(layout)

        win_validator = QRegularExpressionValidator(QRegularExpression("[0-9]{9}"))
        name_validator = QRegularExpressionValidator(QRegularExpression("[A-Za-z]+"))

        self.win_box.setPlaceholderText("WIN...")
        self.win_box.setValidator(win_validator)
            
        # TODO IMPLEMENT ROLE FUNCTIONALITY
        # TODO there needs to be some checking here to see who the attendant is. an attendant should not be able to make anyone an Administrator / Attendant
        self.role.addItem("User")
        self.role.addItem("Administrator")
        self.role.addItem("Attendant")
 
        self.display_name.setPlaceholderText("Display Name...")
        self.display_name.setValidator(name_validator)
 
        self.given_name.setPlaceholderText("Given Name...")
        self.given_name.setValidator(name_validator)
 
        self.surname.setPlaceholderText("Surname...")
        self.surname.setValidator(name_validator)

        self.affiliation.setPlaceholderText("Affiliation...")
        self.affiliation.setValidator(name_validator)
 
        self.rso.setPlaceholderText("Registered Student Org...")
        self.rso.setValidator(name_validator)

    # TODO add proper error handling
    # TODO ADD CHECK FOR IF WIN IS ALREADY TAKEN
    def save_edit(self):
        if self.win_box.text() == "":
            print("err invalid win")
            return
        if self.display_name.text() == "":
            print("err must enter display name")
            return
        if self.given_name.text() == "":
            print("err must enter given_name")
            return
        if self.surname.text() == "":
            print("err must enter surname")
            return
        data = {}
        data['win'] = self.win_box.text()
        data['edit_attrs'] = {}
        
        data['edit_attrs']['display_name'] = self.display_name.text()
        data['edit_attrs']['given_name'] = self.given_name.text()
        data['edit_attrs']['surname'] = self.surname.text()
        data['edit_attrs']['win'] = self.win_box.text()
        data['edit_attrs']['affiliation'] = self.affiliation.text()
        data['edit_attrs']['rso'] = self.rso.text()
        data['edit_attrs']['role'] = self.role.currentText().lower()
        data['edit_attrs']['permissions'] = []


        for item in self.permissions.findChildren(QCheckBox):
            if item.isChecked():
                data['edit_attrs']['permissions'].append(item.text().lower().replace(" ", "_"))

        new_account(self.client, data)

        self.save_update.emit()

    def show_photo(self):
        if self.win_box.text() == "":
            print("err invalid win")
            return
        self.w = Picture(self.client, self.win_box.text())
        self.w.show()

class MainWindow(QMainWindow):
    def __init__(self, client_connection):
        super().__init__()
        self.client_connection = client_connection

        self.setWindowTitle("Student Projects Lab User Management System")
        self.setMinimumSize(QSize(1280, 720))

        self.main_widget = QWidget()
        self.main_widget.setObjectName("Main")

        layout_main = QVBoxLayout()
        self.main_widget.setLayout(layout_main)
        self.setCentralWidget(self.main_widget)

        # initialize as empty for now
        self.accounts = []

        button_dim=[100, 80]
        button_icon_dim=[50, 50]

        # digit width, dimensions, digit value
        self.headcount_display = self.initialize_lcd(2, [button_dim[0]-30, button_dim[1]-25], 0)

        self.add_button = self.initialize_button("Add Account", "./splums/images/add.svg", self.add_account, button_dim, button_icon_dim)
        self.edit_button = self.initialize_button("Edit Account", "./splums/images/edit.svg", self.edit_account, button_dim, button_icon_dim)
        self.signout_button = self.initialize_button("Sign Out", "./splums/images/signout.svg", self.sign_out, button_dim, button_icon_dim)

        layout_topsplit = QHBoxLayout()
        layout_main.addLayout(layout_topsplit)

        button_bar = QHBoxLayout()
        button_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        button_bar.addWidget(self.add_button)
        button_bar.addWidget(self.edit_button)
        button_bar.addWidget(self.signout_button)
        layout_topsplit.addLayout(button_bar)

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
        layout_main.addLayout(layout_accounts)

        layout_accounts.addWidget(self.account_table)

        self.initial_accounts_load()
        self.render_accounts_to_screen()
        self.show()

        self.account_table.selectRow(-1)

    # sends the win of the account that you want to edit to the widget as well as the client
    # connection. from there it grabs and edits the data how it wants.
    def edit_account(self):
        selected_row = self.account_table.currentRow()

        if selected_row == -1:
            print('no account selected, click to select the account you want to edit')
            return

        self.w = EditAccount(self.accounts[selected_row].win, self.client_connection)
        self.w.show()

        # connect signal to pressing the save button 
        self.w.photo_update.connect(self.update_photos)
        self.w.save_update.connect(self.update_save)

    def update_save(self):
        self.accounts.clear()
        self.initial_accounts_load()
        self.render_accounts_to_screen()

    def update_photos(self):
        row = 0
        # for each acc loaded into the gui
        for acc in self.accounts:
            account_photo = QLabel()
            account_photo.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))

            self.account_table.setCellWidget(row, 0, account_photo)
            row += 1

        self.setWindowTitle("new title")

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
        new_account_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        new_account_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        new_account_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        column_labels = ["Photo", "Account", "Permissions", "Notes", "Head Count"]
        new_account_table.setHorizontalHeaderLabels(column_labels)

        return new_account_table

    def initial_accounts_load(self):
        get_account_event = Event(event_type=EventTypes.GET_USERS_BY_ROLE, data = {'role': ''})
        # for each account ordered by role, add to self.accounts based on each dict of data returned.
        for c in self.client_connection.call_server(get_account_event):
            print(c)
            self.accounts.append(Account(c))

        # load notes for each account
        for acc in self.accounts:
            res = get_account_note(self.client_connection, acc.win)
            print(f"res: {res}")
            acc.note = res

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
            self.account_table.setItem(row, 1, account_name_cell)

#            # permission is based on color of permission in acc_permission
#            account_permissions_cell = QLabel("")
#            # TODO ADD THIS LATER
#            perm_string = " ".join(f'<font color="{permission}">⬤</font>' for permission in acc.permissions)
#            account_permissions_cell.setText(perm_string)
#            account_permissions_cell.setStyleSheet("font-size: 18pt;")
#            account_permissions_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
#            self.account_table.setCellWidget(row, 2, account_permissions_cell)

            # horizontal row of buttons for each note this is the layout for the actual notewidget
            note_text_cell = QTextEdit(acc.note)
            note_text_cell.setReadOnly(True)
            note_text_cell.setStyleSheet("font-size: 12pt;")
            note_text_cell.setFixedHeight(100)
            note_text_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.account_table.setCellWidget(row, 3, note_text_cell)

            # Account ID
            account_id_hidden = QTableWidgetItem(acc.win)
            account_id_hidden.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table.setItem(row, 4, account_id_hidden)
            self.account_table.setColumnHidden(4, True)

            row += 1

        # Resize rows and first column to fit images
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnToContents(0)

def edit_account(client, edit_data):
    event = Event(EventTypes.EDIT_ACCOUNT, edit_data)

    res = client.call_server(event)

def new_account(client, edit_data):
    event = Event(EventTypes.CREATE_ACCOUNT, edit_data)

    res = client.call_server(event)

def edit_note(client, edit_data):
    event = Event(EventTypes.EDIT_NOTE_FOR_USER, edit_data)

    res = client.call_server(event)

def get_account_data(client, account_win):
    event = Event(event_type=EventTypes.GET_DATA_FOR_USER, data = {'win': account_win})

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


def get_account_note(client, account_win):
    note = ""
    event = Event(event_type=EventTypes.GET_NOTE_FOR_USER, data = {'win': account_win})

    res = client.call_server(event)
    if res is None:
        return note

    note = res

    return note

if __name__ == '__main__':
    client_connection = client_connection('127.0.0.1', 7373)
    attendant_gui = QApplication(sys.argv)

    qssfile="./splums/qss/style.qss"
    with open(qssfile,"r") as f:
        attendant_gui.setStyleSheet(f.read())

    window = MainWindow(client_connection)

    attendant_gui.exec()
