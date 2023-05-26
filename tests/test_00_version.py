import pynemo


def test_version() -> None:
    assert pynemo.__version__ != "999"
