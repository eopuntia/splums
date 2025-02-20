import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QPushButton, QLineEdit
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from events import Event, EventTypes
from event_broker import event_broker
import cam


class UserCreationWindow(QWidget):
    def __init__(self):
        # Initialize variables
        self.name = ''
        self.win = ''
        self.photo_url = ''

        super().__init__()
        self.setWindowTitle("Add Student")

        #Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        # Set layout as a vertical box
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Create name input box
        self.name_label = QLabel("Enter Name:")
        self.name_box = QLineEdit()
        self.name_box.setPlaceholderText("Name...")
        self.name_box.textChanged.connect(self.update_name)

        # Create WIN input box
        self.win_label = QLabel("Enter WIN:")
        self.win_box = QLineEdit()
        self.win_box.setPlaceholderText("WIN...")
        self.win_box.textChanged.connect(self.update_win)

        # Create button that opens camera using cam.py
        self.photo_button = QPushButton()
        self.photo_button.setText("Take Photo")
        self.photo_button.clicked.connect(self.get_photo)

        # Create submit button
        self.submit_button = QPushButton()
        self.submit_button.setText("Submit")
        self.submit_button.clicked.connect(self.submit_user)

        # Add all fields to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_box)
        layout.addWidget(self.win_label)
        layout.addWidget(self.win_box)
        layout.addWidget(self.photo_button)
        layout.addWidget(self.submit_button)

        # Display layout
        self.setLayout(layout)

    def update_name(self, s):
        print("Name Updated")
        # Update the name variable everytime the field is changed
        self.name = s

    def update_win(self, s):
        print("WIN Updated")
        # Update the win variable everytime the field is changed
        self.win = s

    def get_photo(self):
        # Call cam.py to open the camera and take a picture
        self.photo_url = cam.take_picture(self.win)

    def submit_user(self):
        # Create event with new user data
        new_event = Event(
            EventTypes.CREATE_NEW_USER,
            {
                "win": self.win,
                "name": self.name,
                "photo_url": self.photo_url,
                "user_type_id": 3
            }
        )
        # Pass to the event broker
        event_broker(new_event)
        # Close window
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        #Table containing all the students
        self.student_table = QTableWidget()


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
        students = [{"Student Name": "Estlin Mendez", "Permissions": ["Red"], "Notes": "", "url": "temp.png"}, {"Student Name": "Clara McGrew", "Permissions": ["Red", "Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Renee Rickert", "Permissions": ["Red", "Green", "Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Evan Handy", "Permissions": ["Green"], "Notes": "", "url": "temp.png", }, {"Student Name": "Hunter Hamrick", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Kaden Kramer", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}, {"Student Name": "Ben Crane", "Permissions": ["Blue"], "Notes": "", "url": "temp.png"}]
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

            #Permissions
            #Have to do this one differently, to accomodate for potential multicolored text
            #CANNOT CURRENTLY HANDLE MORE THAN ONE PERMISSION TYPE
            student_permissions_cell = QLabel("")
            perm_string = ""

            #Go through each perm and set to right color
            for permission in student["Permissions"]:
                perm_string += '<font color="' +permission+ '">'+"⬤"+'</font>' + ' '
            #Remove the last space
            perm_string = perm_string[:-1]

            student_permissions_cell.setText(perm_string)
            permission_stylesheet = "font-size: 18pt;"
            student_permissions_cell.setStyleSheet(permission_stylesheet)
            student_permissions_cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            self.student_table.setCellWidget(row, 2, student_permissions_cell)

            #Student Count
            if row == 0:
                student_headcount_cell = QTableWidgetItem(str(head_count))
                student_headcount_cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.student_table.setItem(row, 4, student_headcount_cell)


            #Notes
            self.student_table.setItem(row, 3, QTableWidgetItem(student["Notes"]))
            row+=1
        
        #Resize rows and first column to fit images
        self.student_table.resizeRowsToContents()
        self.student_table.resizeColumnToContents(0)



    #*******************************************************************************************
    # Button Functions
    #*******************************************************************************************

    def add_student(self, checked):
        print("Adding Student")
        # Create window for user creation
        self.addWindow = UserCreationWindow()
        self.addWindow.show()


    def edit_student(self):
        print("Editing Student")

    def sign_out(self):
        print("Signing out")