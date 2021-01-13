# -*- coding: utf-8 -*-

"""
Defines :
 The :class:`Tag` and :class:`ObjectTag` base classes.

 The :meth:`tag_factory` convenience method allowing to create the derived classes
 :class:`MyTag` and :class:`MyObjectTag`, specific to the user defined object and
 its database.

"""

from __future__ import annotations

from functools import partial
from typing import Tuple, Type, Set, List

import peewee
from peewee import Model, ForeignKeyField, CharField, AutoField

import gallery.types as types


class Tag(Model):
    """
    A base model for tags.

    Instance Attributes
    -------------------
    id
    name
    parent
    type

    Methods
    -------
    get_my_objects
    get_my_objects_with_descendants
    delete_self_and_children
    get_descendants

    Warning
    -------
    The base model has no database specified, and cannot be used directly. Instead,
    the user should create a derived class using the :meth:`tag_factory` function.

    """

    id: int = AutoField()
    name: str = CharField()
    parent: Tag = ForeignKeyField("self", backref="children", null=True)
    type: str = CharField()

    def get_my_objects(self) -> types.MyObjectSet:
        """A set of the objects tagged with the tag."""
        # The method uses directly the MyObject class, not defined in the parent Tag
        # class, only in its derived classes created by the tag_factory function.
        # The implementation has to be done inside tag_factory.
        raise NotImplementedError

    def get_my_objects_with_descendants(self) -> types.MyObjectSet:
        """A set of the objects tagged with the tag or one of its descendants."""
        my_objects_with_descendants = self.get_my_objects()
        # "children" is defined as a backref in the "parent" field
        for child in self.children:  # pylint: disable=no-member
            my_objects_with_descendants = my_objects_with_descendants.union(
                child.get_my_objects_with_descendants()
            )
        return my_objects_with_descendants

    def delete_self_and_children(self) -> None:
        """Recursively delete a tag and all his children."""
        # "children" is defined as backref in the "parent" field
        for child in self.children:  # pylint: disable=no-member
            child.delete_self_and_children()
        self.delete_instance()

    def get_descendants(self) -> List[Tag]:
        """The list of all descendants of the tag."""
        descendants = []
        # "children" is defined as backref in the "parent" field
        for child in self.children:  # pylint: disable=no-member
            descendants.append(child)
            descendants += child.get_descendants()
        return descendants


class ObjectTag(Model):
    """
    Links between Tag and MyObject.

    Instance Attributes
    -------------------
    my_object
    tag

    """

    my_object: types.MyObjectType
    tag: Tag


def tag_factory(
    my_database: peewee.SqliteDatabase, MyObject: types.MyObjectType
) -> Tuple[Type[Tag], Type[ObjectTag]]:
    """
    Creates two classes used to manipulate tags specific to MyObject and the associated
    database.

    Parameters
    -----------
    my_database
        The database holding the objects.
    MyObject
        Model for the user defined object.

    Returns
    -------
    MyTag: Type[:class:`Tag`]
        Model for a tag specific to MyObject.
    MyObjectTag: Type[:class:`ObjectTag`]
        Model for the link between MyTag and MyObject.

    """

    # ==================================================================================
    #
    # Pylint disable justifications :
    #
    #   no need for class docstring for My Tag and MyObjectTag, as all important
    #   information are given in the base classes Tag and ObjectTag above.
    #
    #   the Meta class is needed by peewee, but doesn't need its own docstring (or
    #   any additional methods...)
    #
    # ==================================================================================

    class MyTag(Tag):  # pylint: disable=missing-class-docstring

        # The parent field MUST be redefined in any derived class, so that the
        # "children" attribute returns instances of the derived class. Otherwise, it
        # will return instances of the parent class Tag.
        parent = ForeignKeyField("self", backref="children", null=True)

        class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
            database = my_database
            table_name = "tag"

        def get_my_objects(self,) -> Set[Model]:
            my_objects = set(
                MyObject.select()
                .join(MyObjectTag)
                .join(self.__class__)
                .where(MyTag.id == self.id)
            )
            return my_objects

    class MyObjectTag(Model):  # pylint: disable=missing-class-docstring
        my_object = ForeignKeyField(MyObject)
        tag = ForeignKeyField(MyTag)

        class Meta:  # pylint: disable=missing-class-docstring, too-few-public-methods
            database = my_database
            table_name = MyObject.__name__.lower() + "_tag"

    return MyTag, MyObjectTag


def add_get_tags_method(my_object: Model) -> None:
    """
    Convenience method to bind a get_tags method to a used defined object.

    Error
    -----
    AssertionError
        The attributes MyTag and MyObjectTag are added to MyObject when a config object
        is created, through Config._add_attributes_linked_to_my_object. This usually
        happens automatically when a MainWidget is created. Those attributes are
        necessary for a get_tags method.

        An error will be raised if one tries to use this method before having created
        a MainWidget or a Config object.

    Parameters
    ----------
    my_object
        object

    """

    _assert_can_add_get_tags_method(my_object)
    my_object_class = type(my_object)

    def get_tags(self: Model) -> Set[Tag]:
        tags = set(
            self.MyTag.select()
            .join(self.MyObjectTag)
            .join(my_object_class)
            .where(my_object_class.id == self.id)
        )
        return tags

    get_tags_bound_to_my_object = partial(get_tags, my_object)
    setattr(my_object, "get_tags", get_tags_bound_to_my_object)


def _assert_can_add_get_tags_method(my_object):
    assert hasattr(my_object, "MyTag")
    assert hasattr(my_object, "MyObjectTag")
    assert isinstance(my_object, Model)
