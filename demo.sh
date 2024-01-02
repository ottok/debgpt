# XXX: "python3 -m debgpt.maimn_cli" is equivalent to "debgpt"

# general chat
echo python3 -m debgpt.main_cli none
echo python3 examples-pprint.py examples/38d71c1a-3a3c-41f2-977f-569907604971.json

# mailing list
echo python3 -m debgpt.main_cli ml -u 'https://lists.debian.org/debian-project/2023/12/msg00029.html' summary -i
echo python3 examples-pprint.py examples/95e9759b-1b67-49d4-854a-2dedfff07640.json

# bts
echo python3 -m debgpt.main_cli bts --id src:pytorch summary -i
echo examples/42387633-14a3-4cf3-97e1-d3e0e1c8ac5f.json
echo python3 -m debgpt.main_cli bts --id 1056388 summary -i
echo examples/6ae3b04f-a406-4eb9-8cd0-1e540b850ca9.json
