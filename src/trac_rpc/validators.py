import re
from typing import Annotated, Any

from pydantic import AfterValidator, AwareDatetime, BeforeValidator


def validate_datetime(value: Any) -> Any:
    if isinstance(value, dict):
        value_type, value_object = value["__jsonclass__"]
        if value_type == "datetime":
            return f"{value_object}Z"
    return value


def validate_optional_datetime(value: Any) -> Any:
    if value == 0:
        return None
    return validate_datetime(value)


def split_by_separator(separator: str, value: Any) -> Any:
    if isinstance(value, str):
        return [value.strip() for value in value.split(separator)] if value.strip() else []
    return value


def validate_space_separated(value: Any) -> Any:
    if isinstance(value, str):
        return split_by_separator(" ", re.sub(r" +", " ", value.strip()))
    return value


def validate_comma_separated(value: Any) -> Any:
    return split_by_separator(",", value)


def validate_space_or_comma_separated(value: Any) -> Any:
    if isinstance(value, str):
        return validate_comma_separated(value) if "," in value else validate_space_separated(value)
    return value


def validator_string_empty_to_none(v: Any) -> Any | None:
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


def validator_string_strip(v: str) -> str:
    return v.strip()


def validate_in_set[T](value: T | None, allowed: set[T], optional: bool = False) -> T | None:
    if optional and value is None:
        return value
    if value not in allowed:
        raise ValueError(f"'{value}' is not in {allowed}")
    return value


type TracOptionalField[T: str | int] = Annotated[T | None, BeforeValidator(validator_string_empty_to_none)]

type TracDatetime = Annotated[AwareDatetime, BeforeValidator(validate_datetime)]
type OptionalTracDatetime = Annotated[AwareDatetime | None, BeforeValidator(validate_optional_datetime)]

type TracCommaSeparated[T: str] = Annotated[list[T], BeforeValidator(validate_comma_separated)]
type TracSpaceSeparated[T: str] = Annotated[list[T], BeforeValidator(validate_space_separated)]
type TracSpaceOrCommaSeparated[T: str] = Annotated[list[T], BeforeValidator(validate_space_or_comma_separated)]

type TracStrippedStr = Annotated[str, AfterValidator(validator_string_strip)]
