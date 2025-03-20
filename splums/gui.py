import os
import sys

from PyQt6.QtWidgets import QApplication, QPushButton, QComboBox, QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLineEdit, QDialog, QGridLayout, QListWidget, QSizePolicy, QInputDialog, QLCDNumber
from PyQt6.QtCore import Qt, QSize, QLibraryInfo, QCoreApplication, QItemSelection, QItemSelectionModel, QRegularExpression
from PyQt6.QtGui import QPixmap, QIcon, QRegularExpressionValidator
from main import session
from models.models import users
from events import Event
from events import EventTypes
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

from main import get_session

import cam
import event_broker

class Notes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        self.setWindowTitle("Notes")
        self.setObjectName("Main")
        self.setLayout(layout)
        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")
        self.list_widget = QListWidget(self)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        add_button = QPushButton('Add Note')
        add_button.clicked.connect(self.add_note)
        edit_button = QPushButton('Edit Note')
        edit_button.clicked.connect(self.edit_note)
        remove_button = QPushButton('Remove Note')
        remove_button.clicked.connect(self.remove_note)
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_to_db)

        self.list_widget.setStyleSheet("""
    QListWidget::item {
        padding: 5px;
        border-bottom: 1px solid #000;
        margin-bottom: 2px;
    }
    QListWidget::item:selected {
        background-color: #0078d4;
        color: white;
    }
""")
        
        layout.addWidget(self.list_widget)
        layout.addWidget(add_button)
        layout.addWidget(edit_button)
        layout.addWidget(remove_button)
        layout.addWidget(save_button)

    def add_note(self):
        text, ok = QInputDialog.getText(self, 'Add a New Note', 'New Note:')
        if ok and text:
            self.list_widget.addItem(text)

    def edit_note(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            current_item = self.list_widget.currentItem()
            text, ok = QInputDialog.getText(self, 'Edit Note', 'Edit Note:', text=current_item.text())
            if ok and text:
                current_item.setText(text)
    
    def remove_note(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            current_item = self.list_widget.takeItem(current_row)
            del current_item
    
    def save_to_db(self):
        print("Save to db?")

class EditAccount(QWidget):
    def __init__(self, account_table):
        super().__init__()
        self.account_table = account_table
        layout = QFormLayout()
        self.setWindowTitle("Edit Account")

        current_account_row = self.account_table.currentRow()

        if current_account_row > 0:
            account_id = self.account_table.item(current_account_row, 4)
            print(account_id.text())
        
        
        #Make a Select statement (with SQLAlchemy and event broker?) to find in the database where the student_id is equal to the account_id of the current account
        #Add the relevant fields from the database to the fields below with setText() instead of setPlaceholderText()
            
       

 
        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")
 
        # Create WIN input box
        self.win_box = QLineEdit()
        self.win_box.setPlaceholderText("WIN...")
        self.win_box.setInputMask('999999999')

        self.role = QComboBox()
        name_regex = QRegularExpression("[A-Za-z]+")
        name_validator = QRegularExpressionValidator(name_regex)
 
        # Create display name box
        self.display_name = QLineEdit()
        self.display_name.setPlaceholderText("Display Name...")
        self.display_name.setValidator(name_validator)

 
        # Create given name box
        self.given_name = QLineEdit()
        self.given_name.setPlaceholderText("Given Name...")
        self.given_name.setValidator(name_validator)
        # self.given_name.textChanged.connect(self.update_win)
 
        # Create surname box
        self.surname = QLineEdit()
        self.surname.setPlaceholderText("Last Name...")
        
        self.surname.setValidator(name_validator)
        # self.surname.textChanged.connect(self.update_win)

        self.permissions = QComboBox()

          # Create affiliation box
        self.affiliation = QLineEdit()
        self.affiliation.setPlaceholderText("Affiliation...")
        self.affiliation. setValidator(name_validator)
 
           # Create rso box
        self.rso = QLineEdit()
        self.rso.setPlaceholderText("Registered Student Org...")
        self.rso. setValidator(name_validator)
 
       
        # Add fields to the form layout
        layout.addRow("WIN:", self.win_box)
        layout.addRow("Role:", self.role)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Last Name:", self.surname)
        layout.addRow("Permissions:", self.permissions)
        layout.addRow("Affiliation:", self.affiliation)
        layout.addRow("RSO:", self.rso)
 
        # Create button that opens camera using cam.py
        photo_button = QPushButton("Take Photo")
        photo_button.clicked.connect(self.show_photo)

 
        #Notes button
        notes_button = QPushButton("Notes")
        notes_button.clicked.connect(self.show_notes)

        layout.addWidget(photo_button)
        layout.addWidget(notes_button)
 
        # Set layout for the widget
        self.setObjectName("Main")
        self.setLayout(layout)
 
    # def get_photo(self):
    #     # Call cam.py to open the camera and take a picture
    #     self.photo_url = cam.take_picture(self.win_box.text())
    #     print(self.win_box.text())
    #     #self.show_photo()
 
    def show_notes(self):
        self.w = Notes()
        self.w.show()

    def show_photo(self):
        self.w = Picture()
        self.w.show()

class Picture(QWidget):
    def __init__(self):
        super().__init__()
        #Overall layout, picture will be on left, buttons on right
        overall_layout = QVBoxLayout()

        #The label which will contain the video feed. Initializes to loading text that is replaced when cam connection made.
        self.feed_label = QLabel("Loading (If this takes more than a few seconds, ensure webcam is plugged in)")

        #Bottom layout
        bottom_layout = QHBoxLayout()

        #Init save confirmation space instead of hidden, makes it so picture doesn't move up and down.
        self.save_message = QLabel(" ")


        #layout to contain buttons
        buttons_layout = QVBoxLayout()
        self.setWindowTitle("Take PictureT")

        #Might want to find some way to ensure this is always large enough to fit webcam? at the moment assumes resolution of
        #640, 480 specified in cam.py rescaling.
        self.setMinimumSize(QSize(670, 600))
        self.photo_button = QPushButton("Take Picture")
        self.photo_button.clicked.connect(self.take_picture)

        self.retake_button = QPushButton("Retake")
        self.retake_button.clicked.connect(self.retake_picture)
        #Retake button hidden by default
        self.retake_button.hide()

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)

        # buttons_layout.addStretch(1)
        #Add everything to their respective layouts
        overall_layout.addWidget(self.feed_label, alignment= Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.photo_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_layout.addWidget(self.retake_button, alignment= Qt.AlignmentFlag.AlignRight)
        buttons_layout.addWidget(self.exit_button, alignment = Qt.AlignmentFlag.AlignRight)\
        
        bottom_layout.addWidget(self.save_message)
        bottom_layout.addLayout(buttons_layout)
        overall_layout.addLayout(bottom_layout)

        #Start the camera thread
        #TODO: REPLACE temp_name_replace_me with the account being modified
        self.cam_worker = cam.CamWorker("temp_name_replace me")

        #Connect the signal being emitted from the cam worker thread to the image_update function of this window
        #Allows for the video feed of cam to be displayed in GUI
        self.cam_worker.image_update.connect(self.image_update_slot)

        #Start camera thread (this makes the thread's run function execute)
        self.cam_worker.start()
        self.setObjectName("Main")
        self.setLayout(overall_layout)

    def image_update_slot(self, image):
        #Update the videofeed with the latest provided frame
        self.feed_label.setPixmap(QPixmap.fromImage(image))

    def take_picture(self):
        #Calls the cam take picture function
        self.cam_worker.take_picture()
        #Hides photo button and asks if user wants to retake
        self.photo_button.hide()
        self.retake_button.show()
        self.save_message.setText("Photo saved!")
    
    def retake_picture(self):
        self.cam_worker.retake_picture()
        self.retake_button.hide()
        self.photo_button.show()
        self.save_message.setText(" ")

         
    def closeEvent(self, event):
        self.cam_worker.stop()
        
#For the AddUser button
class AddUser(QDialog):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setWindowTitle("Add User")

        self.email = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
 
        # Add User button
        add_button = QPushButton("Add User")
        layout.addRow("Password:", self.password)
        layout.addWidget(add_button)
        add_button.clicked.connect(self.accept)
     
 
        # Set layout for the widget
        self.setObjectName("Main")
        self.setLayout(layout)

    def get_email_and_pwd(self):
            return self.email.text(), self.password.text()


class AddAccount(QSqlDatabase, QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setWindowTitle("Add Account")
 
        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")
 
        # Create WIN input box
        self.win_box = QLineEdit()
        self.win_box.setPlaceholderText("WIN...")
        self.win_box.setInputMask('999999999')
        # self.win_box.textChanged.connect(self.update_win)

        name_regex = QRegularExpression("[A-Za-z]+")
        name_validator = QRegularExpressionValidator(name_regex)
 
        # Create display name box
        self.display_name = QLineEdit()
        self.display_name.setPlaceholderText("Display Name...")
        self.display_name.setValidator(name_validator)
        # self.display_name.textChanged.connect(self.update_win)
 
        # Create given name box
        self.given_name = QLineEdit()
        self.given_name.setPlaceholderText("Given Name...")
        self.given_name.setValidator(name_validator)
        # self.given_name.textChanged.connect(self.update_win)
 
        # Create surname box
        self.surname = QLineEdit()
        self.surname.setPlaceholderText("Surname...")
        
        self.surname.setValidator(name_validator)
        # self.surname.textChanged.connect(self.update_win)
 
        # Fetch roles from the database
        roles = []
        select_roles = QSqlQuery(QSqlDatabase.database())
        select_roles.exec("SELECT user_type FROM user_types")
 
        while select_roles.next():
            role = select_roles.value(0)
            roles.append(role)
            print(role)
 
        # Role selection combobox
        self.r_combobox = QComboBox()
        for role in roles:
            self.r_combobox.addItem(role)

          # Create affiliation box
        self.affiliation = QLineEdit()
        self.affiliation.setPlaceholderText("Affiliation...")
        self.affiliation. setValidator(name_validator)
 
           # Create rso box
        self.rso = QLineEdit()
        self.rso.setPlaceholderText("Registered Student Org...")
        self.rso. setValidator(name_validator)

        # Add fields to the form layout
        layout.addRow("WIN:", self.win_box)
        layout.addRow("Role:", self.r_combobox)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Surname:", self.surname)
        layout.addRow("Affiliation:", self.affiliation)
        layout.addRow("RSO:", self.rso)
 
        # Create button that opens camera using cam.py
        photo_button = QPushButton("Take Photo")
        photo_button.clicked.connect(self.show_photo)
 
        # Add account button
        add_button = QPushButton("Add Account")
        add_button.clicked.connect(self.add_act)
 
        layout.addWidget(photo_button)
        layout.addWidget(add_button)
        # Set layout for the widget
        self.setObjectName("Main")
        self.setLayout(layout)
 
    # def get_photo(self):
    #     # Call cam.py to open the camera and take a picture
    #     self.photo_url = cam.take_picture(self.win_box.text())
    #     print(self.win_box.text())
    #     #self.show_photo()
 
    def show_photo(self):
        self.w = Picture()
        self.w.show()
 
 
 
 
    def add_act(self):
        win = self.win_box.text()
        print(win)
        role = self.r_combobox.currentText()
        print(role)
        display_name = self.display_name.text()
        print(display_name)
        given_name = self.given_name.text()
        print(given_name)
        surname = self.surname.text()
        print(surname)

       # if role == "admin" or role == "attendant":
         #    userDialog = AddUser()
          #   if userDialog.exec() == QDialog.DialogCode.Accepted:
          #       email, password = userDialog.get_email_and_pwd()
           #      print(email, password)

        new_event = Event(
          EventTypes.CREATE_NEW_USER,
         {
             "win": win,
              "role": role,
             "display_name": display_name,
               "given_name": given_name,
              "surname": surname,
               "photo_url": self.photo_url
           }
       )
 
        event_broker.event_broker(new_event)
        self.close()


    

class MainWindow(QMainWindow):

#*******************************************************************************************
# Button Functions
#*******************************************************************************************
    def add_account(self):
        
        print("Adding Account")
        self.db.open()
        if(self.db.isOpen()):
           self.w = AddAccount()
           self.w.show()


    def edit_account(self):
        self.w = EditAccount(self.account_table)
        self.w.show()

    def sign_out(self):
        print("Signing out")    


    def __init__(self):
        super().__init__()
            #Table containing all the accounts
        self.account_table = QTableWidget()
        #selection = self.account_table.selectionModel()
        self.headcount_display = QLCDNumber(self)
        #self.account_table.selectRow(0)
              # Connect to MariaDB (Docker)
        print(QSqlDatabase.drivers()) 
        plugin_path = QLibraryInfo.LibraryPath
        qt_install_path = QCoreApplication.libraryPaths()
        #print("Possible Qt Plugin Paths:", qt_install_path)

        #sqldrivers_path = os.path.join(plugin_path, "sqldrivers")

        print("Qt SQL Drivers Path:", plugin_path)
        self.db = QSqlDatabase.addDatabase("QMARIADB")  
        driver = self.db.driver()
     
        self.db.setHostName("127.0.0.1")
        self.db.setPort(3307) 
        self.db.setDatabaseName("splums")
        self.db.setUserName("splums")
        self.db.setPassword("example")
        self.db.open()
        if(self.db.isOpen()):
            self.update_accounts()
        else:
            print("Failed to connect to MariaDB:", self.db.lastError().text())
       
     

        self.setWindowTitle("Student Projects Lab User Management System")

        #Styling moved to style.qss, keeping this here in case font sizes here ends up being more optimal
        # self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        #Main layout, the over-arching vertical layout that The button bar and the displayed users are apart of
        layout_main = QVBoxLayout()

        #Minimum and maximum gui sizes
        self.setMinimumSize(QSize(1280, 720))
        # self.setMaximumSize(QSize(300, 300))


        #set margins of the layout (how close to the edges they are)
        # layout_main.setContentsMargins(1,1,1,1)

        #Set spacing between all of this layouts elements
        # layout_main.setSpacing(2)
        
        layout_topsplit = QHBoxLayout()

        #*******************************************************************************************
        # BUTTON BAR
        #*******************************************************************************************
        layout_buttonbar = QHBoxLayout()
        layout_buttonbar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        #Button bar buttons

        #Create and connect buttons to functions

        #Add Account Button
        self.button_add = QToolButton(self)
        self.button_add.setText("Add Account")
        self.button_add.setIcon(QIcon("./splums/images/add.svg"))
        self.button_add.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.button_add.clicked.connect(self.add_account)


        #Edit Account Button
        self.button_edit = QToolButton(self)
        self.button_edit.setText("Edit Account")
        self.button_edit.setIcon(QIcon("./splums/images/edit.svg"))
        self.button_edit.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.button_edit.clicked.connect(self.edit_account)

        #Sign Out Button
        self.button_sign_out = QToolButton(self)
        self.button_sign_out.setText("Sign Out")
        self.button_sign_out.setIcon(QIcon("./splums/images/signout.svg"))

        self.button_sign_out.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_sign_out.clicked.connect(self.sign_out)


        #Set dimensions of buttonbar buttons
        bdim=[100, 80]
        bicondim=[50, 50]
        self.button_add.setFixedSize(QSize(bdim[0], bdim[1]))
        self.button_edit.setFixedSize(QSize(bdim[0], bdim[1]))
        self.button_sign_out.setFixedSize(QSize(bdim[0], bdim[1]))

        self.button_add.setIconSize(QSize(bicondim[0], bicondim[1]))
        self.button_edit.setIconSize(QSize(bicondim[0], bicondim[1]))
        self.button_sign_out.setIconSize(QSize(bicondim[0], bicondim[1]))



        #Add the buttons to the button bar
        layout_buttonbar.addWidget(self.button_add)
        layout_buttonbar.addWidget(self.button_edit)
        layout_buttonbar.addWidget(self.button_sign_out)

        #Add the button bar to the main layout
        layout_topsplit.addLayout(layout_buttonbar)


        #*******************************************************************************************
        # Head Count
        #*******************************************************************************************

        #Righthand toolbar for headcount 
        layout_rightbar = QHBoxLayout()
        layout_rightbar.setAlignment(Qt.AlignmentFlag.AlignRight)


        layout_rightbar = QHBoxLayout()
        layout_rightbar.setAlignment(Qt.AlignmentFlag.AlignRight)


        layout_headcount = QVBoxLayout()
        layout_headcount.setSpacing(0)
        headcount_header = QLabel(" Headcount")
        headcount_header.setStyleSheet("font-weight: bold;")
        headcount_header.setObjectName("HeadcountHeader")
        layout_headcount.addWidget(headcount_header)

        self.headcount_display.setDigitCount(2)
        layout_headcount.addWidget(self.headcount_display)
        layout_rightbar.addLayout(layout_headcount)
        layout_topsplit.addLayout(layout_rightbar)



        layout_main.addLayout(layout_topsplit)
        self.headcount_display.setFixedSize(QSize(bdim[0]-30, bdim[1]-25))
        self.headcount_display.display(0)

        #*******************************************************************************************
        # Account Table
        #*******************************************************************************************
        
        layout_accounts = QHBoxLayout()

        #Table containing all the accounts
        self.account_table = QTableWidget()


        self.account_table.verticalHeader().setVisible(False)

        #Configuring way table can be interacted
        self.account_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.account_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.account_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.account_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.account_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode(0))





        #Setting up columns
        self.account_table.setColumnCount(5)

        #Automatic handling of resizing window for table
        self.account_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.account_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        column_labels = [" ", "Account", "Permissions", "Notes", "Head Count"]

        self.account_table.setHorizontalHeaderLabels(column_labels)

        self.update_accounts()
        


        layout_accounts.addWidget(self.account_table)


        layout_main.addLayout(layout_accounts)


        widget = QWidget()
        widget.setObjectName("Main")
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)



        #*******************************************************************************************
        # Account Table
        #*******************************************************************************************
        
        layout_accounts = QHBoxLayout()

        self.account_table.verticalHeader().setVisible(False)

        #Configuring way table can be interacted
        self.account_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.account_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.account_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.account_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.account_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode(0))





        #Setting up columns
        self.account_table.setColumnCount(5)

        #Automatic handling of resizing window for table
        self.account_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.account_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.account_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        column_labels = [" ", "Account", "Permissions", "Notes", "Head Count"]

        self.account_table.setHorizontalHeaderLabels(column_labels)

        self.update_accounts()
        


        layout_accounts.addWidget(self.account_table)


        layout_main.addLayout(layout_accounts)


        widget = QWidget()
        widget.setObjectName("Main")
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
   

    #*******************************************************************************************
    # Create and Update Accounts Table
    #*******************************************************************************************

    def update_accounts(self):
        accounts = []

        #select_accounts.exec("SELECT u.display_name, u.photo_url, n.text, e.name, e.icon_url FROM user as u LEFT JOIN note as n on n.account_id = u.account_id JOIN account-equipment as ae ON ae.account_id = u.account_id, JOIN equipment as e ON e.equipment_id = ae.equipment_id") ")
        #Question: Should we allow users with no machines on their profile to be displayed?
        # while select_accounts.next():
            #   account = {
            #       "Account Name": select_accounts.value(0),
            #       "Permissions": ["Red"],
            #       "Notes": select_accounts.value(1),
            #       "url": "temp.png"
            #  }
            #  accounts.append(account)

            #IMPORTANT: We need a SQLAlchemy query, that gets the name, permissions, etc. from the database when the accounts are logged in.
            #I assume we're doing this from the Event Broker. We can replace the for loop with a while loop and loop through
            #the query, populating the important fields and adding them to the dictionary which will be filled below.
            #It might be a while loop like the one above.
        
        for i in range(6):
            account = {
                "Account Name": "Clara McGrew",
                "Permissions": ["Red"],
                "Notes": ["normal"],
                "url": "temp.png",
                "Account ID": "111111111"
            }
            accounts.append(account)
        
        head_count = len(accounts)
        self.account_table.setRowCount(head_count)
        self.headcount_display.display(head_count)

        row = 0
        for account in accounts:
            # Account Image
            account_image = QLabel()
            account_image.setPixmap(QPixmap("./splums/images/default.png").scaledToHeight(85))
            self.account_table.setCellWidget(row, 0, account_image)

            # Account Name
            account_name_cell = QTableWidgetItem(account["Account Name"])
            account_name_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table.setItem(row, 1, account_name_cell)

            # Permissions
            account_permissions_cell = QLabel("")
            perm_string = " ".join(f'<font color="{permission}">⬤</font>' for permission in account["Permissions"])
            account_permissions_cell.setText(perm_string)
            account_permissions_cell.setStyleSheet("font-size: 18pt;")
            account_permissions_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table.setCellWidget(row, 2, account_permissions_cell)

            # Notes
            note_layout = QHBoxLayout()
            for note in account["Notes"]:
                note_button = QPushButton()
                note_button.setText({
                    "normal": "🟩",
                    "discuss": "💡",
                    "concern": "❗️",
                    "banned": "🛑"
                }.get(note, "Unrecognized note type"))
                note_button.setFixedSize(QSize(60, 60))
                note_layout.addWidget(note_button)
            note_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            notewidget = QWidget()
            notewidget.setLayout(note_layout)
            self.account_table.setCellWidget(row, 3, notewidget)

            # Account ID
            account_id_hidden = QTableWidgetItem(account["Account ID"])
            account_id_hidden.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.account_table.setItem(row, 4, account_id_hidden)
            self.account_table.setColumnHidden(4, True)

            row += 1

        # Resize rows and first column to fit images
        self.account_table.resizeRowsToContents()
        self.account_table.resizeColumnToContents(0)


if __name__ == '__main__':
    attendant_gui = QApplication(sys.argv)
    qssfile="./splums/qss/style.qss"
 

    with open(qssfile,"r") as f:
        attendant_gui.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(attendant_gui.exec())
