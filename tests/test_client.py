import json
from unittest.mock import MagicMock

import httpx
import pytest
import respx
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from trac_rpc.client import ApiClient, HttpClient
from trac_rpc.exceptions import TracRpcError
from trac_rpc.models import TracApiVersion, TracRpcErrorResponse

from .utils import (
    RESPONSE_API_VERSION,
    TRAC_PASSWORD,
    TRAC_RPC_URL,
    TRAC_USERNAME,
    get_fixture,
)


def test_simple_init(api_client: ApiClient):
    assert api_client is not None


def test_auth_default(respx_mock: respx.mock):
    respx_mock.post(
        url=TRAC_RPC_URL,
        headers={
            "Authorization": "Basic dHJhY19sb2dpbjp0cmFjX3Bhc3N3b3Jk",
            "Content-Type": "application/json",
        },
    ).mock(return_value=RESPONSE_API_VERSION)

    api_client = ApiClient(
        rpc_url=TRAC_RPC_URL,
        http_client=HttpClient(auth=(TRAC_USERNAME, TRAC_PASSWORD)),
    )
    api_client.get_api_version()


def test_auth_override(respx_mock: respx.mock):
    respx_mock.post(
        url=TRAC_RPC_URL,
        headers={
            "X-Auth-Token": "1234",
            "Content-Type": "application/json",
        },
    ).mock(return_value=RESPONSE_API_VERSION)

    def custom_auth(request: httpx.Request) -> httpx.Request:
        request.headers["X-Auth-Token"] = "1234"
        return request

    api_client = ApiClient(rpc_url=TRAC_RPC_URL, http_client=HttpClient(auth=custom_auth))
    api_client.get_api_version()

    assert "Authorization" not in respx_mock.calls.last.request.headers


def test_event_hooks_default(monkeypatch: MonkeyPatch, respx_mock: respx.mock):
    respx_mock.post(
        url=TRAC_RPC_URL,
        headers={"Content-Type": "application/json"},
    ).mock(return_value=RESPONSE_API_VERSION)

    mock_log_request, mock_log_response = MagicMock(), MagicMock()
    monkeypatch.setattr(HttpClient, "log_trac_rpc_request", mock_log_request)
    monkeypatch.setattr(HttpClient, "log_trac_rpc_response", mock_log_response)

    api_client = ApiClient(rpc_url=TRAC_RPC_URL)
    api_client.get_api_version()

    mock_log_request.assert_called_once()
    mock_log_response.assert_called_once()


def test_raise_for_status(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post(url=TRAC_RPC_URL) % httpx.codes.BAD_GATEWAY

    with pytest.raises(httpx.HTTPStatusError):
        api_client.get_api_version()


def test_event_hooks_override(monkeypatch: MonkeyPatch, respx_mock: respx.mock):
    respx_mock.post(TRAC_RPC_URL).mock(return_value=RESPONSE_API_VERSION)

    mock_log_request, mock_log_response = MagicMock(), MagicMock()
    monkeypatch.setattr(HttpClient, "log_trac_rpc_request", mock_log_request)
    monkeypatch.setattr(HttpClient, "log_trac_rpc_response", mock_log_response)

    api_client = ApiClient(rpc_url=TRAC_RPC_URL, http_client=HttpClient(event_hooks={}))
    api_client.get_api_version()

    mock_log_request.assert_not_called()
    mock_log_response.assert_not_called()


def test_raise_on_error(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post(TRAC_RPC_URL).respond(
        status_code=httpx.codes.OK,  # sic!
        text=get_fixture("trac-response-rpc-error.json"),
    )

    with pytest.raises(TracRpcError) as excinfo:
        api_client.get_api_version()

    assert str(excinfo.value) == 'RPC method "ticket.wiki_to_html" not found'

    assert excinfo.value.error == TracRpcErrorResponse.model_validate(
        json.loads(get_fixture("trac-response-rpc-error.json"))["error"]
    )


def test_invalid_success_response(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text="""{"error": null, "result": null, "id": null}""")

    with pytest.raises(ValidationError, match=r".+ invalid success response .+"):
        api_client.get_api_version()


def test_invalid_error_response(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text="""{"error": {"message": "", "code": 123, "name": ""}, "result": null, "id": 123}""")

    with pytest.raises(ValidationError, match=r".+ invalid error response .+"):
        api_client.get_api_version()


def test_get_api_version(monkeypatch: MonkeyPatch, api_client, respx_mock: respx.mock):
    respx_mock.post(
        url=TRAC_RPC_URL,
        headers={"Content-Type": "application/json"},
    ).mock(return_value=RESPONSE_API_VERSION)

    response = api_client.get_api_version()

    assert isinstance(response, TracApiVersion)
    assert (response.epoch, response.major, response.minor) == (1, 1, 0)
