#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# main_initdb.py

"""
Initialise database tables, and insert default values.
"""

import initdata
import initschema

# Initialise database schema, and data which acts as foreign keys
initschema.init_schema()

# Initialise constants which can later be re-initialised
initdata.init_data()
