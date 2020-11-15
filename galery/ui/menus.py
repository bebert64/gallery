# -*- coding: utf-8 -*-
"""
The context menus used by various part of the apps.

CellMenu : menu used by the CellWidget.

TagMenu: menu used by the TagWidget.
"""
from PySide2 import QtWidgets


class CellMenu(QtWidgets.QMenu):

    """Menu used by the CellWidget. Actions are defined in the object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = self.parent().object
        self.actions = []
        self.add_actions()

    def add_actions(self):
        """Creates and connects the action defined in the object."""
        if hasattr(object, "actions"):
            for name, func in self.object.actions:
                self.actions.append(self.addAction(name).triggered.connect(func))


class TagMenu(QtWidgets.QMenu):

    """Menu used by the TagWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_actions()

    def add_actions(self):
        """Creates and connects the action for the TagWidget."""
        action_1 = self.addAction("Ajouter un tag enfant")
        action_1.triggered.connect(self.action_1)
        action_2 = self.addAction("Test 2")
        action_2.triggered.connect(self.action_2)

    def action_1(self):
        """Dummy action 1"""
        print("action 1")
        print(self.tag_widget.tag.name)

    def action_2(self):
        """Dummy action 2"""
        print("action 2")
        print(self.tag_widget.tag.name)
