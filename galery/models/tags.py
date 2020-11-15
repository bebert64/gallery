# -*- coding: utf-8 -*-
# import subprocess
# from pathlib import Path
from peewee import Model, ForeignKeyField, CharField, AutoField
from config.config import config
from .my_object import MyObject


class BaseModel(Model):
    class Meta:
        database = config.database


# TODO :create AUTHORIZED_TYPES list, move intialization of values there with the morse
# operator, and create a "validate on create" method to aonly authorize tags with a
# value from the list
class Tag(BaseModel):

    TYPE_FOLDER = "folder"
    TYPE_TAG = "tag"
    TYPE_PLAYLIST = "playlist"
    TYPE_FILTER = "filter"

    id = AutoField()
    name = CharField()
    parent = ForeignKeyField("self", backref="children", null=True)
    type = CharField()

    def Objects(self):
        return MyObject.select().join(ObjectTag).join(Tag).where(Tag.id == self.id)


class ObjectTag(BaseModel):

    my_object = ForeignKeyField(MyObject)
    tag = ForeignKeyField(Tag)
