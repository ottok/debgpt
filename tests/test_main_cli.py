from typing import *
import pytest
from debgpt.main_cli import main


@pytest.mark.parametrize('cmd', (
    '-F dryrun',
    '--version',
))
def test_main_cli_system_exit(cmd: str):
    with pytest.raises(SystemExit):
        main(cmd.split())
