import pytest

from app.util import CheckResult


@pytest.mark.parametrize("success", (True, False))
def test_check_result(success):
    result = CheckResult("check_one", success)
    assert result.name == "check_one"
    assert result.success is success
    assert result.message == ""


@pytest.mark.parametrize("success", (True, False))
def test_check_result_with_message(success):
    result = CheckResult("check_one", success, "test message")
    assert result.name == "check_one"
    assert result.success is success
    assert result.message == "test message"


def test_check_result_to_dict():
    result = CheckResult("check_one", False)

    assert result.to_dict() == {
        "name": "check_one",
        "success": False,
        "message": "",
    }


def test_check_result_with_message_to_dict():
    result = CheckResult("check_one", False, "test message")

    assert result.to_dict() == {
        "name": "check_one",
        "success": False,
        "message": "test message",
    }
