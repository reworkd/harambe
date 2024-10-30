import pytest
from harambe_core.errors import CaptchaError, HarambeException


def simulate_captcha_scenario():
    # Simulating a CAPTCHA hit scenario
    raise CaptchaError()


def test_captcha_exception_is_harambe_exception():
    # Testing if HarambeException is raised when expected
    with pytest.raises(HarambeException):
        simulate_captcha_scenario()
