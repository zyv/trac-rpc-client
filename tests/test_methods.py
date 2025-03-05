import json
from datetime import datetime

import pytest
import respx

from trac_rpc.client import ApiClient
from trac_rpc.models import TracAttachment, TracTicket, TracTicketChangelogEntry, TracTicketProperties

from .utils import get_fixture


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({}, "max=0"),
        ({"per_page": 123, "page_number": 456}, "page=456&max=123"),
        ({"query": "status!=closed"}, "status!=closed&max=0"),
        ({"query": "status!=closed", "per_page": 123}, "status!=closed&max=123"),
        ({"query": "status!=closed", "per_page": 123, "page_number": 456}, "status!=closed&page=456&max=123"),
    ],
)
def test_query_tickets(kwargs: dict, expected: str, api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text="""{"error": null, "result": [3, 2, 1], "id": null}""")

    def get_last_request_params() -> str:
        (param,) = json.loads(respx_mock.calls.last.request.content)["params"]
        return param

    assert sorted(api_client.query_tickets(**kwargs)) == [1, 2, 3]
    assert get_last_request_params() == expected


def test_get_ticket_attachments(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text=get_fixture("trac-get-ticket-attachments-response.json"))

    (attachment,) = api_client.get_ticket_attachments(1)
    assert respx_mock.calls.last.request.content == b'{"id":null,"method":"ticket.listAttachments","params":[1]}'

    assert attachment == TracAttachment(
        filename="TracXMLRPC-1.2.0.dev0-py3.13.egg",
        description="Test attachment",
        size=87904,
        timestamp=datetime.fromisoformat("2025-02-27T13:38:04.870563+00:00"),
        author="admin",
    )


def test_get_ticket_changelog(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text=get_fixture("trac-get-ticket-changelog-response.json"))

    changelog = api_client.get_ticket_changelog(1)
    assert respx_mock.calls.last.request.content == b'{"id":null,"method":"ticket.changeLog","params":[1]}'

    assert changelog == [
        TracTicketChangelogEntry(
            timestamp=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
            author="admin",
            field="comment",
            old_value="1",
            new_value="Test comment",
            permanent=True,
        ),
        TracTicketChangelogEntry(
            timestamp=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
            author="admin",
            field="owner",
            old_value="somebody",
            new_value="admin",
            permanent=True,
        ),
        TracTicketChangelogEntry(
            timestamp=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
            author="admin",
            field="status",
            old_value="new",
            new_value="accepted",
            permanent=True,
        ),
        TracTicketChangelogEntry(
            timestamp=datetime.fromisoformat("2025-02-27T13:38:04.870563+00:00"),
            author="admin",
            field="attachment",
            old_value="",
            new_value="TracXMLRPC-1.2.0.dev0-py3.13.egg",
            permanent=False,
        ),
        TracTicketChangelogEntry(
            timestamp=datetime.fromisoformat("2025-02-27T13:38:04.870563+00:00"),
            author="admin",
            field="comment",
            old_value="",
            new_value="Test attachment",
            permanent=False,
        ),
    ]


def test_get_ticket(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text=get_fixture("trac-get-ticket-response.json"))

    assert api_client.get_ticket(1) == TracTicketProperties(
        id=1,
        time_created=datetime.fromisoformat("2025-02-27T13:36:35.856566+00:00"),
        time_changed=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
        attributes=TracTicket(
            summary="Test summary",
            reporter="admin",
            owner="admin",
            description="Test description\r\n\r\nSecond line",
            type="defect",
            status="accepted",
            priority="major",
            milestone=None,
            component="component1",
            version=None,
            resolution=None,
            keywords=["test1", "test2,test3"],
            cc=[],
            time=datetime.fromisoformat("2025-02-27T13:36:35.856566+00:00"),
            changetime=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
        ),
    )


def test_get_ticket_last_field_change(api_client: ApiClient, respx_mock: respx.mock):
    respx_mock.post().respond(text=get_fixture("trac-get-ticket-changelog-response.json"))

    last_comment = api_client.get_ticket_last_field_change(1, "comment")
    assert last_comment == TracTicketChangelogEntry(
        timestamp=datetime.fromisoformat("2025-02-27T13:38:04.870563+00:00"),
        author="admin",
        field="comment",
        old_value="",
        new_value="Test attachment",
        permanent=False,
    )

    last_cc_change = api_client.get_ticket_last_field_change(1, "cc")
    assert last_cc_change is None

    last_owner_change = api_client.get_ticket_last_field_change(1, "owner", "admin")
    assert last_owner_change == TracTicketChangelogEntry(
        timestamp=datetime.fromisoformat("2025-02-27T13:37:11.171873+00:00"),
        author="admin",
        field="owner",
        old_value="somebody",
        new_value="admin",
        permanent=True,
    )
