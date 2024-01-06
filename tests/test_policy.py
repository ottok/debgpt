import pytest
from debgpt.policy import DebianPolicy
from debgpt.policy import DebianDevref


@pytest.mark.parametrize('section', ('1', '4.6', '4.9.1'))
def test_policy(section):
    policy = DebianPolicy()
    print(policy[section])


@pytest.mark.parametrize('section', ('2', '2.1', '3.1.1'))
def test_devref(section):
    devref = DebianDevref()
    print(devref[section])
