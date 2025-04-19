#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# main_makehtml.py

"""
Copy web pages from source directory into live web space. In the process, minify JS and CSS files.
"""

import argparse
import glob
import logging
import os
import shutil
import sys
import time

import MySQLdb

from typing import List, Sequence

import make_htaccess
import php_preprocess
from adsb_helpers.connect_db import connect_db

# These subdirectories get symlinked rather than copies, because they're quite big
symlink_directories = ("vendor",)


def make_html(minify: bool = True,
              allow_cross_origin: bool = False,
              force_https: bool = True
              ) -> None:
    """
    Copy web pages from source directory into live webspace. In the process, minify JS and CSS files, create htaccess
    files, etc.

    :param minify:
        If true, then CSS and JS source files are minified
    :param allow_cross_origin:
        If true, then .htaccess files are generated that permit cross-origin (CORS) requests
    :param force_https:
        If true, then http requests are redirected to https
    :return:
        None
    """

    # Open database
    db: MySQLdb.connections.Connection
    c: MySQLdb.cursors.DictCursor
    db, c = connect_db()

    # Look up server name
    c.execute("SELECT value FROM adsb_constants WHERE name='server';")
    server: str = str(c.fetchone()["value"])

    # Write last update time
    utc: float = time.time()
    c.execute("UPDATE adsb_constants SET value='{}' WHERE name='lastUpdate';".format(utc))

    # Paths from where we get web content
    cwd: str = os.getcwd()
    root1: str = os.path.join(cwd, "..", "..", "php")
    root2: str = os.path.join(cwd, "..", "..", "auto", "tmp", "html")
    root_list: List[str] = [root1, root2]

    # Path to which we output processed web content
    output: str = os.path.join(cwd, "..", "..", "auto", "html")

    os.system("mkdir -p {}".format(output))
    os.system("rm -Rf {}/*".format(output))

    # Create an htaccess file for the root directory of web server
    make_htaccess.make_htaccess(dir_path=output, server=server,
                                allow_cross_origin=allow_cross_origin, force_https=force_https)

    # Walk through source directory structure
    for root in root_list:
        for in_dir in os.walk(root):

            # Separate out tuple containing subdirectories and files
            assert in_dir[0][0:len(root)] == root
            dir_path: str = in_dir[0][len(root):]
            while dir_path.startswith('/'):
                dir_path = dir_path[1:]

            # List of files in this directory
            files: Sequence[str] = in_dir[2]

            # Ignore directories like .svn which start with a dot
            path_segments: Sequence[str] = dir_path.split('/')
            dotted_path: bool = False
            for segment in path_segments:
                if (len(segment) > 0) and (segment[0] == '.'):
                    dotted_path = True
            if dotted_path:
                continue

            # These are big directories that it's best to symlink
            symlink: bool = False
            for item in symlink_directories:
                if dir_path.startswith(item):
                    if dir_path == item:
                        a: str = os.path.join(root, dir_path)
                        b: str = os.path.join(output, dir_path)
                        if not os.path.exists(b):
                            os.system("ln -s {} {}".format(a, b))
                    symlink = True
            if symlink:
                continue

            # Report working on new directory
            logging.info("Working on directory <{}>".format(dir_path))

            # Create target directory
            path: str = os.path.join(output, dir_path)
            os.system("mkdir -p {}".format(path))

            is_javascript: bool = dir_path.startswith("js")
            is_css: bool = dir_path.startswith("css")

            # Loop over files
            for filename in files:
                in_file: str = "{}".format(os.path.join(root, dir_path, filename))
                out_file: str = "{}".format(os.path.join(output, dir_path, filename))
                if is_javascript and filename.endswith('.js'):
                    logging.info("Compiling JS file <{}>".format(filename))
                    shutil.copyfile(in_file, out_file)
                elif is_css and filename.endswith('.less'):
                    logging.info("Compiling LESS file <{}>".format(filename))
                    css_minify: str = ""
                    if minify:
                        css_minify = "--clean-css=\"--s1 --advanced --compatibility=ie8\""
                    cmd: str = "lessc {} {} {}".format(in_file, css_minify, out_file[:-4] + "css")
                    logging.info(cmd)
                    os.system(cmd)
                elif filename.endswith('.php'):
                    php_preprocess.php_preprocess(filename=filename,
                                                  in_file=in_file, out_file=out_file)
                else:
                    # logging.info("Copying file <{}>".format(filename))
                    shutil.copyfile(in_file, out_file)

    # Compress Javascript
    javascripts: Sequence[str] = (glob.glob(os.path.join(output, "js/*.js")) +
                                  glob.glob(os.path.join(output, "js/*/*.js")))
    if minify:
        cmd: str = "cd {} ; uglifyjs *.js ".format(os.path.join(output, "js"))
        cmd += ' --compress --mangle toplevel --mangle-props regex=/^_/ '
        # cmd += " --source-map " + os.path.join(output, "js", "dcford.min.map")
        cmd += " --output " + os.path.join(output, "js", "dcford.min.js")
        logging.info(cmd)
        os.system(cmd)
    else:
        cmd = "cat {} > {}".format(" ".join(javascripts), os.path.join(output, "js", "dcford.min.js"))
        logging.info(cmd)
        os.system(cmd)

    # Delete all the source JS files that we've combined
    for js in javascripts:
        os.unlink(js)

    # Close database handle
    db.commit()
    db.close()


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO,
                        stream=sys.stdout,
                        format='[%(asctime)s] %(levelname)s:%(filename)s:%(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logger = logging.getLogger(__name__)
    logger.info(__doc__.strip())

    # Read input parameters
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--minify',
                        action='store_true', dest="minify",
                        help="Minify JS code")
    parser.add_argument('--no_minify',
                        action='store_false', dest="minify",
                        help="Do not minify JS code")
    parser.add_argument('--allow_cross_origin',
                        action='store_true', dest="allow_cross_origin",
                        help="Allow cross-origin JS requests")
    parser.add_argument('--no_allow_cross_origin',
                        action='store_false', dest="allow_cross_origin",
                        help="Do not allow cross-origin JS requests")
    parser.add_argument('--force_https',
                        action='store_true', dest="force_https",
                        help="Redirect http requests to https")
    parser.add_argument('--no_force_https',
                        action='store_false', dest="force_https",
                        help="Do not redirect http requests to https")
    parser.set_defaults(minify=True)
    parser.set_defaults(allow_cross_origin=False)
    parser.set_defaults(force_https=True)
    args = parser.parse_args()

    # Make HTML distribution
    make_html(minify=args.minify,
              allow_cross_origin=args.allow_cross_origin,
              force_https=args.force_https
              )
