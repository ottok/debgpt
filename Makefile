autopep8:
	find debgpt -type f -name '*.py' -exec autopep8 -i '{}' \;

pytest:
	true
