main: pytest

man: debgpt.1

debgpt.1:
	pandoc -s README.md -t man > $@

autopep8:
	find debgpt -type f -name '*.py' -exec autopep8 -i '{}' \;

pytest:
	pytest -v
