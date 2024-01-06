import pytest
from debgpt import debian

@pytest.mark.parametrize('idx', ('src:pytorch', '1056388'))
def test_debian_bts(idx: str):
    print(debian.bts(idx))
