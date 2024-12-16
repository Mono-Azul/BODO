# BODO - A production data explorer
#
# Copyright (C) 2024  Jens Hofer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QMainWindow, QPushButton, QLineEdit, QLabel
    , QMessageBox)
import botec_classes
import user

class DbConnectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DB Connection")
        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.db_serv_label = QLabel("DB Server (maybe with instance)")
        self.db_user_label = QLabel("DB User (maybe with domain)")
        self.db_passw_label = QLabel("DB User's password")
        self.db_db_label = QLabel("IFACE DB Name")

        self.db_server = QLineEdit(user.get_server())
        self.db_user = QLineEdit(user.get_user())
        self.db_password = QLineEdit(user.get_password())
        self.db_db = QLineEdit(user.get_db())

        self.db_server.setMaxLength(300)
        self.db_user.setMaxLength(40)
        self.db_password.setMaxLength(40)
        self.db_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.db_db.setMaxLength(50)

        button = QPushButton("Test and go!")

        layout.addWidget(self.db_serv_label)
        layout.addWidget(self.db_server)
        layout.addWidget(self.db_user_label)
        layout.addWidget(self.db_user)
        layout.addWidget(self.db_passw_label)
        layout.addWidget(self.db_password)
        layout.addWidget(self.db_db_label)
        layout.addWidget(self.db_db)
        layout.addWidget(button)
        button.clicked.connect(self.button_clicked)

        self.show()

    def show_error_dialog(self, ex):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Error")
        dlg.setText(ex)
        button = dlg.exec()

    def button_clicked(self):
        try:
            botec_classes.check_and_connect(self.db_server.text(), self.db_user.text(), self.db_password.text()
                                        , self.db_db.text())
            user.set_server(self.db_server.text())
            user.set_user(self.db_user.text())
            user.set_password(self.db_password.text())
            user.set_db(self.db_db.text())
            self.close()
        except Exception as ex:
            self.show_error_dialog((getattr(ex, 'message', repr(ex))))
