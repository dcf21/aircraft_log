#!../../auto/virtualenv/bin/python3
# -*- coding: utf-8 -*-
# main_makehtml.py

"""
Copy web pages from source directory into live web space. In the process, minify JS and CSS files.
"""

import glob
import logging
import os
import shutil
import sys
import time

import make_htaccess
import php_preprocess
from adsb_helpers.connect_db import connect_db

# Flag to choose whether we minify CSS and Javascript
minify = True

# These subdirectories get symlinked rather than copies, because they're quite big
symlink_directories = ["vendor"]


def make_html():
    """
    Copy web pages from source directory into live web space. In the process, minify JS and CSS files, create htaccess
    files, etc.

    :return:
        None
    """

    # Open database
    [db, c] = connect_db()

    # Look up server name
    c.execute("SELECT value FROM adsb_constants WHERE name='server';")
    server = str(c.fetchone()["value"])

    # Write last update time
    utc = time.time()
    c.execute("UPDATE adsb_constants SET value='{}' WHERE name='lastUpdate';".format(utc))

    # Paths from where we get web content
    cwd = os.getcwd()
    root1 = os.path.join(cwd, "..", "..", "php")
    root2 = os.path.join(cwd, "..", "..", "auto", "tmp", "html")
    root_list = [root1, root2]

    # Path to which we output processed web content
    output = os.path.join(cwd, "..", "..", "auto", "html")

    os.system("mkdir -p {}".format(output))
    os.system("rm -Rf {}/*".format(output))

    # Create an htaccess file for the root directory of web server
    make_htaccess.make_htaccess(dir_path=output, server=server)

    # Walk through source directory structure
    for root in root_list:
        for in_dir in os.walk(root):

            # Separate out tuple containing subdirectories and files
            assert in_dir[0][0:len(root)] == root
            dir_path = in_dir[0][len(root):]
            while dir_path.startswith('/'):
                dir_path = dir_path[1:]

            # List of files in this directory
            files = in_dir[2]

            # Ignore directories like .svn which start with a dot
            path_segments = dir_path.split('/')
            dotted_path = False
            for segment in path_segments:
                if (len(segment) > 0) and (segment[0] == '.'):
                    dotted_path = True
            if dotted_path:
                continue

            # These are big directories that it's best to symlink
            symlink = False
            for item in symlink_directories:
                if dir_path.startswith(item):
                    if dir_path == item:
                        a = os.path.join(root, dir_path)
                        b = os.path.join(output, dir_path)
                        if not os.path.exists(b):
                            os.system("ln -s {} {}".format(a, b))
                    symlink = True
            if symlink:
                continue

            # Report working on new directory
            logging.info("Working on directory <{}>".format(dir_path))

            # Create target directory
            path = os.path.join(output, dir_path)
            os.system("mkdir -p {}".format(path))

            is_javascript = dir_path.startswith("js")
            is_css = dir_path.startswith("css")

            # Loop over files
            for filename in files:
                in_file = "{}".format(os.path.join(root, dir_path, filename))
                out_file = "{}".format(os.path.join(output, dir_path, filename))
                if is_javascript and filename.endswith('.js'):
                    logging.info("Compiling JS file <{}>".format(filename))
                    shutil.copyfile(in_file, out_file)
                elif is_css and filename.endswith('.less'):
                    logging.info("Compiling LESS file <{}>".format(filename))
                    css_minify = ""
                    if minify:
                        css_minify = "--clean-css=\"--s1 --advanced --compatibility=ie8\""
                    cmd = "lessc {} {} {}".format(in_file, css_minify, out_file[:-4] + "css")
                    logging.info(cmd)
                    os.system(cmd)
                elif filename.endswith('.php'):
                    php_preprocess.php_preprocess(filename=filename,
                                                  in_file=in_file, out_file=out_file)
                else:
                    # logging.info("Copying file <{}>".format(filename))
                    shutil.copyfile(in_file, out_file)

    # Compress Javascript
    javascripts = glob.glob(os.path.join(output, "js/*.js")) + glob.glob(os.path.join(output, "js/*/*.js"))
    if minify:
        cmd = "cd {} ; uglifyjs *.js ".format(os.path.join(output, "js"))
        cmd += ' --compress --mangle toplevel --mangle-props regex=/^_/ '
        # cmd += " --source-map " + os.path.join(output, "js", "dcford.min.map")
        cmd += " --output " + os.path.join(output, "js", "dcford.min.js")
        logging.info(cmd)
        os.system(cmd)
        for js in javascripts:
            os.unlink(js)
    else:
        cmd = "cat {} > {}".format(" ".join(javascripts), os.path.join(output, "js", "dcford.min.js"))
        logging.info(cmd)
        os.system(cmd)
    # Close database handle
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

    make_html()
