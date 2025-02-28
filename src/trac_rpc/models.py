from typing import Any, NamedTuple

from pydantic import (
    BaseModel as PydanticBaseModel,
)
from pydantic import (
    ConfigDict,
    Field,
    RootModel,
    model_validator,
)

from trac_rpc.validators import (
    OptionalTracDatetime,
    TracDatetime,
    TracOptionalField,
    TracSpaceSeparated,
    TracStrippedStr,
)

DEFAULT_CONFIG = ConfigDict(
    populate_by_name=True,
    validate_default=True,
    validate_assignment=True,
    frozen=True,
)


class BaseModel(PydanticBaseModel):
    model_config = DEFAULT_CONFIG


class TracRequest(BaseModel):
    id: int | None = None
    method: str
    params: list | None = None


class TracRpcErrorResponse(BaseModel):
    message: str
    code: int
    name: str


class TracResponse[ResponseT: Any](BaseModel):
    id: int | None
    error: TracRpcErrorResponse | None
    result: RootModel[ResponseT] | None

    @model_validator(mode="after")
    def check_non_overlapping_union_success_error(self) -> Any:
        if self.error is not None:
            if self.id is not None or self.result is not None:
                raise ValueError("invalid error response")
        elif self.result is None:
            raise ValueError("invalid success response")
        return self


class TracApiVersion(NamedTuple):
    epoch: int
    major: int
    minor: int


class TracComponent[StringType: str](BaseModel):
    name: StringType
    owner: StringType
    description: str


class TracMilestone[StringType: str](BaseModel):
    name: StringType
    description: str
    due: OptionalTracDatetime
    completed: OptionalTracDatetime


class TracVersion[StringType: str](BaseModel):
    name: StringType
    time: OptionalTracDatetime = Field(alias="released")
    description: str


class TracTicket[StringType: str](BaseModel):
    summary: StringType
    reporter: StringType
    owner: TracOptionalField[StringType]
    description: str
    type: StringType
    status: StringType
    priority: StringType
    milestone: TracOptionalField[StringType]
    component: StringType
    version: TracOptionalField[StringType]
    resolution: TracOptionalField[StringType]
    keywords: TracSpaceSeparated[str]
    cc: TracSpaceSeparated[str]
    time: TracDatetime
    changetime: TracDatetime


class TracTicketProperties[CustomTicketT: TracTicket](NamedTuple):
    id: int
    time_created: TracDatetime
    time_changed: TracDatetime
    attributes: CustomTicketT


class TracTicketChangelogEntry(NamedTuple):
    timestamp: TracDatetime
    author: TracOptionalField[TracStrippedStr]  # sometimes Trac doesn't record authorship!
    field: TracStrippedStr
    old_value: TracStrippedStr
    new_value: TracStrippedStr
    permanent: bool


TracTicketChangelog = list[TracTicketChangelogEntry]


class TracAttachment(NamedTuple):
    filename: TracStrippedStr
    description: TracStrippedStr
    size: int
    timestamp: TracDatetime
    author: TracStrippedStr


TracTicketAttachments = list[TracAttachment]
