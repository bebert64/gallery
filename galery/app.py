#!  galery
# -*- coding: utf-8 -*-
"""
Launches the app.
"""

# TODO: find a way to properly remove the warning message from Qt during launch
# import os
# os.environ["QT_API"] = "pyside2"
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
    # FIXME : app is added to config to get access in GridWidgetContainer.repaint
    # to close windows that should not be opened in the first place. When that bug is
    # corrected, we can delete the following 2 lines
    from config.config import config  # pylint: disable=import-outside-toplevel

    config.app = app
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
