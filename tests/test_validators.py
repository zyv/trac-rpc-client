from typing import Any

import pytest

from trac_rpc.validators import (
    validate_comma_separated,
    validate_in_set,
    validate_space_or_comma_separated,
    validate_space_separated,
)


@pytest.mark.parametrize(
    ("value", "allowed", "optional", "raises"),
    [
        (1, {1, 2, 3}, False, False),
        (5, {1, 2, 3}, False, True),
        (None, {1, 2, 3}, False, True),
        (None, {1, 2, 3}, True, False),
    ],
)
def test_validate_in_set(value: int | None, allowed: set[int], optional: bool, raises: bool):
    if raises:
        with pytest.raises(ValueError, match=".+ is not in .+"):
            validate_in_set(value, allowed, optional)
    else:
        assert validate_in_set(value, allowed, optional) == value


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (123, 123),
        ("", []),
        (" ", []),
        ("  ", []),
        ("  test", ["test"]),
        ("  test ", ["test"]),
        ("  test1   test2 ", ["test1", "test2"]),
        ("  test1   test2,test3 ", ["test1", "test2,test3"]),
        ("  test1   test2, test3 ", ["test1", "test2,", "test3"]),
    ],
)
def test_validate_space_separated(value: Any, expected: Any):
    assert validate_space_separated(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (123, 123),
        ("", []),
        (" ", []),
        ("  ", []),
        ("  test", ["test"]),
        ("  test ", ["test"]),
        ("  test1   test2 ", ["test1   test2"]),
        ("  test1   test2,test3 ", ["test1   test2", "test3"]),
        ("  test1   test2, test3 ", ["test1   test2", "test3"]),
    ],
)
def test_validate_comma_separated(value: Any, expected: Any):
    assert validate_comma_separated(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (123, 123),
        ("", []),
        (" ", []),
        ("  ", []),
        ("  test", ["test"]),
        ("  test ", ["test"]),
        ("  test1   test2 ", ["test1", "test2"]),
        ("  test1   test2,test3 ", ["test1   test2", "test3"]),
        ("  test1   test2, test3 ", ["test1   test2", "test3"]),
    ],
)
def test_validate_space_or_comma_separated(value: Any, expected: Any):
    assert validate_space_or_comma_separated(value) == expected
