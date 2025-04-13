import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, \
    QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont
import math
from client import *
import os.path


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

        # lazy loading
        # load when gui needs
        self.notes = []

        #Sloppy but WORKS NEVERMIND
        # self.img_label = QLabel().setPixmap

#ADD TIME, affiliation ,RSOs
#     PIC           Time
#     NAME
#     AFFILIATION
#     RSOs
#     PERMISSIONS
class MainWindow(QMainWindow):
    def __init__(self, client_connection):
        super().__init__()
        self.client_connection = client_connection
        self.setWindowTitle("Student Projects Lab accounts")
        # will be set on successful login
        self.attendant_win = 0000
        self.attendant_display_name = ""
        self.attendant_admin_bool = False

        # Style Sheet for default styling options on widgets
        self.setStyleSheet("QTableWidget{font-size: 18pt;} QHeaderView{font-size: 12pt;}")

        # Main layout, the over-arching vertical layout that The button bar and the displayed accounts are apart of
        layout_main = QHBoxLayout()

        # Make GUI Vertical
        self.setMinimumSize(QSize(720, 1280))

        # self.accounts = [{"account Name": "Estlin Mendez","Affiliation": "Creator", "RSOs": "Test", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": "12:30"},
        #          {"account Name": "Clara McGrew", "Affiliation": "Creator", "RSOs": "", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": ""},
        #          {"account Name": "Renee Rickert","Affiliation": "Creator", "RSOs": "", "Permissions": "Red", "Notes": "", "url": "temp.png", "Time": ""},
        #          {"account Name": "Evan Handy","Affiliation": "Creator", "RSOs": "", "Permissions": "Green", "Notes": "", "url": "temp.png", "Time": "" },
        #          {"account Name": "Hunter Hamrick","Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
        #          {"account Name": "Kaden Kramer", "Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
        #          {"account Name": "Ben Crane","Affiliation": "Creator", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""},
        #          {"account Name": "Jerry Sims","Affiliation": "Faux Attendant", "RSOs": "", "Permissions": "Blue", "Notes": "", "url": "temp.png", "Time": ""}]

        self.accounts = []


        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # Table for the Cards
        layout_lab = QHBoxLayout()
        #accounts currently in the lab
        self.lab_table = QTableWidget()

        self.lab_table.verticalHeader().setVisible(False)
        self.lab_table.setStyleSheet("QTableWidget::item:selected {background-color: transparent;}")

        #Bold Headers
        bold_font = QFont()
        bold_font.setBold(True)

        self.lab_table.setColumnCount(5)
        self.lab_table.setHorizontalHeaderLabels(["accounts Present", "", "", "Head Count", str(len(self.accounts) - 1)])

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


        # self.update_photos()


        # timer = QTimer(self)
        # timer.timeout.connect(self.update_table)
        # timer.start(5000)


        widget = QWidget()
        widget.setObjectName("Main")
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

    def account_card(self,account):
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(1, 1,1,1)
        card_layout.setSpacing(1)

        time = QLabel("Time they've been in lab")
        time.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(time)


        #account Image
        img_label = QLabel()
        img_label.setPixmap(QPixmap("./images/default_pic.jpg").scaledToHeight(85))
        img_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        card_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

        #account Name
        account_name = QLabel(account.display_name)
        account_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        account_name.setStyleSheet("font-size: 9pt")
        card_layout.addWidget(account_name)

        #Affiliation
        account_affiliation = QLabel("REPLACE ME WITH account.affiliation")
        account_affiliation.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        account_affiliation.setStyleSheet("font-size: 9pt")
        card_layout.addWidget(account_affiliation)

        #RSOs
        account_rso = QLabel("REPLACE ME WITH account.RSOS")
        account_rso.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        account_rso.setStyleSheet("font-size: 9pt")
        card_layout.addWidget(account_rso)

        #Permissions
        account_permissions = QLabel(f"REPLACE ME WITH account.permissions LIST")
        # TODO: UPDATE BELOW TWO LINES to use account.permissions list
        # permission_stylesheet = f"color: {account['Permissions'].lower()}; font-size: 14pt;"
        permission_stylesheet = f"font-size: 9pt;"
        account_permissions.setStyleSheet(permission_stylesheet)


        account_permissions.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(account_permissions)
        card.setLayout(card_layout)
        return card

    def attendant_card(self, account):
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(1, 1,1,1)
        card_layout.setSpacing(1)

        #Header that marks attendant

        attendant_header = QLabel("Attendant")
        attendant_header.setStyleSheet("font-size: 10pt; font-weight: bold;")
        attendant_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card_layout.addWidget(attendant_header)


        # Attendant Image
        img_label = QLabel()
        img_label.setPixmap(QPixmap("./images/default_pic.jpg").scaledToHeight(85))
        img_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        card_layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignHCenter)
        # Attendant Name
        account_name = QLabel(account.display_name)
        account_name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        account_name.setStyleSheet("font-size: 10pt")
        card_layout.addWidget(account_name)

        # Affiliation
        account_affiliation = QLabel("REPLACE ME WITH account.affiliation")
        account_affiliation.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        account_affiliation.setStyleSheet("font-size: 10pt")
        card_layout.addWidget(account_affiliation)

        card.setMaximumHeight(180)
        card.setLayout(card_layout)
        return card

    def check_if_still_swiped(self):
        res = check_if_active_attendant(self.client_connection, self.attendant_win)
        if res == False:
            # self.widget.setCurrentIndex(2) old from gui.py
            self.attendant_win = 0
            self.attendant_display_name = ''
            self.attendant_admin_bool = False
            return False
        else:
            return True







    def accounts_load_swiped(self):
        print('in acc load swiped')
        print('in acc load swiped')
        print('in acc load swiped')
        print('in acc load swiped')
        # if self.check_if_still_swiped() == False:
        #     return
        print('in acc load swipedAFTER')
        print('in acc load swipedAFTER')
        print('in acc load swipedAFTER')
        print('in acc load swipedAFTER')
        print('in acc load swipedAFTER')
        event_data = {}
                        
        event_data['privilege'] = "ignore"
        event_data['status'] = "swiped_in"
        event_data['affiliation'] = "ignore"
        event_data['name'] = "ignore"
        event_data['text'] = "ignore"
        event_data['text_private'] = "ignore"

        res = get_swiped_in_users(self.client_connection, event_data)
        # self.total_users_in_query = res["total_users"]
        # self.total_users.setText(str(self.total_users_in_query))
        # self.max_page_label.setText(str(math.ceil(self.total_users_in_query / self.items_per_page)))
        for c in res:
            print(c)
            self.accounts.append(Account(c))

    # def update_photos(self):
    #     # account_name_cell = QTableWidgetItem("renee")
    #     # self.lab_table.setItem(0, 1, account_name_cell)
        
    #     # row = 0
    #     # for each acc loaded into the gui
    #     self.accounts_load_swiped()
    #     for acc in self.accounts:
    #         if os.path.isfile(acc.photo_url):
    #             acc.img_label.setPixmap(QPixmap(acc.photo_url).scaledToHeight(85))
    #         else:
    #             acc.img_label.setPixmap(QPixmap("./images/default_pic.jpg").scaledToHeight(85))

    def update_table(self):
        # for each account ordered by role, add to self.accounts based on each dict of data returned.
        self.accounts_load_swiped()
        usercount = len(self.accounts)-1
        self.lab_table.setRowCount(math.ceil(usercount/6))
        self.lab_table.setHorizontalHeaderLabels(["accounts Present", "", "", "Head Count", str(usercount)])
        column = 0
        row = 0
        #Add Account Card to the table on the screen
        attendant = None

        for account in self.accounts:
            if not check_if_active_attendant(client_connection, account.win):
                card = self.account_card(account)
                self.lab_table.setCellWidget(row, column, card)
                self.lab_table.resizeColumnToContents(column)
                column += 1
                #After 5th account move to next row
                if column > 4:
                    column = 0
                    row += 1
                    # Resize columns and rows to fit the content
            else:
                self.attendant_win = account.win
                attendant = account


        attendant_card_widget = self.attendant_card(attendant)
        self.lab_table.setCellWidget(row, 4, attendant_card_widget)
        self.lab_table.resizeColumnsToContents()
        self.lab_table.resizeRowsToContents()


    

def get_swiped_in_users(client, event_data):
    event = Event(EventTypes.GET_SWIPED_IN_USERS, event_data)

    res = client.call_server(event)

    return res

def check_if_active_attendant(client, account_win):
    event = Event(event_type=EventTypes.CHECK_IF_ACTIVE_ATTENDANT, data = {'win': account_win})
    res = client.call_server(event)
    if res['win'] == False:
        return False
    else:
        return True


if __name__ == '__main__':
    client_connection = client_connection('127.0.0.1', 7373)
    lab_gui = QApplication(sys.argv)
    window = MainWindow(client_connection)
    qssfile="./splums/qss/style.qss"
    with open(qssfile,"r") as f:
        lab_gui.setStyleSheet(f.read())
    window.show()
    lab_gui.exec()