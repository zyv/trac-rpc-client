from pathlib import Path

import httpx

TRAC_RPC_URL = "https://dev.system/trac/rpc"
TRAC_USERNAME = "trac_login"
TRAC_PASSWORD = "trac_password"


def get_fixture(fixture: Path | str) -> str:
    return (Path(__file__).parent / "fixtures" / fixture).read_text()


RESPONSE_API_VERSION = httpx.Response(
    status_code=httpx.codes.OK,
    text=get_fixture("trac-get-api-version-response.json"),
)
