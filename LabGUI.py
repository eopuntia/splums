import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, \
    QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon



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

        #Button Location
        layout_button = QHBoxLayout()
        layout_button.setAlignment(Qt.AlignmentFlag.AlignLeft)

        #Remove Student Button
        self.button_remove = QToolButton(self)
        self.button_remove.setText("Remove Student")
        #ADD ICON?
        #self.button_remove.setIcon()
        self.button_remove.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.button_remove.clicked.connect(self.remove_user)
        layout_button.addWidget(self.button_remove)
        layout_main.addLayout(layout_button)

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Table for the Cards
        layout_lab = QVBoxLayout()
        #Users currently in the lab
        self.lab_table = QTableWidget()

        self.lab_table.verticalHeader().setVisible(False)

        self.lab_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.lab_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.lab_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.lab_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.lab_table.setHorizontalScrollMode(QAbstractItemView.ScrollMode(0))

        self.lab_table.setColumnCount(1)
        self.lab_table.setHorizontalHeaderLabels(["Student Card"])

        self.lab_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.update_table()

        layout_lab.addWidget(self.lab_table)
        layout_lab.setStretch(0,1)

        layout_main.addLayout(layout_lab)
        self.lab_table.resizeRowsToContents()
        self.lab_table.resizeColumnToContents(0)
        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    def user_card(self,user):
        card = QWidget()
        card_layout = QVBoxLayout()

        #Student Image
        user_img = QLabel()
        user_img.setPixmap(QPixmap("./splums/images/default.png").scaledToHeight(85))
        card_layout.addWidget(user_img)
        #Student Name
        user_name = QLabel(user['Student Name'])
        user_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_name.setStyleSheet("font-size: 16pt")
        card_layout.addWidget(user_name)

        #Permissions
        user_permissions = QLabel(f"Permissions: {user['Permissions']}")
        permission_stylesheet = f"color: {user['Permissions'].lower()}; font-size: 14pt;"
        user_permissions.setStyleSheet(permission_stylesheet)
        user_permissions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(user_permissions)

        card.setLayout(card_layout)
        return card

    def update_table(self):
        users = [{"Student Name": "Estlin Mendez", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                {"Student Name": "Clara McGrew", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                {"Student Name": "Renee Rickert", "Permissions": "Red", "Notes": "", "url": "temp.png"},
                {"Student Name": "Evan Hardy", "Permissions": "Green", "Notes": "", "url": "temp.png", },
                {"Student Name": "Hunter Hamrick", "Permissions": "Blue", "Notes": "", "url": "temp.png"},
                {"Student Name": "Kaden Kramer", "Permissions": "Blue", "Notes": "", "url": "temp.png"},
                {"Student Name": "Ben Crane", "Permissions": "Blue", "Notes": "", "url": "temp.png"}]
        self.lab_table.setRowCount(len(users))

        row = 0
        #Add User Card to the table on the screen
        for user in users:
            card = self.user_card(user)
            self.lab_table.setCellWidget(row, 0, card)
            row += 1

    def remove_user(self):
        print("Removing user...")

# Might need to move this into main
splums = QApplication(sys.argv)
splums.setStyle("Breeze")
window = MainWindow()
window.show()
splums.exec()