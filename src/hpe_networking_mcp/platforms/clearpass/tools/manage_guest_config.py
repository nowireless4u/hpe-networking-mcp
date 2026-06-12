"""ClearPass guest configuration write tools (templates, weblogins, settings)."""

from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from fastmcp.exceptions import ToolError
from pydantic import Field

from hpe_networking_mcp.platforms._common.annotations import Capability
from hpe_networking_mcp.platforms._common.url import path_seg
from hpe_networking_mcp.platforms.clearpass._registry import tool
from hpe_networking_mcp.platforms.clearpass.client import get_clearpass_client


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_pass_template(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Template config payload. For delete: empty dict {}.")],
    template_id: Annotated[str | None, Field(description="Template ID (required for update/replace/delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass guest pass template.

    Pass templates define the layout and content of digital passes or printed receipts
    for guest accounts.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        template_id: Numeric ID. Required for update/replace/delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "replace", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/template/pass", json_body=payload)
        if not template_id:
            raise ToolError({"status_code": 400, "message": "template_id is required for update/replace/delete."})
        if action_type == "update":
            return await client.request("patch", f"/template/pass/{path_seg(template_id)}", json_body=payload)
        if action_type == "replace":
            return await client.request("put", f"/template/pass/{path_seg(template_id)}", json_body=payload)
        return await client.request("delete", f"/template/pass/{path_seg(template_id)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing pass template: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_print_template(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Template config payload. For delete: empty dict {}.")],
    template_id: Annotated[str | None, Field(description="Template ID (required for update/replace/delete).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass guest print template.

    Print templates define the layout for printed guest credentials.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        template_id: Numeric ID. Required for update/replace/delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "replace", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/template/print", json_body=payload)
        if not template_id:
            raise ToolError({"status_code": 400, "message": "template_id is required for update/replace/delete."})
        if action_type == "update":
            return await client.request("patch", f"/template/print/{path_seg(template_id)}", json_body=payload)
        if action_type == "replace":
            return await client.request("put", f"/template/print/{path_seg(template_id)}", json_body=payload)
        return await client.request("delete", f"/template/print/{path_seg(template_id)}")
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing print template: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_weblogin_page(
    ctx: Context,
    action_type: Annotated[str, Field(description="Action: 'create', 'update', 'replace', or 'delete'.")],
    payload: Annotated[dict, Field(description="Weblogin page config payload. For delete: empty dict {}.")],
    page_id: Annotated[str | None, Field(description="Weblogin page ID (for update/replace/delete).")] = None,
    page_name: Annotated[str | None, Field(description="Weblogin page name (alternative to ID).")] = None,
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Create, update, replace, or delete a ClearPass weblogin (captive portal) page.

    Weblogin pages define the captive portal experience for guest and BYOD users.

    Args:
        action_type: Operation — 'create', 'update', 'replace', or 'delete'.
        payload: JSON config body. Required for create/update/replace. Empty dict for delete.
        page_id: Numeric ID. Required for update/replace/delete (or use page_name).
        page_name: Page name. Alternative to page_id for update/replace/delete.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if action_type not in ("create", "update", "replace", "delete"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid action_type '{action_type}'. Must be 'create', 'update', 'replace', or 'delete'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if action_type == "create":
            return await client.request("post", "/weblogin", json_body=payload)
        if not page_id and not page_name:
            raise ToolError(
                {"status_code": 400, "message": "Either page_id or page_name is required for update/replace/delete."}
            )
        if action_type == "delete":
            if page_id:
                return await client.request("delete", f"/weblogin/{path_seg(page_id)}")
            return await client.request("delete", f"/weblogin/page-name/{path_seg(page_name)}")
        # update or replace
        path_suffix = f"/{path_seg(page_id)}" if page_id else f"/page-name/{path_seg(page_name)}"
        method = "patch" if action_type == "update" else "put"
        return await client.request(method, f"/weblogin{path_suffix}", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing weblogin page: {e}"}) from e


@tool(capability=Capability.WRITE_DELETE)
async def clearpass_manage_guest_settings(
    ctx: Context,
    setting_type: Annotated[str, Field(description="Setting type: 'authentication' or 'manager'.")],
    payload: Annotated[dict, Field(description="Settings payload to apply.")],
    confirmed: Annotated[
        bool,
        Field(
            description="Fallback confirmation flag — honored only when the client cannot show a "
            "confirmation prompt (the universal gate prompts otherwise)."
        ),
    ] = False,
) -> dict | str:
    """Update ClearPass guest authentication or guest manager settings.

    Args:
        setting_type: Which settings to update — 'authentication' or 'manager'.
        payload: JSON settings body to apply.
        confirmed: Fallback confirmation flag — honored only when the client cannot show a
            confirmation prompt (the universal gate prompts otherwise).
    """
    if setting_type not in ("authentication", "manager"):
        raise ToolError(
            {
                "status_code": 400,
                "message": f"Invalid setting_type '{setting_type}'. Must be 'authentication' or 'manager'.",
            }
        )

    try:
        client = await get_clearpass_client()

        if setting_type == "authentication":
            return await client.request("patch", "/guest/authentication", json_body=payload)
        return await client.request("patch", "/guestmanager", json_body=payload)
    except ToolError:
        raise
    except Exception as e:
        raise ToolError({"status_code": 502, "message": f"Error managing guest settings: {e}"}) from e
