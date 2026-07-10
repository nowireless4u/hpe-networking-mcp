"""Unit tests for the new Central MRT endpoint wrappers.

Covers the tools added for the 2026-07 MRT OAS refresh: application /
website category + security-risk usage reads, gateway modem stats, the
reporting metadata / single-report / create-report tools, and the
notification-rule read + manage surface.

Pins the contract that matters and has bitten us before: **kebab-case
query params** (the #564 class of bug), the request-body **envelope
wrappers** (``{"report": …}`` / ``{"notificationRuleInput": …}``), the
method-per-action mapping (POST/PATCH/DELETE), and the write-tool
validation (ToolError on missing id/payload).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

pytestmark = pytest.mark.unit


def _ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.lifespan_context = {"central_conn": MagicMock()}
    return ctx


def _ok(msg: object | None = None) -> dict:
    return {"code": 200, "msg": msg if msg is not None else {"ok": True}}


_APPS_RETRY = "hpe_networking_mcp.platforms.central.tools.mrt_applications.retry_central_command"
_GW_RETRY = "hpe_networking_mcp.platforms.central.tools.mrt_gateway.retry_central_command"
_REP_RETRY = "hpe_networking_mcp.platforms.central.tools.mrt_reporting.retry_central_command"
_NOTIF_RETRY = "hpe_networking_mcp.platforms.central.tools.mrt_notifications.retry_central_command"


# ---------------------------------------------------------------------------
# mrt_applications — usage/security reads (kebab-case params)
# ---------------------------------------------------------------------------


class TestApplicationVisibilityReads:
    @patch(_APPS_RETRY)
    async def test_application_categories_kebab_params(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_applications import central_get_application_categories

        mock_retry.return_value = _ok({"items": [], "count": 0, "offset": 0, "total": 0})
        await central_get_application_categories(
            _ctx(), start_at="2026-07-01T00:00:00Z", end_at="2026-07-02T00:00:00Z", site_id="s1", top=5
        )
        kw = mock_retry.call_args.kwargs
        assert kw["api_method"] == "GET"
        assert kw["api_path"] == "network-monitoring/v1/application-categories"
        # kebab-case keys, snake-case Python args — the #564 trap.
        assert kw["api_params"]["start-at"] == "2026-07-01T00:00:00Z"
        assert kw["api_params"]["end-at"] == "2026-07-02T00:00:00Z"
        assert kw["api_params"]["site-id"] == "s1"
        assert kw["api_params"]["top"] == 5
        # unset optionals must not leak into the query.
        assert "client-id" not in kw["api_params"]
        assert "serial-number" not in kw["api_params"]

    @patch(_APPS_RETRY)
    async def test_website_categories_path(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_applications import central_get_website_categories

        mock_retry.return_value = _ok()
        await central_get_website_categories(_ctx(), start_at="a", end_at="b")
        assert mock_retry.call_args.kwargs["api_path"] == "network-monitoring/v1/website-categories"

    @patch(_APPS_RETRY)
    async def test_security_risks_has_no_top_param(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_applications import central_get_security_risks

        mock_retry.return_value = _ok()
        await central_get_security_risks(_ctx(), start_at="a", end_at="b", limit=10)
        kw = mock_retry.call_args.kwargs
        assert kw["api_path"] == "network-monitoring/v1/security-risks"
        assert kw["api_params"]["limit"] == 10
        assert "top" not in kw["api_params"]  # security-risks endpoint has no `top`


# ---------------------------------------------------------------------------
# mrt_gateway — modem stats
# ---------------------------------------------------------------------------


class TestGatewayModemStats:
    @patch(_GW_RETRY)
    async def test_modem_stats_path_and_optional_site(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_gateway import central_get_gateway_modem_stats

        mock_retry.return_value = _ok({"rssi": "-70"})
        await central_get_gateway_modem_stats(_ctx(), serial_number="CN123")
        kw = mock_retry.call_args.kwargs
        assert kw["api_method"] == "GET"
        assert kw["api_path"] == "network-monitoring/v1/gateways/CN123/modem-stat"
        assert kw["api_params"] == {}  # no site-id → empty

        await central_get_gateway_modem_stats(_ctx(), serial_number="CN123", site_id="site-9")
        assert mock_retry.call_args.kwargs["api_params"] == {"site-id": "site-9"}


# ---------------------------------------------------------------------------
# mrt_reporting — metadata, single report, create
# ---------------------------------------------------------------------------


class TestReportingTools:
    @patch(_REP_RETRY)
    async def test_reports_metadata_params(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_reporting import central_get_reports_metadata

        mock_retry.return_value = _ok()
        await central_get_reports_metadata(_ctx(), report_type="client", kpi_widget="usage")
        kw = mock_retry.call_args.kwargs
        assert kw["api_path"] == "network-reporting/v1/reports-meta"
        assert kw["api_params"] == {"type": "client", "kpi-widget": "usage"}

    @patch(_REP_RETRY)
    async def test_get_single_report_path(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_reporting import central_get_report

        mock_retry.return_value = _ok()
        await central_get_report(_ctx(), report_id="r-42")
        assert mock_retry.call_args.kwargs["api_path"] == "network-reporting/v1/reports/r-42"

    @patch(_REP_RETRY)
    async def test_create_report_wraps_body(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_reporting import central_create_report

        mock_retry.return_value = {"code": 201, "msg": {"report": {"id": "r-99"}}}
        report = {"name": "Weekly", "type": "client"}
        result = await central_create_report(_ctx(), report=report)
        kw = mock_retry.call_args.kwargs
        assert kw["api_method"] == "POST"
        assert kw["api_path"] == "network-reporting/v1/reports"
        assert kw["api_data"] == {"report": report}  # wrapped envelope
        assert result["status"] == "success"


# ---------------------------------------------------------------------------
# mrt_notifications — reads + manage (create/update/delete)
# ---------------------------------------------------------------------------


class TestNotificationRules:
    @patch(_NOTIF_RETRY)
    async def test_list_rules_pagination(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_get_notification_rules

        mock_retry.return_value = _ok()
        await central_get_notification_rules(_ctx(), limit=50, offset=10)
        kw = mock_retry.call_args.kwargs
        assert kw["api_path"] == "network-notifications/v1/notification-rules"
        assert kw["api_params"] == {"limit": 50, "offset": 10}

    @patch(_NOTIF_RETRY)
    async def test_get_rule_path(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_get_notification_rule

        mock_retry.return_value = _ok()
        await central_get_notification_rule(_ctx(), rule_id="nr-1")
        assert mock_retry.call_args.kwargs["api_path"] == "network-notifications/v1/notification-rules/nr-1"

    @patch(_NOTIF_RETRY)
    async def test_manage_create_wraps_body(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_manage_notification_rule

        mock_retry.return_value = {"code": 201, "msg": {"id": "nr-2"}}
        rule = {"name": "high-sev", "sourceTypes": ["ALERTS"]}
        await central_manage_notification_rule(_ctx(), action_type="create", payload=rule)
        kw = mock_retry.call_args.kwargs
        assert kw["api_method"] == "POST"
        assert kw["api_path"] == "network-notifications/v1/notification-rules"
        assert kw["api_data"] == {"notificationRuleInput": rule}

    @patch(_NOTIF_RETRY)
    async def test_manage_delete_method(self, mock_retry):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_manage_notification_rule

        mock_retry.return_value = _ok()
        await central_manage_notification_rule(_ctx(), action_type="delete", rule_id="nr-4")
        kw = mock_retry.call_args.kwargs
        assert kw["api_method"] == "DELETE"
        assert kw["api_path"] == "network-notifications/v1/notification-rules/nr-4"

    async def test_manage_create_requires_payload(self):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_manage_notification_rule

        with pytest.raises(ToolError) as e:
            await central_manage_notification_rule(_ctx(), action_type="create")
        assert e.value.args[0]["status_code"] == 400

    async def test_manage_delete_requires_rule_id(self):
        from hpe_networking_mcp.platforms.central.tools.mrt_notifications import central_manage_notification_rule

        with pytest.raises(ToolError) as e:
            await central_manage_notification_rule(_ctx(), action_type="delete")
        assert e.value.args[0]["status_code"] == 400
