# -*- coding: utf-8 -*-
"""
Module defining operations possible on the database.

create_table: Creates the main tables on the database.
"""

# import shutil
from config.config import config
from .my_object import MyObject
from .tags import Tag, ObjectTag


def create_tables():
    config.database.connect()
    config.database.create_tables([Tag, ObjectTag, MyObject])


# def clear_database():
#     try:
#         (config.app_folder / "shortcuts.db").unlink()
#     except FileNotFoundError:
#         pass
#     shutil.copy(config.app_folder / "empty.db", config.app_folder / "shortcuts.db")


# def add_objects(folder_path):
#     video_files = [file for file in folder_path.iterdir() if file.is_file()]
#     counter = 0
#     for file in video_files:
#         Video(name=file.name, path=file.parent.absolute()).save()
#         counter += 1
#         if counter % 20 == 0:
#             print(f"{counter} videos treated")
