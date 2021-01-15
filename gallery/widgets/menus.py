# -*- coding: utf-8 -*-

"""
Defines:
 The CellMenu class, the context menu used by cells.

 The TagMenu class, the context menu used by the tag tree.

"""

from __future__ import annotations

from typing import Optional

from PySide6 import QtWidgets

import gallery.models.tags as tag
import gallery.widgets.tag_tree as tag_tree


# The TagMenu class doesn't have public function, but still cleaner to have its
# own class.
class TagMenu(QtWidgets.QMenu):  # pylint: disable=too-few-public-methods

    """Context menu for the TagWidget items."""

    def __init__(
        self,
        parent: tag_tree.TagTreeWidget,
        widget_item: Optional[tag_tree.WidgetItem],
    ):
        super().__init__(parent)
        self._widget_item: Optional[tag_tree.WidgetItem] = widget_item
        self._add_actions()

    def _add_actions(self) -> None:
        self.addAction("Créer un tag").triggered.connect(self._create_widget_item_tag)
        self.addAction("Créer un dossier").triggered.connect(
            self._create_widget_item_tag_folder
        )
        self.addAction("Supprimer un tag").triggered.connect(self._delete_widget_item)

    def _create_widget_item_tag_folder(self) -> None:
        self._create_widget_item("folder")

    def _create_widget_item_tag(self) -> None:
        self._create_widget_item("tag")

    def _create_widget_item(self, tag_type: str) -> None:
        new_tag = self._create_tag(tag_type)
        new_tag.save()
        self._redraw_tag_tree()
        self._start_rename_new_widget_item(new_tag)

    def _redraw_tag_tree(self) -> None:
        self._expand_widget_item()
        self.parent().redraw_tree()

    def _start_rename_new_widget_item(self, new_tag: tag.Tag) -> None:
        new_widget_item = self.parent().widget_items[str(new_tag.id)]
        self.parent().start_rename_tag(new_widget_item)

    def _expand_widget_item(self) -> None:
        if self._widget_item is not None:
            widget_items_expanded = self.parent().widget_items_expanded
            widget_item_id = self._widget_item.widget_item_id
            widget_items_expanded.add(widget_item_id)

    def _create_tag(self, tag_type: str) -> tag.Tag:
        widget_item_tag = self._get_widget_item_tag()
        MyTag = self.parent().config.models.MyTag
        new_tag = MyTag(name="New tag", parent=widget_item_tag, type=tag_type)
        return new_tag

    def _get_widget_item_tag(self) -> Optional[tag.Tag]:
        if self._widget_item is not None:
            widget_item_tag = self._widget_item.tag
        else:
            widget_item_tag = None
        return widget_item_tag

    def _delete_widget_item(self) -> None:
        if self._widget_item is not None:
            self._widget_item.my_delete()
            self.parent().redraw_tree()
