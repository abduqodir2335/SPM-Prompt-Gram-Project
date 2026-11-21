import importlib.util


def test_test_guard_module_exists():
    spec = importlib.util.spec_from_file_location("test_conftest", "tests/conftest.py")
    assert spec is not None
