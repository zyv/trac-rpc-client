import respx

from trac_rpc.client import ApiClient
from trac_rpc.models import TracMilestone
from trac_rpc.validators import TracStrippedStr

from .utils import get_fixture


def test_custom_string_type(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text=get_fixture("trac-get-milestone-response.json"))

    milestone = api_client.get_milestone(" milestone2  ", TracMilestone[TracStrippedStr])
    assert milestone.name == "milestone2"
