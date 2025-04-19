# -*- coding: utf-8 -*-
# initschema.py

import os

from adsb_helpers.connect_db import db_name, db_user, db_passwd, db_host


def make_mysql_login_config() -> None:
    """
    Create MySQL configuration file with username and password, which means we can log into database without
    supplying these on the command line.

    :return:
        None
    """

    pwd: str = os.getcwd()
    db_config_path: str = os.path.join(pwd, "../../auto/mysql_login.cfg")

    config_text: str = """
[client]
user = {:s}
password = {:s}
host = {:s}
default-character-set = utf8mb4
""".format(db_user, db_passwd, db_host)

    with open(db_config_path, "wt") as f_out:
        f_out.write(config_text)


def init_schema() -> None:
    """
    Create database tables, using schema defined in <initschema.sql>.

    :return:
        None
    """

    pwd: str = os.getcwd()
    sql: str = os.path.join(pwd, "initschema.sql")
    db_config: str = os.path.join(pwd, "../../auto/mysql_login.cfg")

    # Create mysql login config file
    make_mysql_login_config()

    # Recreate database from scratch
    cmd: str = "echo 'DROP DATABASE IF EXISTS {:s};' | mysql --defaults-extra-file={:s}".format(db_name, db_config)
    os.system(cmd)
    cmd = ("echo 'CREATE DATABASE {:s} CHARACTER SET utf8mb4;' | mysql --defaults-extra-file={:s}".
           format(db_name, db_config))
    os.system(cmd)

    # Create basic database schema
    cmd = "cat {:s} | mysql --defaults-extra-file={:s} {:s}".format(sql, db_config, db_name)
    os.system(cmd)


# Do it right away if we're run as a script
if __name__ == "__main__":
    init_schema()
