# -*- coding: utf-8 -*-

"""Defines types used by other modules."""

from __future__ import annotations

from typing import Union, Set

import peewee

import gallery.widgets.tag_tree as tag_tree


WidgetItemId = Union[str, int]

WidgetItemParent = Union[tag_tree.WidgetItem, tag_tree.TagTreeWidget]
"""
A WidgetItem can accept either the TagTreeWidget or another WidgetItem as its parent.
"""

MyObjectId = Union[str, int]

MyObjectType = Union[peewee.Model]
"""The user defined object must be derived from a peewee Model class."""

MyObjectSet = Set[MyObjectType]
