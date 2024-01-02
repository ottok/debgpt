# XXX: "python3 -m debgpt.maimn_cli" is equivalent to "debgpt"

# general chat
echo python3 -m debgpt.main_cli none
echo python3 examples-pprint.py examples/38d71c1a-3a3c-41f2-977f-569907604971.json

# mailing list
echo python3 -m debgpt.main_cli ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary -i
echo python3 examples-pprint.py examples/95e9759b-1b67-49d4-854a-2dedfff07640.json
