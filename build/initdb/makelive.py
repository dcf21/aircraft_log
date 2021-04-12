#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# makelive.py

from dcford_helpers.connect_db import connect_db


def make_live():
    """
    Set website to use live hostname for URLs.

    :return:
        None
    """

    # Open database
    [db, c] = connect_db()

    # Insert data
    c.execute("UPDATE dcford_constants SET value='https://adsb.rpi/' WHERE name='server';")

    # Commit changes
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    make_live()
