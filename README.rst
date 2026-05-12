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


Deploying on a Cloudflare page for testing
------------------------------------------

Run the following::

    export CLOUDFLARE_ACCOUNT="282..."
    export CLOUDFLARE_API_TOKEN="cfat_twKk..."
    ./tools/upload-preview

The preview of the website should be published on
https://new-homepage.psycopg-org-website.pages.dev
