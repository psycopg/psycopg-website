.PHONY: build serve setup

build:
	env/bin/lektor build -O ../build

publish:
	(cd build && git add -A && git commit -m "updated on $$(date -Iseconds)")
	git add build
	git commit -m "content changed on $$(date -Iseconds)"
	git push
	(cd build && git push)

serve:
	env/bin/lektor serve

setup:
	test -d env || virtualenv -p python3 env
	test -x env/bin/lektor || env/bin/pip install -r requirements.txt
