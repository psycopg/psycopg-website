.PHONY: build serve setup

build:
	cd psycopg && ../env/bin/lektor build -O ../build

serve:
	cd psycopg && ../env/bin/lektor serve

setup:
	test -d env || virtualenv -p python3 env
	test -x env/bin/lektor || env/bin/pip install -r requirements.txt
