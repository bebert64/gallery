# -*- coding: utf-8 -*-

"""
Defines :
 The 4 QueryParameter classes, QueryParameterBase, QueryParameterAdd,
 QueryParameterRemove and QueryParameterFilter.

 The QueryParameters class, representing a sequence of QueryParameter.

"""

from __future__ import annotations

from functools import partial
from typing import List, Type, Dict, Callable, Tuple

import gallery.types as types
import gallery.widgets.tag_tree as tag_tree


class QueryParameter:
    """
    Base class for all QueryParameter.

    Parameters
    ----------
    widget_item

    """

    def __init__(self, widget_item: tag_tree.WidgetItem) -> None:
        self._widget_item: tag_tree.WidgetItem = widget_item

    @property
    def widget_item_id(self) -> types.WidgetItemId:
        """The widget item id."""
        widget_item_id = self._widget_item.widget_item_id
        return widget_item_id

    @property
    def _widget_item_name(self) -> str:
        widget_item = self._widget_item
        widget_item_name = widget_item.name
        return widget_item_name

    def _get_widget_item_objects(self) -> types.MyObjectSet:
        widget_item = self._widget_item
        widget_item_objects = widget_item.get_my_objects()
        return widget_item_objects

    def get_modified_objects(
        self, unused_my_objects: types.MyObjectSet
    ) -> types.MyObjectSet:
        """Must be implemented in derived classes."""
        raise NotImplementedError


class QueryParameterBase(QueryParameter):
    """
    Base parameter. Can only be added to a QueryParameters in first position.

    A QueryParameterBase doesn't modify an existing set of objects but instead
    serves as the base, the first parameter.

    """

    def __str__(self) -> str:
        return self._widget_item_name

    def get_modified_objects(
        self, unused_my_objects: types.MyObjectSet
    ) -> types.MyObjectSet:
        """Gets the complete list of my_objects associated with its widget_item."""
        new_objects = self._get_widget_item_objects()
        return new_objects


class QueryParameterAdd(QueryParameter):
    """A QueryParameterAdd is used to add my_objects to the existing collection."""

    def __str__(self) -> str:
        return f" + {self._widget_item_name}"

    def get_modified_objects(self, my_objects: types.MyObjectSet) -> types.MyObjectSet:
        """Gets the existing list of my_objects plus the ones associated with its
         widget_item."""
        new_objects = self._get_widget_item_objects()
        my_objects = my_objects.union(new_objects)
        return my_objects


class QueryParameterRemove(QueryParameter):
    """
    A QueryParameterRemove is used to remove my_objects from the existing collection.
    """

    def __str__(self) -> str:
        return f" - {self._widget_item_name}"

    def get_modified_objects(self, my_objects: types.MyObjectSet) -> types.MyObjectSet:
        """Gets the existing list of my_objects minus the ones associated with its
         widget_item."""
        new_objects = self._get_widget_item_objects()
        my_objects = my_objects.difference(new_objects)
        return my_objects


class QueryParameterFilter(QueryParameter):
    """
    A QueryParameterFilter is used to intersect my_objects with the existing collection.
    """

    def __str__(self) -> str:
        return f" ∩ {self._widget_item_name}"

    def get_modified_objects(self, my_objects: types.MyObjectSet) -> types.MyObjectSet:
        """Gets the my_objects present both in the existing collection and in the
        set associated with its widget item"""
        new_objects = self._get_widget_item_objects()
        my_objects = my_objects.intersection(new_objects)
        return my_objects


