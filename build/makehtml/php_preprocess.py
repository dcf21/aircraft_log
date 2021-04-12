# -*- coding: utf-8 -*-
# php_preprocess.py

import os
import shutil
import logging


def php_preprocess(filename, in_file, out_file):
    """
    Hook to apply pre-processing to PHP files when they are copied from the source code directory to the live
    web space.

    :param filename:
        The filename (excluding path) of the source PHP file
    :param in_file:
        The filename (including path) to the source PHP file
    :param out_file:
        The filename (including path) of the target directory where the live web space sits
    :return:
        None
    """

    logging.info("Working on file <{}>".format(filename))
    shutil.copyfile(in_file, out_file)

    # Make PHP files executable
    os.system("chmod 755 {}".format(out_file))
