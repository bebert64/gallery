#!  galery
# -*- coding: utf-8 -*-
"""
Short script, designed to be adapted (uncomment lines) for various database management needs.
"""


import sys

# from pathlib import Path
from models import database


# TODO : change main to enter in a functionning where you call the scripts with
# argument via command line to execute the desired tasks.
def main():
    """Launches whatever lines are uncommented."""
    # database.clear_database()
    database.create_tables()


if __name__ == "__main__":
    sys.exit(int(main() or 0))
