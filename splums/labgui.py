import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QTableWidget, \
    QTableWidgetItem, QTableView, QAbstractItemView, QLabel, QHeaderView, QSizePolicy
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont
import math
from client import *
import os.path
from datetime import datetime


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

        self.note = ""
        self.notes = []

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
        self.setWindowTitle("Student Projects Lab Gui")
        self.attendant_display_name = ""

        layout_main = QHBoxLayout()

        self.setMinimumSize(QSize(850, 1000))
        self.accounts = []

        layout_lab = QHBoxLayout()

        self.lab_table = QTableWidget()
        self.lab_table.setColumnCount(5)
        self.lab_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lab_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lab_table.verticalHeader().setVisible(False)
        self.lab_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.lab_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        bold_font = QFont()
        bold_font.setBold(True)
        self.lab_table.horizontalHeader().setFont(bold_font)

        layout_lab.addWidget(self.lab_table)

        layout_main.addLayout(layout_lab)
        self.lab_table.resizeRowsToContents()
        self.lab_table.resizeColumnsToContents()

        # self.update_photos()

        # timer = QTimer(self)
        # timer.timeout.connect(self.update_table)
        # timer.start(5000)

        widget = QWidget()
        widget.setLayout(layout_main)
        self.setCentralWidget(widget)

        self.update_table()

    def account_card(self,account):
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(1, 1,1,1)
        card_layout.setSpacing(1)

        print(account.last_access)
        time_diff = datetime.now() - account.last_access

        total_seconds = time_diff.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        time = QLabel("Time in lab: " + f"{hours:02d}:{minutes:02d}")
        time.setAlignment(Qt.AlignmentFlag.AlignRight)
        card_layout.addWidget(time)

        #account Image
        img_label = QLabel()
        img_label.setPixmap(QPixmap(account.photo_url).scaledToHeight(85))
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
        img_label.setPixmap(QPixmap(account.photo_url).scaledToHeight(85))
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

    def accounts_load_swiped(self):
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
        self.lab_table.setHorizontalHeaderLabels(["Accounts Present", "", "", "Head Count", str(usercount)])
        column = 0
        row = 0
        #Add Account Card to the table on the screen
        attendant = None

        for account in self.accounts:
            card = self.account_card(account)
            self.lab_table.setCellWidget(row, column, card)
            self.lab_table.resizeColumnToContents(column)
            column += 1
            #After 5th account move to next row
            if column > 4:
                column = 0
                row += 1

        active_attendant = get_active_attendant(self.client_connection)
        if active_attendant is not None:
            self.attendant_win = active_attendant['win']
            attendant = Account(get_account(self.client_connection, self.attendant_win))
        else:
            self.attendant_win = 'N/A'
            no_attendant = {
                'win' : '0000',
                'display_name' : 'ATTENDANT MISSING',
                'given_name' : 'n/a',
                'surname' : 'n/a',
                'photo_url' : './images/missing_attendant.jpg',
                'role' : 'attendant',
                'affiliation' : 'other',
                'rso' : 'n/a',
                'created_at' : 'n/a',
                'last_updated_at' : 'n/a',
                'swiped_in' : False,
                'last_access' : 'n/a',
            }
            attendant = Account(no_attendant)

        attendant_card_widget = self.attendant_card(attendant)
        self.lab_table.setCellWidget(row, 4, attendant_card_widget)

        self.lab_table.resizeColumnsToContents()
        self.lab_table.resizeRowsToContents()

def get_account(client, account_win):
    event = Event(EventTypes.GET_USER, data = {'win': account_win})
    res = client.call_server(event)
    return res

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

def get_active_attendant(client):
    event = Event(event_type=EventTypes.GET_ACTIVE_ATTENDANT, data = {})
    res = client.call_server(event)
    return res

if __name__ == '__main__':
    client_connection = client_connection('127.0.0.1', 7373)
    lab_gui = QApplication(sys.argv)
    window = MainWindow(client_connection)
    qssfile="./splums/qss/style.qss"
    with open(qssfile,"r") as f:
        lab_gui.setStyleSheet(f.read())
    window.show()
    lab_gui.exec()
