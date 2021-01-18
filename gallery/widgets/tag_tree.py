# -*- coding: utf-8 -*-
"""
Defines :
 The TagTreeWidget class, and its associated TagTreeWidgetSignals.

 The WidgetItem base class for all tag tree widget items.

 The WidgetItemTagBase base class for tag related widget items, and its two derived
 classes WidgetItemTag and WidgetItemTagFolder

 The special WidgetItemAll, representing all objects in the database.

 The WidgetItemView, a view corresponding to a specific set of query parameters.

 The WidgetItemRating, corresponding to objects with that rating.

 TheWidgetItemFolder, a basic folder, used to organise widget items in the tree.

"""


from __future__ import annotations

import time
from typing import List, Set, Dict, Optional, Type

from PySide6 import QtWidgets, QtGui, QtCore

import gallery.types as types
import gallery.widgets.drag as drag
import gallery.widgets.main_widget as main_widget
from gallery.config.config import Config
from gallery.models.tags import Tag
from gallery.models.views import View
from gallery.widgets import icons
from gallery.widgets.menus import TagMenu
from gallery.widgets.my_custom_widget import MyCustomWidget
from gallery.widgets.query import QueryParameters


class WidgetItem(QtWidgets.QTreeWidgetItem):

    """
    A widget item of the tag tree.

    The class provides several static convenience methods to help create items
    corresponding to different roles (tag, view, folder...). All items can accept
    drops (via handle_drop_on_self) and/or be droppable (via get_objects), and must
    implement the corresponding methods only if necessary.
    Widget items can also define a rename method, in which case a double click on
    themselves will start the renaming process.

    Instance Attributes
    -------------------
    widget_item_id
    name
    config
    accepts_drop
    is_droppable

    """

    def __init__(self, parent: types.WidgetItemParent) -> None:
        super().__init__(parent)
        self.widget_item_id: types.WidgetItemId
        self.name: str = ""
        self.config: Config = parent.config

    def _set_name(self, name: str) -> None:
        self.name = name
        self.setText(0, name)

    def _set_icon(self, icon_name: str) -> None:
        icon = icons.get_icon(icon_name)
        self.setIcon(0, icon)

    @property
    def is_droppable(self) -> bool:
        """Whether the widget item can be dropped on the grid."""
        is_droppable = hasattr(self, "get_my_objects")
        return is_droppable

    @property
    def accepts_drop(self) -> bool:
        """Whether the widget item accepts a drop from the grid."""
        accepts_drop = hasattr(self, "handle_drop_on_self")
        return accepts_drop


class WidgetItemTagBase(WidgetItem):

    """
    Base class for tag tree widget items based on a tag (either a "real" tag or a
    folder).

    Parameters
    ----------
    parent
    tag

    """

    def __init__(self, parent: types.WidgetItemParent, tag: Tag) -> None:
        super().__init__(parent)
        self.tag = tag
        self.widget_item_id = str(tag.id)
        self._set_name(tag.name)

    def get_my_objects(self) -> types.MyObjectSet:
        """Gets the objects tagged with the widget item tag."""
        my_objects = self.tag.get_my_objects_with_descendants()
        return my_objects

    def rename(self, name: str) -> None:
        """
        Renames the widget item and its tag.

        Parameters
        ----------
        name

        """
        self.name = name
        self.tag.name = name
        self.tag.save()

    def my_delete(self) -> None:
        """Deletes the widget item, as well as its tag and all its descendants."""
        self.tag.delete_self_and_children()
        self._remove_from_widget_items_expanded()

    def _remove_from_widget_items_expanded(self) -> None:
        tag_tree = self.treeWidget()
        widget_items_expanded = tag_tree.widget_items_expanded
        if self.widget_item_id in widget_items_expanded:
            widget_items_expanded.remove(self.widget_item_id)


class WidgetItemTag(WidgetItemTagBase):

    """
    Widget item base on a "real" tag.

    The widget item accepts drops and is droppable. When being dropped, the objects
    associated to the item are the one tagged with its tag and one of its descendants.
    When an object is dropped on it, it will tag it with its tag.

    """

    def handle_drop_on_self(self, my_object_id: types.MyObjectId, remove: bool) -> None:
        """
        Adds or removes a tag from the my_object with the id my_object_id.

        Whether the tag is added or removed is based on whether the Shift key is
        being pressed at the moment of the drop.

        Parameters
        ----------
        my_object_id
        remove

        """
        if remove:
            self._remove_tag(my_object_id)
        else:
            self._add_tag(my_object_id)

    def _add_tag(self, my_object_id: types.MyObjectId) -> None:
        self.config.models.MyObjectTag.get_or_create(my_object=my_object_id, tag=self.tag.id)

    def _remove_tag(self, my_object_id: types.MyObjectId) -> None:
        self.config.models.MyObjectTag.get(
            my_object=my_object_id, tag=self.tag.id
        ).delete_instance()


