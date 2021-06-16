.PHONY: build serve setup docs docs3 publish

PYTHON=$(CURDIR)/env/bin/python
LEKTOR=$(CURDIR)/env/bin/lektor
DOC_BRANCH=master
DOC3_BRANCH=master

TRACKING_ID = $(shell jq --raw-output '.tracking_id' databags/analytics.json)

build: docs docs3
	test "$$TRAVIS" = "true" || test -d build/.git \
		|| git clone git@github.com:psycopg/psycopg.github.io.git build
	echo 'y' | $(LEKTOR) build -O build

serve:
	$(LEKTOR) serve

setup:
	test -x $(PYTHON) || virtualenv -p python3 env
	test -x $(LEKTOR) || env/bin/pip install -r requirements.txt

publish:
	git -C build add -A
	git -C build commit -m "updated on $$(date -Iseconds)"
	git -C build push


# Build psycopg2 docs

docs: psycopg2/doc/env psycopg2/doc/src/_templates/layout.html
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc html

psycopg2/doc/env: psycopg2/README.rst
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc env

psycopg2/README.rst:
	test -d psycopg2/.git \
		|| git clone -b $(DOC_BRANCH) https://github.com/psycopg/psycopg2.git
	git -C psycopg2 checkout $(DOC_BRANCH)
	git -C psycopg2 pull

psycopg2/doc/src/_templates/layout.html: templates/docs-layout.html databags/analytics.json
	mkdir -p $(dir $@)
	TRACKING_ID=${TRACKING_ID} envsubst < $< > $@


# Build psycopg3 docs

docs3: psycopg3/docs/.venv psycopg3/docs/_templates/layout.html templates/_sponsors.html
	$(MAKE) SPHINXBUILD=.venv/bin/sphinx-build PSYCOPG3_IMPL=python -C psycopg3/docs html

psycopg3/docs/.venv: psycopg3/README.rst
	$(MAKE) PYTHON=$(PYTHON) -C psycopg3/docs env

psycopg3/README.rst:
	test -d psycopg3/.git \
		|| git clone -b $(DOC3_BRANCH) https://github.com/psycopg/psycopg3.git
	git -C psycopg3 checkout $(DOC3_BRANCH)
	git -C psycopg3 pull

psycopg3/docs/_templates/layout.html: templates/docs3-layout.html databags/analytics.json
	mkdir -p $(dir $@)
	TRACKING_ID=${TRACKING_ID} envsubst < $< > $@

templates/_sponsors.html: psycopg3/BACKERS.yaml tools/make_sponsors.py
	$(PYTHON) tools/make_sponsors.py < $< > $@
