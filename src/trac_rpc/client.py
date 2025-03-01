import logging

import httpx

from trac_rpc.exceptions import TracRpcError
from trac_rpc.models import (
    TracApiVersion,
    TracComponent,
    TracMilestone,
    TracRequest,
    TracResponse,
    TracTicket,
    TracTicketAttachments,
    TracTicketChangelog,
    TracTicketChangelogEntry,
    TracTicketProperties,
    TracVersion,
)

logger = logging.getLogger(__name__)


class HttpClient(httpx.Client):
    @staticmethod
    def log_trac_rpc_request(request: httpx.Request):
        logger.debug(f"Trac API Request: {request.method} {request.url} {request.content.decode()}")

    @staticmethod
    def log_trac_rpc_response(response: httpx.Response):
        request = response.request
        response.read()
        logger.debug(f"Trac API Response: {request.method} {request.url} {response.status_code} {response.text}")

    def __init__(self, *, event_hooks=None, **kwargs):
        super().__init__(
            event_hooks=(
                event_hooks
                if event_hooks is not None
                else {
                    "request": [HttpClient.log_trac_rpc_request],
                    "response": [HttpClient.log_trac_rpc_response, httpx.Response.raise_for_status],
                }
            ),
            **kwargs,
        )


class ApiClient:
    def __init__(self, rpc_url: str, *, http_client: httpx.Client | None = None):
        self._rpc_url = rpc_url
        self._http_client = http_client if http_client is not None else HttpClient()

    def _request[T](self, request: TracRequest, klass: type[T]) -> T:
        http_response = self._http_client.post(self._rpc_url, json=request.model_dump())
        trac_response = TracResponse[klass].model_validate_json(http_response.text)

        if trac_response.error is not None:
            raise TracRpcError(trac_response.error.message, error=trac_response.error)

        return trac_response.result.root

    def _request_list_pod[T: str | int](self, function: str, klass: type[T]) -> list[T]:
        return self._request(TracRequest(method=function), list[klass])

    # system - Core of the RPC system
    def get_api_version(self) -> TracApiVersion:
        """
        Returns a list with three elements. First element is the epoch (0=Trac 0.10, 1=Trac 0.11 or higher). Second
        element is the major version number, third is the minor. Changes to the major version indicate API breaking
        changes, while minor version changes are simple additions, bug fixes, etc.
        """
        return self._request(TracRequest(method="system.getAPIVersion"), TracApiVersion)

    # ticket.component - Interface to ticket component objects
    # ticket.milestone - Interface to ticket milestone objects
    # ticket.priority - Interface to ticket priority
    # ticket.resolution - Interface to ticket resolution
    # ticket.severity - Interface to ticket severity
    # ticket.status - An interface to Trac ticket status objects (deprecated)
    # ticket.type - Interface to ticket type
    # ticket.version - Interface to ticket version objects

    def get_all_components(self) -> list[str]:
        """Get a list of all ticket component names"""
        return self._request_list_pod("ticket.component.getAll", str)

    def get_all_milestones(self) -> list[str]:
        """Get a list of all ticket milestone names"""
        return self._request_list_pod("ticket.milestone.getAll", str)

    def get_all_priorities(self) -> list[str]:
        """Get a list of all ticket priority names"""
        return self._request_list_pod("ticket.priority.getAll", str)

    def get_all_resolutions(self) -> list[str]:
        """Get a list of all ticket resolution names"""
        return self._request_list_pod("ticket.resolution.getAll", str)

    def get_all_severities(self) -> list[str]:
        """Get a list of all ticket severity names"""
        return self._request_list_pod("ticket.severity.getAll", str)

    def get_all_statuses(self) -> list[str]:
        """Returns all ticket states described by active workflow"""
        return self._request_list_pod("ticket.status.getAll", str)

    def get_all_types(self) -> list[str]:
        """Get a list of all ticket type names"""
        return self._request_list_pod("ticket.type.getAll", str)

    def get_all_versions(self) -> list[str]:
        """Get a list of all ticket version names"""
        return self._request_list_pod("ticket.version.getAll", str)

    def get_component[T: TracComponent](self, component_name: str, klass: type[T] = TracComponent) -> T:
        """Get a ticket component"""
        return self._request(TracRequest(method="ticket.component.get", params=[component_name]), klass)

    def get_milestone[T: TracMilestone](self, milestone_name: str, klass: type[T] = TracMilestone) -> T:
        """Get a ticket milestone"""
        return self._request(TracRequest(method="ticket.milestone.get", params=[milestone_name]), klass)

    def get_version[T: TracVersion](self, version_name: str, klass: type[T] = TracVersion) -> T:
        """Get a ticket priority"""
        return self._request(TracRequest(method="ticket.version.get", params=[version_name]), klass)

    # The following objects are just strings and do not need custom getters:
    #
    #   * priority
    #   * resolution
    #   * severity
    #   * status (deprecated)
    #   * type
    #

    # ticket - An interface to Trac's ticketing system
    def query_tickets(self, query: str = "", per_page: int = 0, page_number: int | None = None) -> list[int]:
        """
        Perform a ticket query, returning a list of ticket ID's. All queries will use stored settings for maximum
        number of results per page and paging options. Use max=n to define number of results to receive,
        and use page=n to page through larger result sets. Using max=0 will turn off paging and return all results.
        """
        pieces = (
            *((query,) if query != "" else ()),
            *((f"page={page_number}",) if page_number is not None else ()),
            f"max={per_page}",
        )
        return self._request(TracRequest(method="ticket.query", params=["&".join(pieces)]), list[int])

    def get_ticket_attachments(self, ticket_id: int) -> TracTicketAttachments:
        """
        Lists attachments for a given ticket. Returns (filename, description, size, time, author) for each attachment
        """
        return self._request(TracRequest(method="ticket.listAttachments", params=[ticket_id]), TracTicketAttachments)

    def get_ticket_changelog(self, ticket_id: int) -> TracTicketChangelog:
        """
        Return the changelog as a list of tuples of the form (time, author, field, oldvalue, newvalue, permanent).
        While the other tuple elements are quite self-explanatory, the permanent flag is used to distinguish
        collateral changes that are not yet immutable (like attachments, currently)
        """
        return self._request(TracRequest(method="ticket.changeLog", params=[ticket_id]), TracTicketChangelog)

    def get_ticket[T: TracTicket](self, ticket_id: int, klass: type[T] = TracTicket) -> TracTicketProperties[T]:
        """Fetch a ticket. Returns [id, time_created, time_changed, attributes]"""
        return self._request(TracRequest(method="ticket.get", params=[ticket_id]), TracTicketProperties[klass])

    # wiki - Superset of the WikiRPC API
    def get_all_wiki_pages(self) -> list[str]:
        """Returns a list of all pages. The result is an array of utf8 page names"""
        return self._request_list_pod("wiki.getAllPages", str)

    def wiki_to_html(self, text: str) -> str:
        """
        Render arbitrary Wiki text as HTML.

        For some migrations, the RPC server may need to be patched to force `escape_newlines=True`.
        """
        return self._request(TracRequest(method="wiki.wikiToHtml", params=[text]), str)

    # Utilities
    def get_ticket_last_field_change(
        self, ticket_id: int, field_name: str, new_value: str | None = None
    ) -> TracTicketChangelogEntry | None:
        """Get the changelog entry that represents the last time a given field was set to a particular value"""
        entry, *_ = [
            change
            for change in reversed(self.get_ticket_changelog(ticket_id))
            if change.field == field_name and (change.new_value == new_value if new_value is not None else True)
        ] + [None]
        return entry
