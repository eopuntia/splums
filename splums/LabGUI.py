import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, \
    QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont
import math


#ADD TIME, affiliation ,RSOs
#     PIC           Time
#     NAME
#     AFFILIATION
#     RSOs
#     PERMISSIONS
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Projects Lab Users")

        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        # Main layout, the over-arching vertical layout that The button bar and the displayed users are apart of
        layout_main = QVBoxLayout()

        # Make GUI Vertical
        self.setMinimumSize(QSize(720, 1280))

        self.users = [{"User Name": "Estlin Mendez","Affiliation": "Creator", "RSOs": "Test", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": "12:30"},
                 {"User Name": "Clara McGrew", "Affiliation": "Creator", "RSOs": "", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": ""},
                 {"User Name": "Renee Rickert","Affiliation": "Creator", "RSOs": "", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": ""},
                 {"User Name": "Evan Handy","Affiliation": "Creator", "RSOs": "", "Permissions": "Green", "Notes": "", "url": "temp.png", "Time": "" },
                 {"User Name": "Hunter Hamrick","Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
                 {"User Name": "Kaden Kramer", "Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
                 {"User Name": "Ben Crane","Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
                 {"User Name": "Jerry Sims","Affiliation": "Faux Attendant", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""}]




        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Table for the Cards
        layout_lab = QHBoxLayout()
        #Users currently in the lab
        self.lab_table = QTableWidget()

        self.lab_table.verticalHeader().setVisible(False)
        self.lab_table.setStyleSheet("QTableWidget::item:selected {background-color: transparent;}")

        #Bold Headers
        bold_font = QFont()
        bold_font.setBold(True)

        self.lab_table.setColumnCount(5)
        self.lab_table.setHorizontalHeaderLabels(["Users Present", "", "", "Head Count", str(len(self.users) - 1)])

        header = self.lab_table.horizontalHeader()
        header.setFont(bold_font)

        self.lab_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_table()
        #Allow Window Resizing
        self.lab_table.horizontalHeader().setStretchLastSection(True)
        #Allow all columns to stretch
        for col in range(self.lab_table.columnCount()):
            self.lab_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        #Disable Editing
        self.lab_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.lab_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lab_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout_lab.addWidget(self.lab_table)
        layout_lab.setStretch(0,1)


        layout_main.addLayout(layout_lab)
        self.lab_table.resizeRowsToContents()
        self.lab_table.resizeColumnsToContents()

        widget = QWidget()
        widget.setObjectName("Main")
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    def user_card(self,user):
        card = QWidget()
        card_layout = QVBoxLayout()

        #TimeLayout
        time_layout =QHBoxLayout()
        #Time Swiped In
        time = QLabel((user['Time']))
        time.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_layout.addWidget(time)

        #User Image
        user_img = QLabel()
        user_img.setPixmap(QPixmap("./images/").scaledToHeight(85))
        card_layout.addWidget(user_img)

        #User Name
        user_name = QLabel(user['User Name'])
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_name.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_name)

        #Affiliation
        user_affiliation = QLabel(user['Affiliation'])
        user_affiliation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_affiliation.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_affiliation)

        #RSOs
        user_rso = QLabel(user['RSOs'])
        user_rso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_rso.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_rso)

        #Permissions
        user_permissions = QLabel(f"{user['Permissions']}")
        permission_stylesheet = f"color: {user['Permissions'].lower()}; font-size: 14pt;"
        user_permissions.setStyleSheet(permission_stylesheet)
        user_permissions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(user_permissions)
        #Add time to top of card
        card_layout.insertLayout(0, time_layout)
        card.setLayout(card_layout)
        return card

    def attendant_card(self, user):
        card = QWidget()
        card_layout = QVBoxLayout()

        # Attendant Image
        user_img = QLabel()
        user_img.setPixmap(QPixmap("./splums/images/default.png").scaledToHeight(85))
        card_layout.addWidget(user_img)
        # Attendant Name
        user_name = QLabel(user['User Name'])
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_name.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_name)

        # Affiliation
        user_affiliation = QLabel(user['Affiliation'])
        user_affiliation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_affiliation.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_affiliation)

        card.setMaximumHeight(180)
        card.setLayout(card_layout)
        return card

    def update_table(self):
        non_attendant = self.users[:-1]
        self.lab_table.setRowCount(math.ceil(len(non_attendant)/6))

        column = 0
        row = 0
        #Add User Card to the table on the screen
        for user in non_attendant:
            card = self.user_card(user)
            self.lab_table.setCellWidget(row, column, card)
            self.lab_table.resizeColumnToContents(column)
            column += 1
            #After 5th user move to next row
            if column > 4:
                column = 0
                row += 1

        attendant_card_widget = self.attendant_card(self.users[-1])
        self.lab_table.setCellWidget(row, 4, attendant_card_widget)


        # Resize columns and rows to fit the content
        self.lab_table.resizeColumnsToContents()
        self.lab_table.resizeRowsToContents()


if __name__ == '__main__':
    lab_gui = QApplication(sys.argv)
    window = MainWindow()
    qssfile="./splums/qss/style.qss"
    with open(qssfile,"r") as f:
        lab_gui.setStyleSheet(f.read())
    window.show()
    lab_gui.exec()
