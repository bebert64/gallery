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

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.actions = [
            ("action test", lambda: print("test")),
            ("action id", self.action1),
        ]

    id = AutoField()
    name = CharField()

    def action1(self):
        print(self.id)
