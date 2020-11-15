#
from peewee import Model, CharField, AutoField
from config.config import config


class BaseModel(Model):
    """Base model"""

    class Meta:
        """Meta class"""

        database = config.database


class MyObject(BaseModel):
    """Object model"""

    id = AutoField()
    name = CharField()