class WidgetItemTagFolder(WidgetItemTagBase):

    """
    Widget item base on a "folder" tag.

    The widget item is droppable but doesn't accept drop itself.

    """

    def __init__(self, parent: types.WidgetItemParent, tag: Tag) -> None:
        super().__init__(parent, tag)
        self._set_icon("folder")


class WidgetItemRating(WidgetItem):

    """
    Widget item based on a rating, if the MyObject model has such a field.

    The item accepts drops and is droppable. When being dropped, the objects
    associated to the item are the one rated with its rating. When an object is
    dropped on it, it will rate it with its rating.

    Parameters
    ----------
    parent
    rating

    """

    def __init__(self, parent: types.WidgetItemParent, rating: int) -> None:
        super().__init__(parent)
        self.widget_item_id = f"rating_{rating}"
        self.rating = rating
        self._set_name_from_rating(rating)

    def _set_name_from_rating(self, rating: int) -> None:
        name = self._get_name_from_rating(rating)
        self._set_name(name)

    @staticmethod
    def _get_name_from_rating(rating: int) -> str:
        name = WidgetItemRating._get_base_name_from_rating(rating)
        name = WidgetItemRating._add_s_to_plural(name, rating)
        return name

    @staticmethod
    def _get_base_name_from_rating(rating: int) -> str:
        if rating == 0:
            name = "Non noté"
        else:
            name = f"{rating} étoile"
        return name

    @staticmethod
    def _add_s_to_plural(name: str, rating: int) -> str:
        if rating > 1:
            name += "s"
        return name

    def get_my_objects(self) -> types.MyObjectSet:
        """Gets all objects rated with its rating."""
        my_objects = set(
            self.config.models.MyObject.select().where(
                self.config.models.MyObject.rating == self.rating
            )
        )
        return my_objects

    def handle_drop_on_self(
        self, object_id: types.MyObjectId, unused_remove: bool
    ) -> None:
        """
        Rates the my_object with its rating.

        The remove parameter is not used. To "unrate" a my_object, it must instead be
        dropped on the widget item corresponding to the rating 0.

        """
        my_object = self.config.models.MyObject.get(id=object_id)
        my_object.rating = self.rating
        my_object.save()


class WidgetItemAll(WidgetItem):

    """
    Widget item associated with all objects in the database.

    The item is droppable but it does not accept drops. When being dropped, the
    objects associated to the item are the whole collections of objects in the
    database.

    Parameters
    ----------
    parent

    """

    def __init__(self, parent: types.WidgetItemParent) -> None:
        super().__init__(parent)
        self.widget_item_id = "all"
        self._set_name("Tout")

    def get_my_objects(self) -> types.MyObjectSet:
        """Gets all objects from the database."""
        my_objects = set(self.config.models.MyObject.select())
        return my_objects


class WidgetItemView(WidgetItem):
    """
    Widget item associated with a view.

    The item is droppable but it does not accept drops. When being dropped, the
    objects associated to the item are the ones corresponding to the view's query
    parameters.

    Parameters
    ----------
    parent
    view

    """

    def __init__(self, parent: types.WidgetItemParent, view: View) -> None:
        super().__init__(parent)
        self.view = view
        self.widget_item_id = self.get_id(view)
        self._query_parameters: QueryParameters
        self._set_name(view.name)

    def _create_query_parameters(self) -> QueryParameters:
        # my_main_widget = self._get_main_widget()
        tag_tree_widget = self.treeWidget()
        query_string = self.view.query_string
        query_parameters = QueryParameters.create_from_string(
            query_string, tag_tree_widget
        )
        return query_parameters

    def _get_main_widget(self) -> main_widget.MainWidget:
        tag_tree = self.treeWidget()
        my_main_widget = tag_tree.get_main_widget()
        return my_main_widget

    def _get_query_parameters(self) -> QueryParameters:
        if not hasattr(self, "_query_parameters"):
            self._set_query_parameters()
        return self._query_parameters

    def _set_query_parameters(self) -> None:
        query_parameters = self._create_query_parameters()
        query_parameters.refresh_my_objects()
        self._query_parameters = query_parameters

    def get_my_objects(self) -> types.MyObjectSet:
        """Gets objects associated with the view's query parameters."""
        query_parameters = self._get_query_parameters()
        my_objects = query_parameters.my_objects
        return my_objects

    def rename(self, name: str) -> None:
        """Rename the view."""
        self.name = name
        self.view.name = name
        self.view.save()

    @staticmethod
    def get_id(view: View) -> str:
        """The view's id is view_{view.id}."""
        return f"view_{view.id}"

    def my_delete(self):
        """Deletes the view."""
        self.view.delete_instance()


