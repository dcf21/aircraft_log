# -*- coding: utf-8 -*-
# connect_db.py

import os
import re
import sys
# Ignore SQL warnings
import warnings
from os import path as os_path

import MySQLdb

warnings.filterwarnings("ignore", ".*Unknown table .*")

# Fetch path to database profile
our_path = os_path.split(os_path.abspath(__file__))[0]
root_path = re.match(r"(.*ads_b/)", our_path).group(1)
if not os.path.exists(os_path.join(root_path, "build/initdb/dbinfo/db_profile")):
    sys.stderr.write(
        "You must create a file <db_profile> in <build/initdb/dbinfo> to specify which database profile to use.\n")
    sys.exit(1)
db_profile = open(os_path.join(root_path, "build/initdb/dbinfo/db_profile")).read().strip()
if not os.path.exists(os_path.join(root_path, "build/initdb/dbinfo/db_profile_%s" % db_profile)):
    sys.stderr.write("File <db_profile> in <build/initdb/dbinfo> names an invalid profile.\n")
    sys.exit(1)

# Look up MySQL database log in details
db_login = open(os_path.join(root_path, "build/initdb/dbinfo/db_profile_%s" % db_profile)).read().split('\n')
db_host = "localhost"
db_user = db_login[0].strip()
db_passwd = db_login[1].strip()
db_name = db_login[2].strip()


# Open database
def connect_db():
    """
    Return a new MySQLdb connection to the database.

    :return:
        List of [database handle, connection handle]
    """

    global db_host, db_name, db_passwd, db_user
    db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_passwd, db=db_name)
    c = db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    db.set_character_set('utf8mb4')
    c.execute('SET NAMES utf8mb4;')
    c.execute('SET CHARACTER SET utf8mb4;')
    c.execute('SET character_set_connection=utf8mb4;')

    return [db, c]
