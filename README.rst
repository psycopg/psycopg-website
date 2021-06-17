A website for https://www.psycopg.org
=====================================

.. |build| image:: https://github.com/psycopg/psycopg-website/actions/workflows/build.yml/badge.svg
    :target: https://github.com/psycopg/psycopg-website/actions/workflows/build.yml
    :alt: Website build status

In order to change the website:

- clone the repository
- run ``make setup`` to create the virtualenv
- run ``make serve`` to serve the website on http://localhost:5000/
- hack on the website (pages are in the `content` directory)
- commit and push

GitHub Actions will |build| the website and push it to the `github pages repos`__,
served as https://www.psycopg.org/.

.. __: https://github.com/psycopg/psycopg.github.io
