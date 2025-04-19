#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# makelive.py

import MySQLdb

from adsb_helpers.connect_db import connect_db


def make_live() -> None:
    """
    Set website to use live hostname for URLs.

    :return:
        None
    """

    # Open database
    db: MySQLdb.connections.Connection
    c: MySQLdb.cursors.DictCursor
    db, c = connect_db()

    # Insert data
    c.execute("UPDATE adsb_constants SET value='https://adsb.rpi/' WHERE name='server';")

    # Commit changes
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    make_live()
