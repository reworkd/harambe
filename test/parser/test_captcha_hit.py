import pytest
from harambe.errors import CaptchaError, HarambeException


def simulate_captcha_scenario():
    # Simulating a CAPTCHA hit scenario
    raise CaptchaError()


def test_captcha_hit_exception():
    # Testing if CaptchaHitException is raised when expected
    with pytest.raises(HarambeException, match="CAPTCHA was hit."):
        simulate_captcha_scenario()
