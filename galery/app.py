#!  galery
# -*- coding: utf-8 -*-
"""
Launches the app.
"""


import sys
from PySide2 import QtWidgets
import qdarkstyle
from ui.main_window import MyMainWindow


def main():
    """Creates and launches the app."""
    app = QtWidgets.QApplication(sys.argv)
    window = MyMainWindow.create_widget(parent=None)
    window.show()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    from config.config import config

    config.app = app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
