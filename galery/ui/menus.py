# -*- coding: utf-8 -*-
"""
The context menus used by various part of the apps.

CellMenu : menu used by the CellWidget.

TagMenu: menu used by the TagWidget.
"""
from PySide2 import QtWidgets
from models.tags import Tag


class CellMenu(QtWidgets.QMenu):

    """Menu used by the CellWidget. Actions are defined in the object."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = self.parent().object
        self.actions = []
        self.add_actions()

    def add_actions(self):
        """Creates and connects the action defined in the object."""
        if hasattr(self.object, "actions"):
            for name, func in self.object.actions:
                self.addAction(name).triggered.connect(func)


class TagMenu(QtWidgets.QMenu):

    """Menu used by the TagWidget."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_actions()

    def add_actions(self):
        """Creates and connects the action for the TagWidget."""
        action_1 = self.addAction("Créer un tag")
        action_1.triggered.connect(self.create_tag)
        action_2 = self.addAction("Test 2")
        action_2.triggered.connect(self.action_2)

    def create_tag(self):
        """Creates a new tag and open its name's edition"""
        new_tag = Tag(
            # id = AutoField(),
            name="New tag",
            parent=None,
            type="tag",
        )
        new_tag.save()
        self.parent().rename_tag(self.tag_widget)
        print("action 1")
        print(self.tag_widget.tag.name)

    def action_2(self):
        """Dummy action 2"""
        print("action 2")
        print(self.tag_widget.tag.name)
