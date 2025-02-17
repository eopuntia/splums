import os
import sys

from PyQt6.QtWidgets import QApplication, QPushButton, QComboBox, QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLineEdit
from PyQt6.QtCore import Qt, QSize, QLibraryInfo, QCoreApplication
from PyQt6.QtGui import QPixmap, QIcon
from main import session
from models.models import users
from events import Event
from events import EventTypes
from sqlalchemy.exc import SQLAlchemyError
from PyQt6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel


class AddStudent(QSqlDatabase, QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout()
        self.label = QLabel("Another Window")

        username_id_edit = QLineEdit(parent=self)
        role_name = QLineEdit(parent=self)
        display_name = QLineEdit(parent=self)
        given_name = QLineEdit(parent=self)
        surname = QLineEdit(parent=self)
        roles = []
        select_roles = QSqlQuery(QSqlDatabase.database())
        select_roles.exec("SELECT name FROM user_types")
        #select_roles.exec("SELECT name from roles")

        while select_roles.next():
            role = select_roles.value(0)
            roles.append(role)
            print(role)

        r_combobox = QComboBox()

        for role in roles:
            r_combobox.addItem(role)
    

        layout.addRow("WIN number:", username_id_edit)
        layout.addRow("Role:", r_combobox)
        layout.addRow("Display Name:", display_name)
        layout.addRow("Given Name:", given_name)
        layout.addRow("Surname:", surname)

        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_std)
        layout.addWidget(add_button)
        self.setLayout(layout)
        

    def add_std(self, s):
        print("click", s)


    

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

 def select_user_types(self):
        # Create a QSqlQuery object
        query = QSqlQuery(self.db)

        # Perform a SELECT query on the user_types table
        query.exec("SELECT user_type_id, name, last_updated_at FROM user_types")

        # Check if the query executed successfully
        if query.lastError().isValid():
            print("Query failed:", query.lastError().text())
        else:
            # Retrieve the data
            while query.next():
                user_type_id = query.value(0) 
                name = query.value(1)          # Get the second column (name)
                last_updated_at = query.value(2)  # Get the third column (last_updated_at)

                # Print or process the data
                print(f"User Type ID: {user_type_id}, Name: {name}, Last Updated At: {last_updated_at}")

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
            self.select_user_types()
            self.update_students()
        else:
            print("Failed to connect to MariaDB:", self.db.lastError().text())
          #  print("Failed to connect to MariaDB:", self.db.lastError().text())
#
       # driver = self.db.driver()
       # if driver:
        #    print(f"Driver type: {driver.dbmsType}")
        #    self.db.setHostName("127.0.0.1") 
         #   self.db.setPort(3307)  
        #    self.db.setDatabaseName("splums") 
        #    self.db.setUserName("splums")  
        #    self.db.setPassword("example")
        #    if self.db.open():
           #     print("Connected to the database")
#
           #     self.model = QSqlTableModel(self)
           #     self.model.setTable("user")  # Set the table name

          #  if self.model.select():
           #     self._table_view.setModel(self.model)
           # else:
               # print("Failed to select data from the table")
     #   else:
     #       print("Driver not loaded. Failed to connect to database")
     

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