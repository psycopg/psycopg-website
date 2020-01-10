A website for https://psycopg.org
=================================

.. |build| image:: https://travis-ci.org/psycopg/psycopg-website.svg?branch=master
    :target: https://travis-ci.org/psycopg/psycopg-website
    :alt: Website build status

In order to change the website:

- clone the repository
- run ``make setup`` to create the virtualenv
- run ``make serve`` to serve the website on http://localhost:5000/
- hack on the website (pages are in the `content` directory)
- commit and push

Travis will |build| the website and push it to the `github pages repos`__,
served as https://www.psycopg.org/.

.. __: https://github.com/psycopg/psycopg.github.io
