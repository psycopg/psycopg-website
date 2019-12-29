.PHONY: build serve setup docs publish

PYTHON=$(CURDIR)/env/bin/python
LEKTOR=$(CURDIR)/env/bin/lektor

build: docs
	$(LEKTOR) build -O build

docs:
	test -d psycopg2/doc/env || $(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc env
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2
	$(MAKE) PYTHON=$(PYTHON) -C psycopg2/doc html

publish:
	(cd build && git add -A && git commit -m "updated on $$(date -Iseconds)")
	git add build
	git commit -m "content changed on $$(date -Iseconds)"
	git push
	(cd build && git push)

serve:
	$(LEKTOR) serve

setup:
	test -x $(PYTHON) || virtualenv -p python3 env
	test -x $(LEKTOR) || env/bin/pip install -r requirements.txt
