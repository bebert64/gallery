#!  gallery
# -*- coding: utf-8 -*-
"""
Short script, designed to be adapted (uncomment lines) for various database management needs.
"""


import sys

# from pathlib import Path
from gallery.models import database


def main():
    """Launches whatever lines are uncommented."""
    # database.clear_database()
    # database.create_tables()
    pass


if __name__ == "__main__":
    sys.exit(int(main() or 0))
