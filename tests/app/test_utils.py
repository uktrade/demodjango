import pytest

from app.util import CheckResult


@pytest.mark.parametrize("success", (True, False))
def test_check_result(success):
    result = CheckResult("check_one", "the_description", success)
    assert result.type == "check_one"
    assert result.description == "the_description"
    assert result.success is success
    assert result.message == ""


@pytest.mark.parametrize("success", (True, False))
def test_check_result_with_message(success):
    result = CheckResult("check_one", "the_description", success, "test message")
    assert result.type == "check_one"
    assert result.description == "the_description"
    assert result.success is success
    assert result.message == "test message"


def test_check_result_to_dict():
    result = CheckResult("check_one", "the_description", False)

    assert result.to_dict() == {
        "type": "check_one",
        "description": "the_description",
        "success": False,
        "message": "",
    }


def test_check_result_with_message_to_dict():
    result = CheckResult("check_one", "the_description", False, "test message")

    assert result.to_dict() == {
        "type": "check_one",
        "description": "the_description",
        "success": False,
        "message": "test message",
    }
