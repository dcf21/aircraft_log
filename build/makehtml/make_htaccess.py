# -*- coding: utf-8 -*-
# make_htaccess.py

import os


def make_htaccess(dir_path, server):
    """
    Make .htaccess file for a directory.

    :param dir_path:
        The directory path relative to the website root.
    :param server:
        The hostname of the server we will serve this web space from.
    :return:
        None
    """

    out = open(os.path.join(dir_path, ".htaccess"), "w")

    # If hostname uses https, then redirect http requests to http
    if server.startswith("https"):
        force_https = """
RewriteCond %{HTTPS} !=on
RewriteCond %{REQUEST_URI} !google97b1895dd6619486.html
RewriteCond %{REQUEST_URI} !^/.well-known/
RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]
"""
    else:
        force_https = ""

    # Standard Apache settings, plus redirects to catch alternative hostnames
    out.write("""\
Options +Indexes
DirectoryIndex index.php
AddType application/pdf .pdf
AddType application/json .json
AddType text/html .html
AddType text/css .css
AddType application/rss+xml .rss
AddType application/x-httpd-php .php
AddHandler cgi-script .php
Options +ExecCGI
RewriteEngine on

{0}

# Fix commonly scraped URLs to fail silently
RewriteRule ^/?wp-login.php(.*) - [R=404,L]

# GZIP COMPRESSION
SetOutputFilter DEFLATE
AddOutputFilterByType DEFLATE text/html text/css text/plain text/xml application/javascript application/json text/xml
BrowserMatch ^Mozilla/4 gzip-only-text/html
BrowserMatch ^Mozilla/4\.0[678] no-gzip
BrowserMatch \bMSIE !no-gzip !gzip-only-text/html
BrowserMatch \bMSI[E] !no-gzip !gzip-only-text/html
SetEnvIfNoCase Request_URI \.(?:gif|jpe?g|png)$ no-gzip
Header append Vary User-Agent env=!dont-vary

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresDefault "access plus 1 seconds"
  ExpiresByType text/html "access plus 1 seconds"
  ExpiresByType image/gif "access plus 120 minutes"
  ExpiresByType image/jpeg "access plus 120 minutes"
  ExpiresByType image/png "access plus 120 minutes"
  ExpiresByType text/css "access plus 60 minutes"
  ExpiresByType application/json "access plus 120 minutes"
  ExpiresByType application/javascript "access plus 60 minutes"
  ExpiresByType text/xml "access plus 60 minutes"
</IfModule>
""".format(force_https))
    out.close()
