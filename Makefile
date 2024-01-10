main: pytest

man: debgpt.1

.PHONY: debgpt.1
debgpt.1:
	pandoc -s README.md -t man > $@

autopep8:
	find debgpt -type f -name '*.py' -exec autopep8 -i '{}' \;

pytest:
	PYTHONPATH=. pytest -v

pyflakes:
	find . -type f -name '*.py' -exec pyflakes3 '{}' \; || find . -type f -name '*.py' -exec pyflakes '{}' \;

install:
	pip3 install .
