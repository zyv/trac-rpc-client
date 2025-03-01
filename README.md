# Trac RPC API client

Modern, Pythonic and type-safe Trac RPC API client.

## Installation

```shell
$ pip install trac-rpc-client
```

### Dependencies

* [Pydantic V2](https://pydantic.dev)
* [httpx](https://www.python-httpx.org)

## Usage

```pycon
>>> from trac_rpc.client import ApiClient, HttpClient

>>> api_client = ApiClient(
    rpc_url="http://127.0.0.1:8000/login/rpc",
    http_client=HttpClient(auth=("admin", "admin")),
)

>>> api_client.get_api_version()
TracApiVersion(epoch=1, major=2, minor=0)

>>> result = api_client.get_ticket_last_field_change(1, "status", "closed")
>>> result.timestamp
datetime.datetime(2025, 2, 27, 13, 37, 11, 171873, tzinfo=TzInfo(UTC))
```

> [!IMPORTANT]
> Trac APIs (e.g. `query_tickets`) do not return IDs and/or objects sorted in alphanumeric order!
>
> They can either be returned in a custom order (such as priority levels) or grouped by certain fields (such as ticket IDs). If you want to iterate on the objects in a particular order, always remember to sort them appropriately after you call the API.

### Customizing models

#### Changing default string type

Some models like `TracMilestone` can be parameterized with a string type such as `TracStrippedStr` instead of `str` to strip leading and trailing whitespace:

```python
from trac_rpc.client import ApiClient
from trac_rpc.models import TracMilestone
from trac_rpc.validators import TracStrippedStr

api_client = ApiClient(rpc_url="http://127.0.0.1:8000/rpc")
milestone = api_client.get_milestone(" milestone2  ", TracMilestone[TracStrippedStr])
```

This is especially useful for migrations to detect unnoticed whitespace problems. However, this can potentially cause calls to the Trac RPC API with string object names to fail, so it is not enabled by default.

#### Adjusting `TracTicket` model

Each Trac installation is configured in its own way. The default `TracTicket` model can be easily customized by subclassing:

```python
from trac_rpc.models import TracTicket as TracTicketBase
from trac_rpc.validators import TracSpaceOrCommaSeparated

class TracTicket(TracTicketBase):
    keywords: TracSpaceOrCommaSeparated[str]
    cc: TracSpaceOrCommaSeparated[str]
```

Usually Trac fields are separated by spaces (`TracSpaceSeparated`), but alternative types are provided for convenience (`TracCommaSeparated`, `TracSpaceOrCommaSeparated`).

Complex validation to ensure data consistency is possible with the `validate_in_set` validator:

```python
from functools import partial
from typing import Annotated

from pydantic import AfterValidator
from trac_rpc.models import TracTicket as TracTicketBase
from trac_rpc.validators import validate_in_set, TracOptionalField

VERSIONS = {"1.0", "2.0"}


class TracTicket(TracTicketBase):
    validate_version = partial(validate_in_set, allowed=VERSIONS, optional=True)
    ...
    version: Annotated[TracOptionalField[str], AfterValidator(validate_version)]
```

## Setting up test Trac server

See [GitHub Actions workflow](.github/workflows/ci.yml) for integration tests.
