import pytest

from trac_rpc.client import ApiClient

from .utils import TRAC_RPC_URL


@pytest.fixture
def api_client():
    return ApiClient(rpc_url=TRAC_RPC_URL)
