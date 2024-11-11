import os
import sys
import threading
import pymssql
import routes
import db_connection_dialog
from flask import Flask

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

db_con_app = QApplication(sys.argv)
db_window = db_connection_dialog.DbConnectionWindow()
db_con_app.exec()

webapp = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("BODE")
layout = QVBoxLayout()

view = QWebEngineView()
layout.addWidget(view)

view.setUrl(QUrl("http://127.0.0.1:35178/index.html"))

window.setLayout(layout)
window.resize(1200, 1200)
window.show()

def start_flask(fapp):
    fapp.run(port=35178)

gui_thread = threading.Thread(target=start_flask, args=(routes.fapp,))
gui_thread.start()

webapp.exec()
os._exit(os.EX_OK)