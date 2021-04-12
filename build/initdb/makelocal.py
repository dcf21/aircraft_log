#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# makelocal.py

"""
Configure website to use a local hostname by default.
"""

import argparse

from dcford_helpers.connect_db import connect_db


def make_local(suffix="local"):
    """
    Set website to use localhost hostname for URLs.

    :param suffix:
        Suffix to local hostname, usually <local>.

    :type suffix:
        str

    :return:
        None
    """

    # Open database
    [db, c] = connect_db()

    # Insert data
    local_host = 'https://adsb.{suffix}/'.format(suffix=suffix)
    c.execute("UPDATE dcford_constants SET value='{}' WHERE name='server';".format(local_host))

    # Commit changes
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.strip())
    parser.add_argument('--suffix', dest='suffix', default="local",
                    help="Suffix to local hostname, usually <local>.")
    args = parser.parse_args()

    make_local(suffix=args.suffix)
