import json

import pytest

from trac_rpc.client import ApiClient, HttpClient
from trac_rpc.models import TracApiVersion, TracComponent, TracMilestone, TracVersion

from .utils import get_fixture

pytestmark = pytest.mark.integration


@pytest.fixture
def api_client():
    return ApiClient(
        rpc_url="http://127.0.0.1:8000/login/rpc",
        http_client=HttpClient(auth=("admin", "admin")),
    )


def test_get_api_version(api_client: ApiClient):
    assert api_client.get_api_version() == TracApiVersion(epoch=1, major=2, minor=0)


def get_list_str_result(fixture_name: str) -> list[str]:
    return json.loads(get_fixture(f"{fixture_name}.json"))["result"]


def test_get_all_components(api_client: ApiClient):
    assert api_client.get_all_components() == get_list_str_result("trac-get-all-components-response")


def test_get_all_milestones(api_client: ApiClient):
    assert api_client.get_all_milestones() == get_list_str_result("trac-get-all-milestones-response")


def test_get_all_priorities(api_client: ApiClient):
    assert api_client.get_all_priorities() == get_list_str_result("trac-get-all-priorities-response")


def test_get_all_resolutions(api_client: ApiClient):
    assert api_client.get_all_resolutions() == get_list_str_result("trac-get-all-resolutions-response")


def test_get_all_severities(api_client: ApiClient):
    assert api_client.get_all_severities() == get_list_str_result("trac-get-all-severities-response")


def test_get_all_statuses(api_client: ApiClient):
    assert api_client.get_all_statuses() == get_list_str_result("trac-get-all-statuses-response")


def test_get_all_types(api_client: ApiClient):
    assert api_client.get_all_types() == get_list_str_result("trac-get-all-types-response")


def test_get_all_versions(api_client: ApiClient):
    assert api_client.get_all_versions() == get_list_str_result("trac-get-all-versions-response")


def test_get_milestone(api_client: ApiClient):
    assert api_client.get_milestone("milestone2") == TracMilestone(
        name="milestone2",
        description="",
        completed=None,
        due=None,
    )


def test_get_component(api_client: ApiClient):
    assert api_client.get_component("component2") == TracComponent(
        name="component2",
        owner="somebody",
        description="",
    )


def test_get_version(api_client: ApiClient):
    assert api_client.get_version("2.0") == TracVersion(
        name="2.0",
        released=None,
        description="",
    )


def test_get_all_wiki_pages(api_client: ApiClient):
    assert sorted(api_client.get_all_wiki_pages()) == sorted(get_list_str_result("trac-get-all-wiki-pages-response"))


def test_wiki_to_html(api_client: ApiClient):
    assert (
        api_client.wiki_to_html("'''bold''', ''italic'', `monospaced`")
        == """\
<p>
<strong>bold</strong>, <em>italic</em>, <code>monospaced</code>
</p>
"""
    )
