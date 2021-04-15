#!auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# databaseBackup.py

import os
import datetime

now = datetime.datetime.now()

filename = "mysqlDump_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}.sql.gz".format(
    now.year, now.month, now.day, now.hour, now.minute, now.second)

cmd = "mysqldump --defaults-extra-file={config} {database} | gzip > {output}".format(
    config="auto/mysql_login.cfg",
    database="adsb",
    output=os.path.join("archive", filename))

os.system("mkdir -p archive")
print(cmd)
os.system(cmd)
