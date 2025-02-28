import pytest
from utils import TRAC_RPC_URL

from trac_rpc.client import ApiClient


@pytest.fixture
def api_client():
    return ApiClient(rpc_url=TRAC_RPC_URL)
