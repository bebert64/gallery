# -*- coding: utf-8 -*-

"""
Defines :
 The :class:`View` class.
"""

from peewee import Model, CharField, AutoField


class View(Model):
    """
    A base model for a view.

    Instance Attributes
    -------------------
    id
    name
    query_string

    """

    id: int = AutoField()
    name: str = CharField()
    query_string: str = CharField()
    """A dump of a QueryParameters object as a string. Allows for storage in the
    database and its reconstruction at runtime."""
