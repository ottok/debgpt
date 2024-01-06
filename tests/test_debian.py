import pytest
from debgpt import debian

@pytest.mark.parametrize('idx', ('src:pytorch', '1056388'))
def test_debian_bts(idx: str):
    print(debian.bts(idx))


@pytest.mark.parametrize('section', ('1', '4.6', '4.6.1'))
def test_policy(section, tmp_path):
    print(debian.policy(section, debgpt_home=tmp_path))
