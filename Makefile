.PHONY: build serve setup docs publish

PYTHON=$(CURDIR)/env/bin/python
LEKTOR=$(CURDIR)/env/bin/lektor
DOC_BRANCH=goodbye-initd

build: docs
	test "$$TRAVIS" = "true" || test -d build/.git \
		|| git clone git@github.com:psycopg/psycopg.github.io.git build
	echo 'y' | $(LEKTOR) build -O build -f webpack

docs:
	test -d psycopg2/.git \
		|| git clone -b $(DOC_BRANCH) https://github.com/psycopg/psycopg2.git
	git -C psycopg2 checkout $(DOC_BRANCH)
	git -C psycopg2 pull
	test -d psycopg2/doc/env || $(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc env
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc html

publish:
	git -C build add -A
	git -C build commit -m "updated on $$(date -Iseconds)"
	git -C build push

serve:
	$(LEKTOR) serve -f webpack

setup:
	test -x $(PYTHON) || virtualenv -p python3 env
	test -x $(LEKTOR) || env/bin/pip install -r requirements.txt
