import sys

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QLCDNumber, QPushButton, QFormLayout, QLineEdit, QGridLayout, QListWidget, QSizePolicy, QInputDialog, QComboBox
from PyQt6.QtCore import Qt, QSize, QRegularExpression
from PyQt6.QtGui import QPixmap, QIcon, QRegularExpressionValidator

class Notes(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        self.setWindowTitle("Notes")
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

class EditStudent(QWidget):
    def __init__(self, student_table):
        super().__init__()
        self.student_table = student_table
        layout = QFormLayout()
        self.setWindowTitle("Edit Student")

        current_student_row = self.student_table.currentRow()
        print(current_student_row)

        student_id_test = self.student_table.item(current_student_row, 4)
        print(student_id_test.text())
        
        
        #Make a Select statement (with SQLAlchemy and event broker?) to find in the database where the student_id is equal to the student_id of the current student
        #Add the relevant fields from the database to the fields below
            
       

 
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
 
       
        # Add fields to the form layout
        layout.addRow("WIN:", self.win_box)
        layout.addRow("Role:", self.role)
        layout.addRow("Display Name:", self.display_name)
        layout.addRow("Given Name:", self.given_name)
        layout.addRow("Last Name:", self.surname)
        layout.addRow("Permissions", self.permissions)
 
        # Create button that opens camera using cam.py
        photo_button = QPushButton("Take Photo")
 
        #Notes button
        notes_button = QPushButton("Notes")
        notes_button.clicked.connect(self.show_notes)

        layout.addWidget(photo_button)
        layout.addWidget(notes_button)
 
        # Set layout for the widget
        self.setLayout(layout)
 
    # def get_photo(self):
    #     # Call cam.py to open the camera and take a picture
    #     self.photo_url = cam.take_picture(self.win_box.text())
    #     print(self.win_box.text())
    #     #self.show_photo()
 
    def show_notes(self):
        self.w = Notes()
        self.w.show()
 
 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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

        self.headcount_display = QLCDNumber(self)
        self.headcount_display.setDigitCount(2)
        layout_headcount.addWidget(self.headcount_display)
        layout_rightbar.addLayout(layout_headcount)
        layout_topsplit.addLayout(layout_rightbar)



        layout_main.addLayout(layout_topsplit)
        self.headcount_display.setFixedSize(QSize(bdim[0]-30, bdim[1]-25))
        self.headcount_display.display(30)

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
        column_labels = [" ", "Student", "Permissions", "Notes", "Head Count"]

        self.student_table.setHorizontalHeaderLabels(column_labels)

        self.update_students()
        


        layout_students.addWidget(self.student_table)


        layout_main.addLayout(layout_students)


        widget = QWidget()
        widget.setObjectName("Main")
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    #*******************************************************************************************
    # Create and Update Student Table
    #*******************************************************************************************

    def update_students(self):
        students = [{"Student Name": "Estlin Mendez", "Permissions": ["Red"], "Notes": [], "url": "temp.png", "Student ID": "252526263"}, 
                    {"Student Name": "Clara McGrew", "Permissions": ["Red", "Blue"], "Notes": ["normal", "discuss", "concern"], "url": "temp.png", "Student ID": "252525263"}, 
                    {"Student Name": "Renee Rickert", "Permissions": ["Red", "Green", "Blue"], "Notes": ["normal", "normal", "discuss", "concern"], "url": "temp.png", "Student ID": "111111111"}, 
                    {"Student Name": "Evan Handy", "Permissions": ["Green"], "Notes": ["normal", "discuss", "concern"], "url": "temp.png", "Student ID": "000000000"}, 
                    {"Student Name": "Hunter Hamrick", "Permissions": ["Blue"], "Notes": "", "url": "temp.png", "Student ID": "222222222"}, 
                    {"Student Name": "Kaden Kramer", "Permissions": ["Blue"], "Notes": ["normal"], "url": "temp.png", "Student ID": "444444444"}, 
                    {"Student Name": "Ben Crane", "Permissions": ["Blue"], "Notes": ["normal", "discuss", "concern", "banned"], "url": "temp.png", "Student ID": "555555555"}]
        head_count = 0
        head_count = len(students)
        self.student_table.setRowCount(head_count)
        self.headcount_display.display(head_count)

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


            #Go through each button for notes
            note_layout = QHBoxLayout()
            for note in student["Notes"]:
                note_button = QPushButton()
                if note == "normal":
                    note_button.setText("🟩")
                elif note == "discuss":
                    note_button.setText("💡")
                elif note == "concern":
                    note_button.setText("❗️")
                elif note == "banned":
                    note_button.setText("🛑")
                else:
                    note_button.setText("Unrecognized note type")
                note_button.setFixedSize(QSize(60, 60))
                note_layout.addWidget(note_button)
            note_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            
            notewidget= QWidget()
            notewidget.setLayout(note_layout)
            self.student_table.setCellWidget(row, 3, notewidget)

                #Student ID
            student_id_hidden =  QTableWidgetItem(student["Student ID"])
            student_id_hidden.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.student_table.setItem(row, 4, student_id_hidden)
            self.student_table.setColumnHidden(4, True)
        

            row+=1
        
        #Resize rows and first column to fit images
        self.student_table.resizeRowsToContents()
        self.student_table.resizeColumnToContents(0)



    #*******************************************************************************************
    # Button Functions
    #*******************************************************************************************

    def add_student(self):
        print("Adding Student")


    def edit_student(self):
        self.w = EditStudent(self.student_table)
        self.w.show()

    def sign_out(self):
        print("Signing out")