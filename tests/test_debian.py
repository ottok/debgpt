import pytest
from debgpt import debian

@pytest.mark.parametrize('idx', ('src:pytorch', '1056388'))
def test_debian_bts(idx: str):
    print(debian.bts(idx))


@pytest.mark.parametrize('section', ('1', '4.6', '4.6.1'))
def test_policy(section, tmp_path):
    print(debian.policy(section, debgpt_home=tmp_path))

@pytest.mark.parametrize('section', ('5.5', '1'))
def test_devref(section, tmp_path):
    print(debian.devref(section, debgpt_home=tmp_path))


@pytest.mark.parametrize('p', ('pytorch',))
def test_buildd(p):
    print(debian.buildd(p))


