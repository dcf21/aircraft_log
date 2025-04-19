# -*- coding: utf-8 -*-
# initdata.py

import os

import MySQLdb

from adsb_helpers.connect_db import connect_db
from adsb_helpers.vendor import xmltodict


def init_data() -> None:
    """
    Read default data from the file <initdata.xml> and populate it into the database.

    :return:
        None
    """

    # Read source data
    pwd: str = os.getcwd()
    with open(os.path.join(pwd, "initdata.xml"), "rb") as xml_file:
        xml = xmltodict.parse(xml_file)

    # Open database
    db: MySQLdb.connections.Connection
    c: MySQLdb.cursors.DictCursor
    db, c = connect_db()

    c.execute("BEGIN;")

    # Populate table of constants
    for const in xml['data']['constants']['constant']:
        c.execute("INSERT INTO adsb_constants VALUES (DEFAULT, %s, %s);", (const['name'], const['value']))
        if const['name'] == 'copyright':
            os.system("mkdir -p ../../auto/tmp/settings")
            with open("../../auto/tmp/settings/copyright", "w") as f_out:
                f_out.write(const["value"])

    # Image formats
    for item in xml['data']['imgFormats']['format']:
        c.execute("INSERT INTO adsb_img_formats VALUES (DEFAULT, %s, %s, %s);",
                  (item['name'], item['xsize'], item['ysize']))

    # Commit changes
    c.execute("COMMIT;")
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    init_data()