class WidgetItemFolder(WidgetItem):
    """
    Creates and returns a widget item representing a folder.

    The item is neither droppable nor can it accept drops.

    Parameters
    ----------
    parent
    name

    """

    def __init__(self, parent: types.WidgetItemParent, name: str) -> None:
        super().__init__(parent)
        self.widget_item_id: types.WidgetItemId = f"folder_{name}"
        self._set_name(name)
        self._set_icon("folder")


# The QTreeWidget already have 7 ancestors itself, but not subclassing it is not an
# option here...
class TagTreeWidget(
    QtWidgets.QTreeWidget, MyCustomWidget
):  # pylint: disable = too-many-ancestors
    """
    The TagTreeWidget holds the tag's tree, as well as some special additional items.

    The special element added are a first tag allowing to select all instance of
    MyObject. If MyObject has a rating attribute, then a folder is also created holding
    widget items for rating from 1 to 5, with 0 being assimilated to unrated tags.

    Attributes
    ----------
    widget_items
    widget_items_expanded

    """

    _brushes: Dict[str, QtGui.QBrush] = {}
    _widget_item_class_from_type: Dict[str, Type[WidgetItem]] = {
        "tag": WidgetItemTag,
        "folder": WidgetItemTagFolder,
    }

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self._timer_click: float = 0
        self._tag_widget_hovered: Optional[WidgetItem] = None
        self._tag_widget_being_edited: Optional[WidgetItem] = None
        self.widget_items: Dict[types.WidgetItemId, WidgetItem] = {}
        """A dictionary mapping widget_item_id to their corresponding WidgetItem."""

        self.widget_items_expanded: Set[types.WidgetItemId] = set()
        """A list of the widget items being expanded.."""

        self.signals: TagTreeWidgetSignals = TagTreeWidgetSignals()

    @classmethod
    def create_tag_tree_widget(cls, parent) -> TagTreeWidget:
        """
        Factory method to create tag tree widgets.

        Parameters
        ----------
        parent

        """
        # create_tag_tree_widget is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        tag_tree_widget = cls.create_widget(parent)
        assert isinstance(tag_tree_widget, cls)
        tag_tree_widget.redraw_tree()
        tag_tree_widget._init_brushes()
        tag_tree_widget._connect_events()
        return tag_tree_widget

    def _init_brushes(self):
        self._brushes["background_color"] = self.palette().base()
        widget_hovered_background_color = QtGui.QColor(
            self.config.hovered_background_color
        )
        self._brushes["widget_hovered"] = QtGui.QBrush(widget_hovered_background_color)

    def _connect_events(self) -> None:
        # pylint: disable = no-member
        self.itemDoubleClicked.connect(self.start_rename_tag)
        self.itemExpanded.connect(self._handle_tag_widget_expanded)
        self.itemCollapsed.connect(self._handle_tag_widget_collapsed)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        is_changed_background_color = (
            self._brushes["background_color"] != self.palette().base()
        )
        if is_changed_background_color:
            self._handle_background_color_change()
        super().paintEvent(event)

    def _handle_background_color_change(self) -> None:
        self._brushes["background_color"] = self.palette().base()
        self._apply_new_background_color()

    def _apply_new_background_color(self) -> None:
        for widget_item in self.widget_items.values():
            widget_item.setBackground(0, self._brushes["background_color"])

    def _handle_tag_widget_expanded(self, item: WidgetItem) -> None:
        self.widget_items_expanded.add(item.widget_item_id)

    def _handle_tag_widget_collapsed(self, item: WidgetItem) -> None:
        self.widget_items_expanded.remove(item.widget_item_id)

    def _add_to_widget_items_dict(self, widget_item: WidgetItem) -> None:
        self.widget_items[widget_item.widget_item_id] = widget_item

    def redraw_tree(self) -> None:
        """Clears and redraws the tag tree."""
        self.clear()
        self._tag_widget_hovered = None
        self._create_tag_tree()

    def clear(self):
        super().clear()
        self.widget_items = {}

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        tag_hovered = self.itemAt(event.pos())
        menu = TagMenu(self, tag_hovered)
        menu_position = event.pos()
        self._open_context_menu(menu, menu_position)

    def _open_context_menu(self, menu: TagMenu, menu_position: QtCore.QPoint) -> None:
        menu.exec_(self.mapToGlobal(menu_position))

    def _create_tag_tree(self) -> None:
        # The structure is : all / tags / views / ratings
        self._add_widget_item_all()
        self._add_widget_items_tag(self)
        self._add_widget_items_view()
        self._add_widget_items_rating()
        self._expand_widget_items()

    def _expand_widget_items(self) -> None:
        for widget_item_id in self.widget_items_expanded:
            widget_item = self.widget_items[widget_item_id]
            widget_item.setExpanded(True)

    def _add_widget_item_all(self) -> None:
        widget_item_all = WidgetItemAll(self)
        self._add_to_widget_items_dict(widget_item_all)

    def _add_widget_items_tag(self, parent: types.WidgetItemParent) -> None:
        tags = self._get_tags_from_parent(parent)
        for tag in tags:
            widget_item_class = self._widget_item_class_from_type[tag.type]
            self._add_widget_item_tag_by_type(parent, tag, widget_item_class)

    def _add_widget_item_tag_by_type(
        self,
        parent: types.WidgetItemParent,
        tag: Tag,
        widget_item_class: Type[WidgetItemTagBase],
    ) -> None:
        widget_item_tag = widget_item_class(parent, tag)
        self._add_to_widget_items_dict(widget_item_tag)
        self._add_widget_items_tag(widget_item_tag)

    def _get_tags_from_parent(self, parent: types.WidgetItemParent) -> List[Tag]:
        if isinstance(parent, WidgetItemTagBase):
            tags = self._get_tags_from_widget_item_tag(parent)
        else:
            tags = self._get_tags_at_root()
        return tags

    def _get_tags_from_widget_item_tag(
        self, widget_item_tag: WidgetItemTagBase
    ) -> List[Tag]:
        children = widget_item_tag.tag.children
        tags_ordered_alphabetically = children.order_by(self.config.models.MyTag.name)
        return tags_ordered_alphabetically

    def _get_tags_at_root(self) -> List[Tag]:
        tags = self.config.models.MyTag.select().where(self.config.models.MyTag.parent_id.is_null())
        return tags

    def _add_widget_items_rating(self) -> None:
        need_widget_items_rating = hasattr(self.config.models.MyObject, "rating")
        if need_widget_items_rating:
            rating_folder_widget = self._create_folder("Ratings")
            self._add_widget_items_rating_to_folder(rating_folder_widget)

    def _add_widget_items_rating_to_folder(
        self, rating_folder_widget: WidgetItemFolder,
    ) -> None:
        for i in range(5, -1, -1):
            rating_item = WidgetItemRating(rating_folder_widget, i)
            self._add_to_widget_items_dict(rating_item)

    def _create_folder(self, name: str) -> WidgetItemFolder:
        rating_folder_widget = WidgetItemFolder(self, name)
        self._add_to_widget_items_dict(rating_folder_widget)
        return rating_folder_widget

    def _add_widget_items_view(self) -> None:
        views_folder = self._create_folder("Views")
        self._add_widget_items_view_to_folder(views_folder)

    def _add_widget_items_view_to_folder(self, views_folder: WidgetItemFolder) -> None:
        for view in self.config.models.MyView.select():
            tag_widget_view = WidgetItemView(views_folder, view)
            self.widget_items[tag_widget_view.widget_item_id] = tag_widget_view

    def _handle_widget_hovered_change(self, event: QtGui.QDragMoveEvent) -> None:
        hovered_position = event.pos()
        has_widget_hovered_changed = self._has_widget_hovered_changed(hovered_position)
        if has_widget_hovered_changed:
            self._handle_widget_hovered_changed(hovered_position)

    def startDrag(self, _: QtCore.Qt.DropActions) -> None:
        drag_object = drag.DragFromTree(self)
        drag_object.exec_()

    def _has_widget_hovered_changed(self, hovered_position: QtCore.QPoint) -> bool:
        old_id = self._get_old_hovered_id()
        new_id = self._get_new_hovered_id(hovered_position)
        return old_id != new_id

    def _get_new_hovered_id(
        self, hovered_position: QtCore.QPoint
    ) -> Optional[types.WidgetItemId]:
        new_widget_hovered = self.itemAt(hovered_position)
        new_id = self._get_id_from_widget_item(new_widget_hovered)
        return new_id

    def _get_old_hovered_id(self) -> Optional[types.WidgetItemId]:
        old_widget_hovered = self._tag_widget_hovered
        old_hovered_id = self._get_id_from_widget_item(old_widget_hovered)
        return old_hovered_id

    def _handle_widget_hovered_changed(self, hovered_position: QtCore.QPoint) -> None:
        self._handle_old_widget_hovered_changed()
        new_widget_hovered = self.itemAt(hovered_position)
        self._handle_new_widget_hovered_changed(new_widget_hovered)
        self._tag_widget_hovered = new_widget_hovered

    def _handle_new_widget_hovered_changed(
        self, new_widget_hovered: Optional[WidgetItem]
    ) -> None:
        if new_widget_hovered is not None:
            new_widget_hovered.setBackground(0, self._brushes["widget_hovered"])

    def _handle_old_widget_hovered_changed(self) -> None:
        old_widget_hovered = self._tag_widget_hovered
        if old_widget_hovered is not None:
            old_widget_hovered.setBackground(0, self._brushes["background_color"])

    @staticmethod
    def _get_id_from_widget_item(
        widget_item: Optional[WidgetItem],
    ) -> Optional[types.WidgetItemId]:
        if widget_item is None:
            widget_item_id = None
        else:
            widget_item_id = widget_item.widget_item_id
        return widget_item_id

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        drag_object = self._get_drag_object()
        assert drag_object is not None
        drag_object.handle_move_on_tree(event)
        self._handle_widget_hovered_change(event)

    def dragEnterEvent(  # pylint: disable=no-self-use
        self, event: QtGui.QDragEnterEvent
    ) -> None:
        event.accept()

    def dropEvent(self, _: QtGui.QDropEvent) -> None:
        if self._tag_widget_hovered is not None:
            drag_object = self._get_drag_object()
            assert drag_object is not None
            drag_object.handle_drop_on_tree(self._tag_widget_hovered)
            self._set_default_background(self._tag_widget_hovered)

    def _set_default_background(self, tag_widget):
        tag_widget.setBackground(0, self._brushes["background_color"])

    def start_rename_tag(self, tag_widget: WidgetItem) -> None:
        """
        Starts the process of renaming a tag.

        The actual renaming of the tag (update of the database) takes place within
        the handle_simple_click method, when we click out of the tag being renamed.

        Parameters
        ----------
        tag_widget

        """
        if hasattr(tag_widget, "rename"):
            self._tag_widget_being_edited = tag_widget
            self.openPersistentEditor(tag_widget)

    def mouseReleaseEvent(self, _: QtGui.QMouseEvent) -> None:
        """
        Checks the time since the last click, and starts the simple click handler
        if appropriate.
        """
        is_simple_click = self._is_simple_click()
        if is_simple_click:
            self._handle_simple_click()
        self._reset_timer_click()

    def _is_simple_click(self) -> bool:
        is_double_click = self._is_double_click()
        is_simple_click = not is_double_click
        return is_simple_click

    def _is_double_click(self) -> bool:
        now = time.time()
        time_since_last_click = now - self._timer_click
        is_double_click = time_since_last_click <= self.config.double_click_time_limit
        return is_double_click

    def _reset_timer_click(self) -> None:
        self._timer_click = time.time()

    def _handle_simple_click(self) -> None:
        if self._tag_widget_being_edited is not None:
            if self.isPersistentEditorOpen(self._tag_widget_being_edited):
                self.closePersistentEditor(self._tag_widget_being_edited)
                self._finish_rename_tag()

    def _finish_rename_tag(self) -> None:
        try:
            assert isinstance(self._tag_widget_being_edited, WidgetItem)
        except AssertionError:
            pass
        else:
            new_name = self._tag_widget_being_edited.text(0)
            self._tag_widget_being_edited.rename(new_name)

    def get_main_widget(self):
        """Gets the main widget."""
        return self.get_ancestor_by_class(main_widget.MainWidget)

    def _get_drag_object(self) -> drag.MyDrag:
        my_main_widget = self.get_main_widget()
        drag_object = my_main_widget.drag_object
        return drag_object


class TagTreeWidgetSignals(QtCore.QObject):  # pylint: disable=too-few-public-methods

    # Only a QObject can hold signals, which is why we need a QObject subclass as an
    # intermediate attribute of the QWidget to which we want to attach those signals.
    # By QT design, the signal also needs to be a class instance of the object, so
    # I haven't found a cleaner way than to create a class holding only that signals...

    """
    Collection of signals used by the TagTreeWidget.

    Class Attributes
    ----------------
    dropped

    """

    dropped: QtCore.Signal = QtCore.Signal(int, str, bool)
    """A signal emited when something is dropped on the tree. The parameters are
    (my_object_id, tag_widget.widget_item_id, remove)."""
