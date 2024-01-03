main: pytest

show-demo:
	pygmentize demo.sh

autopep8:
	find debgpt -type f -name '*.py' -exec autopep8 -i '{}' \;

pytest:
	pytest -v debgpt/debian.py
