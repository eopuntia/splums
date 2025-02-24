import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, \
    QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont
import math



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

        self.users = [{"User Name": "Estlin Mendez", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                 {"User Name": "Clara McGrew", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                 {"User Name": "Renee Rickert", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                 {"User Name": "Evan Hardy", "Permissions": "Green", "Notes": "", "url": "temp.png", },
                 {"User Name": "Hunter Hamrick", "Permissions": "Blue", "Notes": "", "url": "temp.png"},
                 {"User Name": "Kaden Kramer", "Permissions": "Blue", "Notes": "", "url": "temp.png"},
                 {"User Name": "Ben Crane", "Permissions": "Blue", "Notes": "", "url": "temp.png"},
                 {"User Name": "Jerry Sims", "Permissions": "Blue", "Notes": "", "url": "temp.png"}]




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

        self.lab_table.setColumnCount(6)
        self.lab_table.setHorizontalHeaderLabels(["Users Present", "", "", "", "Head Count", str(len(self.users))])

        header = self.lab_table.horizontalHeader()
        header.setFont(bold_font)

        self.lab_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_table()
        #Allow Window Resizing
        self.lab_table.horizontalHeader().setStretchLastSection(True)
        #Allow all column to stretch
        for col in range(self.lab_table.columnCount()):
            self.lab_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        #Disable Editing
        self.lab_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.lab_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lab_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout_lab.addWidget(self.lab_table)
        layout_lab.setStretch(0,1)
        #Attendant card in the bottom right
        attendant_layout = QVBoxLayout()
        attendant_card = self.attendant_card(self.users[-1])
        attendant_layout.addWidget(attendant_card)

        layout_attendant =QHBoxLayout()
        layout_attendant.addLayout(layout_lab)
        layout_attendant.addLayout(attendant_layout)

        layout_main.addLayout(layout_attendant)
        self.lab_table.resizeRowsToContents()
        self.lab_table.resizeColumnsToContents()

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    def user_card(self,user):
        card = QWidget()
        card_layout = QVBoxLayout()

        #User Image
        user_img = QLabel()
        user_img.setPixmap(QPixmap("./splums/images/default.png").scaledToHeight(85))
        card_layout.addWidget(user_img)
        #User Name
        user_name = QLabel(user['User Name'])
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_name.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_name)

        #Permissions
        user_permissions = QLabel(f"{user['Permissions']}")
        permission_stylesheet = f"color: {user['Permissions'].lower()}; font-size: 14pt;"
        user_permissions.setStyleSheet(permission_stylesheet)
        user_permissions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(user_permissions)

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

        card.setLayout(card_layout)
        return card

    def update_table(self):
        self.lab_table.setRowCount(math.ceil(len(self.users)/6))

        column = 0
        row = 0
        #Add User Card to the table on the screen
        for user in self.users:
            card = self.user_card(user)
            self.lab_table.setCellWidget(row, column, card)
            self.lab_table.resizeColumnToContents(column)
            column += 1
            #After 6th user move to next row
            if column > 5:
                column = 0
                row += 1
                # Resize columns and rows to fit the content
        self.lab_table.resizeColumnsToContents()
        self.lab_table.resizeRowsToContents()

# Might need to move this into main
splums = QApplication(sys.argv)
splums.setStyle("Breeze")
window = MainWindow()
window.show()
splums.exec()