class QueryParameters:
    """
    A collection of QueryParameter.

    Parameters
    ----------
    tag_tree_widget

    """

    class_to_method_dict: Dict[Type[QueryParameter], str] = {
        QueryParameterBase: "base",
        QueryParameterAdd: "add",
        QueryParameterRemove: "remove",
        QueryParameterFilter: "filter",
    }

    def __init__(self, tag_tree_widget: tag_tree.TagTreeWidget) -> None:
        self._parameters: List[QueryParameter] = []
        self._tag_tree_widget: tag_tree.TagTreeWidget = tag_tree_widget
        self._has_changed: bool = False
        self.my_objects: types.MyObjectSet = set()
        self._add_handle_parameter_methods()

    def _add_handle_parameter_methods(self):
        for parameter_type in QueryParameters.class_to_method_dict:
            self._add_handle_parameter_method(parameter_type)

    def __str__(self) -> str:
        if self._is_empty:
            query_name = "Empty QueryParameters object"
        else:
            query_name = self._get_query_name_from_parameters()
        return query_name

    def _get_query_name_from_parameters(self) -> str:
        query_name = ""
        for query_parameter in self._parameters:
            query_name += str(query_parameter)
        return query_name

    @property
    def _is_empty(self) -> bool:
        return len(self._parameters) == 0

    def _add_handle_parameter_method(
        self, parameter_type: Type[QueryParameter]
    ) -> None:
        widget_items = self._get_widget_items()
        handle_parameter_method = self._create_handle_parameter_method(
            widget_items, parameter_type
        )
        method_name = QueryParameters.class_to_method_dict[parameter_type]
        self._bind_method(handle_parameter_method, method_name)

    @staticmethod
    def _create_handle_parameter_method(widget_items, parameter_type):
        def _handle_parameter(
            query_parameters: QueryParameters, widget_item_id: types.WidgetItemId
        ) -> None:
            # The method will be dynamically added to an instance of a QueryParameters
            # and should therefore be allowed to access its protected members.
            # pylint: disable = protected-access
            widget_item = widget_items[widget_item_id]
            new_parameter = parameter_type(widget_item)
            query_parameters._parameters.append(new_parameter)

        return _handle_parameter

    def _get_widget_items(self) -> Dict[types.WidgetItemId, tag_tree.WidgetItem]:
        tag_tree_widget = self._tag_tree_widget
        widget_items = tag_tree_widget.widget_items
        return widget_items

    def _bind_method(self, handle_parameter: Callable, method_name: str) -> None:
        method_bound_to_self = partial(handle_parameter, self)
        setattr(self, method_name, method_bound_to_self)

    def get_my_objects(self) -> types.MyObjectSet:
        """The result of the sequence of parameters."""
        my_objects: types.MyObjectSet = set()
        for parameter in self._parameters:
            my_objects = parameter.get_modified_objects(my_objects)
        return my_objects

    def refresh_my_objects(self) -> None:
        """Refreshes the results and check if it has been modified."""
        my_objects_new = self.get_my_objects()
        my_objects_old = self.my_objects
        self.my_objects = my_objects_new
        self._has_changed = my_objects_new != my_objects_old

    @property
    def has_changed(self) -> bool:
        """Whether or not the set of objects has been modified since the last reset."""
        return self._has_changed

    def reset_has_changed_attribute(self) -> None:
        """Resets whether or not the set of objects has been modified."""
        self._has_changed = False

    def get_query_string(self) -> str:
        """
        Transforms the sequence of parameters in a string.

        That string can be reversed into a QueryParameters object via the class
        method create_from_string.

        """
        query_string = ""
        for parameter in self._parameters:
            query_string += self._get_query_string_from_parameter(parameter)
        return query_string

    @staticmethod
    def _get_query_string_from_parameter(parameter):
        # TODO : re clean..
        query_string = "New_QueryParameter|"
        query_string += str(QueryParameters.class_to_method_dict[type(parameter)]) + "|"
        query_string += str(parameter.widget_item_id) + "|"
        return query_string

    @staticmethod
    def create_from_string(
        query_string: str, tag_tree_widget: tag_tree.TagTreeWidget
    ) -> QueryParameters:
        """Creates a QueryParameters object from a formatted string."""
        # create_from_string is a factory method, and should therefore be allowed
        # to access protected members of the class.
        # pylint: disable = protected-access
        query_parameters = QueryParameters(tag_tree_widget)
        split_query_string = query_string.split("New_QueryParameter|")
        for parameter in split_query_string[1:]:
            query_parameters._apply_parameter_method(parameter)
        return query_parameters

    def _apply_parameter_method(self, parameter: str) -> None:
        parameter_method_name, widget_item_id = self._split_into_arguments(parameter)
        parameter_method = getattr(self, parameter_method_name)
        parameter_method(widget_item_id)

    @staticmethod
    def _split_into_arguments(parameter: str) -> Tuple[str, str]:
        parameter_split = parameter.split("|")
        parameter_method_name = parameter_split[0]
        widget_item_id = parameter_split[1]
        return parameter_method_name, widget_item_id

    @staticmethod
    def create_from_widget_item(widget_item: tag_tree.WidgetItem) -> QueryParameters:
        """
        Creates a QueryParameters object based on a widget item.

        If the widget item is based on a tag or a rating (or anything rather than a
        view really...), it will simply create a QueryParameters with one
        QueryParameterBase for that tag (or rating, or...).
        If the widget item is a view, its parameters will be decomposed into the
        original view parameters (instead of simply having a QueryParameterBase for
        that view).
        """
        if isinstance(widget_item, tag_tree.WidgetItemView):
            query_parameters = QueryParameters._create_from_widget_item_view(
                widget_item
            )
        else:
            query_parameters = QueryParameters._create_from_widget_item_default(
                widget_item
            )
        return query_parameters

    @staticmethod
    def _create_from_widget_item_default(
        widget_item: tag_tree.WidgetItem,
    ) -> QueryParameters:
        tag_tree_widget = widget_item.treeWidget()
        query_parameters = QueryParameters(tag_tree_widget)
        # The "base" method is added at runtime by _add_handle_parameter_method
        assert hasattr(query_parameters, "base")
        query_parameters.base(  # type: ignore  # pylint: disable = no-member
            widget_item.widget_item_id
        )
        return query_parameters

    @staticmethod
    def _create_from_widget_item_view(
        widget_item: tag_tree.WidgetItem,
    ) -> QueryParameters:
        tag_tree_widget = widget_item.treeWidget()
        query_string = widget_item.view.query_string
        query_parameters = QueryParameters.create_from_string(
            query_string, tag_tree_widget
        )
        return query_parameters
