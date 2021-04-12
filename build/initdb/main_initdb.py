#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# main_initdb.py

"""
Initialise database tables, and insert default values.
"""

import initschema

# Initialise database schema, and data which acts as foreign keys
initschema.init_schema()
