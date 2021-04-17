#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# make_plane_database.py

"""
Read database of planes, indexed by hex ident.
"""

import csv
import logging
import os
import sys

from adsb_helpers.connect_db import connect_db, db_name


def init_plane_database():
    """
    Read database of planes, indexed by hex ident.

    :return:
        None
    """

    # Fetch source data
    os.system("mkdir -p ../../auto/downloads")

    csv_filename = "../../auto/downloads/aircraftDatabase.csv"
    if not os.path.exists(csv_filename):
        logging.info("Fetching CSV file from OpenSky")
        url = "https://opensky-network.org/datasets/metadata/aircraftDatabase.csv"
        os.system("cd ../../auto/downloads/ ; wget {}".format(url))

    # Open database
    [db, c] = connect_db()
    c.execute("BEGIN;")

    # Create tables
    logging.info("Making aircraft SQL tables")
    c.execute("DROP TABLE IF EXISTS aircraft_hex_codes;")

    pwd = os.getcwd()
    sql = os.path.join(pwd, "create_tables.sql")
    db_config = os.path.join(pwd, "../../auto/mysql_login.cfg")
    cmd = "cat {:s} | mysql --defaults-extra-file={:s} {:s}".format(sql, db_config, db_name)
    os.system(cmd)

    # Read source data
    with open(csv_filename) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            # Capitalise hex ident
            row[0] = row[0].upper()

            # Insert
            c.execute("""
INSERT INTO aircraft_hex_codes
(hex_ident, registration, manufacturericao, manufacturername, model, typecode, serialnumber, linenumber,
 icaoaircrafttype, operator, operatorcallsign, operatoricao, operatoriata, owner, testreg, registered, reguntil,
 status, built, firstflightdate, seatconfiguration, engines, modes, adsb, acars, notes, categoryDescription)
VALUES
(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                      row)

    # Commit changes
    c.execute("COMMIT;")
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    init_plane_database()
