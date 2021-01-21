# -*- coding: utf-8 -*-

"""
Defines :
 The GalleryModels class.

"""

from typing import Type

import peewee

from gallery.models.tags import tag_factory
from gallery.models.views import View


class GalleryModels:  # pylint: disable=too-few-public-methods

    """
    Holds the various peewee models necessary to manage the collection of MyObject.

    Instance Attributes
    -------------------
    MyObject
    MyTag
    MyObjectTag
    MyView

    """

    MyObject: Type[peewee.Model]
    MyTag: Type[peewee.Model]
    MyObjectTag: Type[peewee.Model]
    MyView: Type[peewee.Model]

    def __init__(
        self, database: peewee.SqliteDatabase, MyObject: Type[peewee.Model],
    ):
        self.database = database
        self._add_attributes_linked_to_my_object(MyObject)
        self._add_view_attribute()

    def _add_attributes_linked_to_my_object(self, MyObject: Type[peewee.Model]) -> None:
        self.MyObject = MyObject
        MyTag, MyObjectTag = tag_factory(self.database, MyObject)
        self.MyTag = MyTag
        self.MyObjectTag = MyObjectTag
        self.MyObject.MyTag = self.MyTag
        self.MyObject.MyObjectTag = self.MyObjectTag

    def _add_view_attribute(self) -> None:
        self.MyView = View
        self.MyView._meta.database = (  # pylint: disable = no-member, protected-access
            self.database
        )
