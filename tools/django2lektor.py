#!/usr/bin/env python3
"""Convert django records to lektor content.

For the psycopg website.
"""

import sys
import json
import logging
from pathlib import Path

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s')

PROJECT_DIR = Path(__file__).parent.parent


def main():
    with open(PROJECT_DIR / 'data.json') as f:
        data = json.load(f)

    users = {}
    for record in data:
        if record['model'] == 'auth.user':
            users[record['pk']] = record

    for record in data:
        if record['model'] == 'flatpages.flatpage':
            convert_flatpage(record)
        if record['model'] == 'diario.entry':
            convert_diario_entry(record, users)


def convert_flatpage(record):
    fields = record['fields']
    if 2 not in fields['sites']:
        return

    logger.info("flatpage: %s", fields['url'])
    body = fields['content'].replace('\r\n', '\n').strip()
    fn = PROJECT_DIR / 'convert/pages' / fields['url'].strip('/') / 'contents.lr'
    fn.parent.mkdir(parents=True, exist_ok=True)
    with fn.open('w') as f:
        f.write(f"""\
title: {fields['title']}
---
body:

{body}
""")


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
        f.write(f"""\
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
""")


if __name__ == '__main__':
    sys.exit(main())
