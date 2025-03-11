import os
import sys

from PyQt6.QtWidgets import QApplication, QPushButton, QComboBox, QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLineEdit, QDialog
from PyQt6.QtCore import Qt, QSize, QLibraryInfo, QCoreApplication, QRegularExpression
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
        self.setWindowTitle("Take Picture")

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
        #TODO: REPLACE temp_name_replace_me with the student being modified
        self.cam_worker = cam.CamWorker("temp_name_replace me")

        #Connect the signal being emitted from the cam worker thread to the image_update function of this window
        #Allows for the video feed of cam to be displayed in GUI
        self.cam_worker.image_update.connect(self.image_update_slot)

        #Start camera thread (this makes the thread's run function execute)
        self.cam_worker.start()
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

        layout.addRow("Email:", self.email)
        layout.addRow("Password:", self.password)
        layout.addWidget(add_button)
        add_button.clicked.connect(self.accept)
     
 
        # Set layout for the widget
        self.setLayout(layout)

    def get_email_and_pwd(self):
            return self.email.text(), self.password.text()


class AddStudent(QSqlDatabase, QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.setWindowTitle("Add Student")
 
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
 
        # Add fields to the form layout
        layout.addRow("WIN number:", self.win_box)
        layout.addRow("Role:", self.r_combobox)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Surname:", self.surname)
 
        # Create button that opens camera using cam.py
        photo_button = QPushButton("Take Photo")
        photo_button.clicked.connect(self.show_photo)
 
        # Add Student button
        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_std)
 
        layout.addWidget(photo_button)
        layout.addWidget(add_button)
 
        # Set layout for the widget
        self.setLayout(layout)
 
    # def get_photo(self):
    #     # Call cam.py to open the camera and take a picture
    #     self.photo_url = cam.take_picture(self.win_box.text())
    #     print(self.win_box.text())
    #     #self.show_photo()
 
    def show_photo(self):
        self.w = Picture()
        self.w.show()
 
 
 
 
    def add_std(self):
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
  
 def add_student(self):
        
        print("Adding Student")
        self.db.open()
        if(self.db.isOpen()):
           self.w = AddStudent()
           self.w.show()


 def edit_student(self):
        print("Editing Student")

 def sign_out(self):
        print("Signing out")    


 def __init__(self):
        super().__init__()
            #Table containing all the students
        self.student_table = QTableWidget()
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
            self.update_students()
        else:
            print("Failed to connect to MariaDB:", self.db.lastError().text())
       
     

        self.setWindowTitle("Student Projects Lab User Management System")

        #Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        #Main layout, the over-arching vertical layout that The button bar and the displayed users are apart of
        layout_main = QVBoxLayout()

        #Minimum and maximum gui sizes
        self.setMinimumSize(QSize(1280, 720))
        # self.setMaximumSize(QSize(300, 300))


        #set margins of the layout (how close to the edges they are)
        # layout_main.setContentsMargins(1,1,1,1)

        #Set spacing between all of this layouts elements
        # layout_main.setSpacing(2)
        

        #*******************************************************************************************
        # BUTTON BAR
        #*******************************************************************************************
        layout_buttonbar = QHBoxLayout()
        layout_buttonbar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        #Button bar buttons

        #Create and connect buttons to functions

        #Add Student Button
        self.button_add = QToolButton(self)
        self.button_add.setText("Add Student")
        self.button_add.setIcon(QIcon("./splums/images/add.svg"))
        self.button_add.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.button_add.clicked.connect(self.add_student)


        #Edit Student Button
        self.button_edit = QToolButton(self)
        self.button_edit.setText("Edit Student")
        self.button_edit.setIcon(QIcon("./splums/images/edit.svg"))
        self.button_edit.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        self.button_edit.clicked.connect(self.edit_student)

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
        layout_main.addLayout(layout_buttonbar)



        #*******************************************************************************************
        # Student Table
        #*******************************************************************************************
        
        layout_students = QHBoxLayout()

        self.student_table.verticalHeader().setVisible(False)

        #Configuring way table can be interacted
        self.student_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.student_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.student_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.student_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.student_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode(0))





        #Setting up columns
        self.student_table.setColumnCount(5)

        #Automatic handling of resizing window for table
        self.student_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.student_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.student_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.student_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.student_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        column_labels = [" ", "Student", "Permissions", "Notes", "Head Count"]

        self.student_table.setHorizontalHeaderLabels(column_labels)

        self.update_students()
        


        layout_students.addWidget(self.student_table)


        layout_main.addLayout(layout_students)


        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)
   

    #*******************************************************************************************
    # Create and Update Student Table
    #*******************************************************************************************

 def update_students(self):
        #students = [{"Student Name": "Estlin Mendez", "Permissions": ["Red"], "Notes": "", "url": "temp.png"}, {"Student Name": "Clara McGrew", "Permissions": ["Red", "Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Renee Rickert", "Permissions": ["Red", "Green", "Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Evan Handy", "Permissions": ["Green"], "Notes": "", "url": "temp.png", }, {"Student Name": "Hunter Hamrick", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Kaden Kramer", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Ben Crane", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}]
        students =[]
        select_students = QSqlQuery(self.db)
        select_students.exec("SELECT u.name, n.note FROM users as u LEFT JOIN notes as n ON n.win = u.win")
     #select_students.exec("SELECT u.display_name, u.photo_url, n.text, e.name, e.icon_url FROM user as u LEFT JOIN note as n on n.account_id = u.account_id JOIN account-equipment as ae ON ae.account_id = u.account_id, JOIN equipment as e ON e.equipment_id = ae.equipment_id") ")
      #Question: Should we allow users with no machines on their profile to be displayed?
        while select_students.next():
            student = {
                "Student Name": select_students.value(0),
                "Permissions": ["Red"],
                "Notes": select_students.value(1),
                "url": "temp.png"
            }
            students.append(student)
           # print(student)
      
        head_count = 0
        head_count = len(students)
        self.student_table.setRowCount(head_count)

        row = 0
        for student in students:
       
            #Student Image
            student_image = QLabel()
            student_image.setPixmap(QPixmap("./splums/images/default.png").scaledToHeight(85))
            
            self.student_table.setCellWidget(row, 0, student_image)


            #Student Name
            student_name_cell = QTableWidgetItem(student["Student Name"])
            student_name_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.student_table.setItem(row, 1, student_name_cell)
            row+=1
            #Permissions
            #Have to do this one differently, to accomodate for potential multicolored text
            #CANNOT CURRENTLY HANDLE MORE THAN ONE PERMISSION TYPE
            student_permissions_cell = QLabel("")
            perm_string = ""

            #Go through each perm and set to right color
           #for permission in student["Permissions"]:
            # perm_string += '<font color="' +permission+ '">'+"⬤"+'</font>' + ' '
            #Remove the last space
          #  perm_string = perm_string[:-1]

           # student_permissions_cell.setText(perm_string)
            #permission_stylesheet = "font-size: 18pt;"
           # student_permissions_cell.setStyleSheet(permission_stylesheet)
           # student_permissions_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
           # 
           # self.student_table.setCellWidget(row, 2, student_permissions_cell)

            #Student Count
        if row == 0:
               student_headcount_cell = QTableWidgetItem(str(head_count))
               student_headcount_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
               self.student_table.setItem(row, 4, student_headcount_cell)

#
            ##Notes
            #self.student_table.setItem(row, 3, QTableWidgetItem(student["Notes"]))
     
        #
        #Res#ize rows and first column to fit images
      #  self.student_table.resizeRowsToContents()
      #  self.student_table.resizeColumnToContents(0)



    #*******************************************************************************************
    # Button Functions
    #*******************************************************************************************





if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())