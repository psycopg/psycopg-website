#!/usr/bin/env python3
"""Convert django records to lektor content.

For the psycopg website.
"""

import re
import sys
import json
import logging
from pathlib import Path

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s'
)

PROJECT_DIR = Path(__file__).parent.parent


def main():
    with open(PROJECT_DIR / 'data.json') as f:
        data = json.load(f)

    users = {}
    for record in data:
        if record['model'] == 'auth.user':
            users[record['pk']] = record

    redirs = []
    for record in data:
        if record['model'] == 'flatpages.flatpage':
            convert_flatpage(record)
        if record['model'] == 'redirects.redirect':
            convert_redirect(record)
            redirs.append(record)
        if record['model'] == 'diario.entry':
            convert_diario_entry(record, users)

    generate_nginx_config(redirs)
    generate_nginx_config(redirs, host='test.initd.org', status='redirect')
    generate_apache_config(redirs)
    generate_apache_config(redirs, host='test.initd.org', status='temp')


def convert_flatpage(record):
    fields = record['fields']
    if 2 not in fields['sites']:
        return

    logger.info("flatpage: %s", fields['url'])
    body = fields['content'].replace('\r\n', '\n').strip()
    fn = (
        PROJECT_DIR
        / 'convert/pages'
        / fields['url'].strip('/')
        / 'contents.lr'
    )
    fn.parent.mkdir(parents=True, exist_ok=True)
    with fn.open('w') as f:
        f.write(
            f"""\
title: {fields['title']}
---
body:

{body}
"""
        )


def convert_redirect(record):
    fields = record['fields']
    if fields['site'] != 2:
        return

    logger.info("redirect: %s -> %s", fields['old_path'], fields['new_path'])
    fn = (
        PROJECT_DIR
        / 'convert/redirects'
        / fields['old_path'].strip('/')
        / 'contents.lr'
    )
    fn.parent.mkdir(parents=True, exist_ok=True)
    target = fields['new_path']
    if target.startswith('/psycopg/'):
        target = target[len('/psycopg') :]
    absolute = 'yes' if target.startswith('http') else 'no'
    with fn.open('w') as f:
        f.write(
            f"""\
_model: redirect
---
target: {target}
---
absolute: {absolute}
---
_discoverable: no
"""
        )


def convert_diario_entry(record, users):
    fields = record['fields']
    if fields['is_draft']:
        return
    if 2 not in fields['publish_on']:
        return
    logger.info("diario entry: %s", fields['slug'])
    body = fields['body_source'].replace('\r\n', '\n').strip()
    author = "%(first_name)s %(last_name)s" % users[fields['author']]['fields']
    pub_date = fields['pub_date'].split()[0]
    tags = '\n'.join(t.strip(',') for t in fields['tags'].split())
    fn = PROJECT_DIR / 'convert/diario' / fields['slug'] / 'contents.lr'
    fn.parent.mkdir(parents=True, exist_ok=True)
    with fn.open('w') as f:
        f.write(
            f"""\
title: {fields['title']}
---
pub_date: {pub_date}
---
author: {author}
---
tags:

{tags}
---
body:

{body}
"""
        )


def generate_nginx_config(records, host='initd.org', status='permanent'):
    redirs_str = []
    for record in records:
        fields = record['fields']
        if fields['site'] != 2:
            continue

        orig = re.escape(fields['old_path'])
        dest = fields['new_path']
        if dest.startswith('/'):
            dest = f"http://{host}{dest}"

        redirs_str.append(
            f"""\
    rewrite ^{orig}$ {dest} {status};
"""
        )
    redirs_str = ''.join(redirs_str).rstrip()

    fn = PROJECT_DIR / f'convert/{host}.nginx.conf'
    with fn.open('w') as f:
        f.write(
            f"""\
server {{
    server_name {host};

    # Legacy redirects
{redirs_str}

    # Redirect tarballs to PyPI
    rewrite ^/psycopg/tarballs/PSYCOPG-2-./(psycopg2-.*)$
        https://pypi.org/packages/source/p/psycopg2/$1 {status};

    # Point to the new website
    rewrite ^/psycopg/(.*)$ https://www.psycopg.org/$1 {status};
}}

# vim: set filetype=nginx:
"""
        )


def generate_apache_config(records, host='initd.org', status='permanent'):
    redirs_str = []
    for record in records:
        fields = record['fields']
        if fields['site'] != 2:
            continue

        orig = fields['old_path']
        dest = fields['new_path']
        if dest.startswith('/'):
            dest = f"http://{host}{dest}"

        redirs_str.append(
            f"""\
        Redirect {status} {orig} {dest}
"""
        )
    redirs_str = ''.join(redirs_str).rstrip()

    fn = PROJECT_DIR / f'convert/{host}.apache.conf'
    with fn.open('w') as f:
        f.write(
            f"""\
<VirtualHost *:80>
    ServerName {host}
    ServerAdmin daniele.varrazzo@gmail.com

    DocumentRoot /home/psycoweb/psycoweb/var/www/

    <Directory "/home/psycoweb/psycoweb/var/www/">
        # Legacy redirects
{redirs_str}

        # Redirect tarballs to PyPI
        RedirectMatch {status} ^/psycopg/tarballs/PSYCOPG-2-./(psycopg2-.*)$ \\
            https://pypi.org/packages/source/p/psycopg2/$1

        # Point to the new website
        RedirectMatch {status} ^/psycopg/(.*)$ https://www.psycopg.org/$1
    </Directory>

    ErrorLog /var/log/apache2/{host}-error.log
    LogLevel warn

    CustomLog /var/log/apache2/{host}-access.log combined
</VirtualHost>

# vim: set filetype=apache:
"""
        )

if __name__ == '__main__':
    sys.exit(main())
