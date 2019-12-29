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

    for record in data:
        if record['model'] == 'flatpages.flatpage':
            convert_flatpage(record)
        if record['model'] == 'diario.entry':
            convert_diario_entry(record)


def convert_flatpage(record):
    fields = record['fields']
    logger.info("flatpage: %s", fields['url'])
    body = fields['content'].replace('\r\n', '\n')
    fn = PROJECT_DIR / 'convert' / fields['url'].strip('/') / 'contents.lr'
    fn.parent.mkdir(parents=True, exist_ok=True)
    with fn.open('w') as f:
        f.write(f"""\
title: {fields['title']}
---
body:

{body}
""")


def convert_diario_entry(record):
    logger.info("diario entry: %s", record['fields']['slug'])


if __name__ == '__main__':
    sys.exit(main())
