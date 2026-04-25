# Platform Template

Canonical scaffold for adding a new platform to the HPE Networking MCP server. Anything outside `platforms/_template/` follows the same patterns as Mist / Central / Apstra — copy from here, adapt the auth, fill in the tools.

The template is a real Python package: `import hpe_networking_mcp.platforms._template` succeeds. It just isn't wired into `server.py:create_server`, so it never registers any tool at runtime. That's deliberate — it lets `tests/unit/test_platform_template.py` import it and assert structural conventions without polluting the live tool surface.

## How to use the template

Adding `myplatform` to the server is a five-step copy:

### 1. Copy the template directory

```bash
cp -r src/hpe_networking_mcp/platforms/_template src/hpe_networking_mcp/platforms/myplatform
```

Then, inside the new directory, search-replace:
- `_template` → `myplatform` (snake_case identifiers + module paths)
- `_TEMPLATE` → `_MYPLATFORM`  (constants)
- `Template` → `Myplatform` (class names if any are added later)

The two example tools (`tools/example_read.py`, `tools/example_write.py`) demonstrate the read and write patterns. **Delete them once you've added real tools** — they're for reference, not production code.

### 2. Add the secret loader to `src/hpe_networking_mcp/config.py`

Three edits:

```python
@dataclass
class MyplatformSecrets:
    api_token: str
    # add more fields as needed


# in ServerConfig:
enable_myplatform_write_tools: bool = False
myplatform: MyplatformSecrets | None = None

# in enabled_platforms property:
if self.myplatform:
    platforms.append("myplatform")


def _load_myplatform() -> MyplatformSecrets | None:
    api_token = _read_secret("myplatform_api_token")
    if not api_token:
        logger.info("Myplatform: disabled (myplatform_api_token secret not found)")
        return None
    logger.info("Myplatform: credentials loaded (token: {})", mask_secret(api_token))
    return MyplatformSecrets(api_token=api_token)


# in load_config():
myplatform = _load_myplatform()
# ...
return ServerConfig(
    ...,
    myplatform=myplatform,
    enable_myplatform_write_tools=enable_myplatform_write,
)
```

Plus an env var for write-tool gating:

```python
enable_myplatform_write = os.getenv("ENABLE_MYPLATFORM_WRITE_TOOLS", "false").lower() in _truthy
```

### 3. Wire the lifespan + tool registration in `src/hpe_networking_mcp/server.py`

In `lifespan()`:

```python
if config.myplatform:
    try:
        from hpe_networking_mcp.platforms.myplatform.client import MyplatformClient
        context["myplatform_client"] = MyplatformClient(config.myplatform)
        context["myplatform_config"] = config.myplatform
    except Exception as e:
        logger.warning("Myplatform: failed to initialize — {}", e)
        context["myplatform_client"] = None
        context["myplatform_config"] = None
else:
    context["myplatform_client"] = None
    context["myplatform_config"] = None
```

In the lifespan teardown:

```python
client = context.get("myplatform_client")
if client is not None:
    await client.aclose()
```

In `create_server()`:

```python
if config.myplatform:
    _register_myplatform_tools(mcp, config)


def _register_myplatform_tools(mcp: FastMCP, config: ServerConfig) -> None:
    """Register all Myplatform platform tools."""
    from hpe_networking_mcp.platforms.myplatform import register_tools
    count = register_tools(mcp, config)
    logger.info("Myplatform: registered {} tools", count)
```

And the Visibility transform for write-tool gating:

```python
if not config.enable_myplatform_write_tools:
    mcp.add_transform(Visibility(False, tags={"myplatform_write", "myplatform_write_delete"}, components={"tool"}))
```

### 4. Add the health probe in `src/hpe_networking_mcp/platforms/health.py`

```python
async def _probe_myplatform(ctx: Context) -> dict[str, Any]:
    client = ctx.lifespan_context.get("myplatform_client")
    if client is None:
        return {"status": "unavailable", "message": "Myplatform is not configured or failed to initialize"}
    try:
        await client.health_check()
        return {"status": "ok", "message": "Myplatform API reachable"}
    except Exception as e:
        return {"status": "degraded", "message": f"Myplatform probe failed: {e}"}
```

Then add `"myplatform"` to `_ALL_PLATFORMS` and `_PROBES`.

### 5. Add the secret template + a unit test

```bash
echo "your-token-here" > secrets/myplatform_api_token.example
cp tests/unit/test_axis_dynamic_mode.py tests/unit/test_myplatform_dynamic_mode.py
# adapt the imports + assertions
```

## What the template captures

These patterns are uniform across every existing platform — change them in the template and every future copy gets the fix:

| Concern | File | Why it's templated |
|---|---|---|
| Tool registry shim with `dynamic_managed` tag | `_registry.py` | Visibility transform requires this tag on every dynamic-mode tool |
| Per-tool ToolAnnotations (`READ_ONLY` / `WRITE` / `WRITE_DELETE`) | `tools/__init__.py` | MCP clients use these to render confirmation UX |
| `register_tools(mcp, config)` + importlib loop | `__init__.py` | Single-source registration so meta-tools and Visibility both work |
| `format_http_error` helper | `client.py` | Consistent error shape across tools |
| `get_<platform>_client()` ctx accessor with 503 on missing client | `client.py` | Fail-fast when the platform isn't configured |

## What's NOT templated

These vary legitimately and are left as comments / extension points in `client.py`:

- **Auth flavor** — bearer token (default), OAuth2 client_credentials, username/password. The template ships with bearer; comments show where to swap.
- **HTTP layer** — direct `httpx` (template default) or a vendor SDK wrapper. If the platform has a maintained SDK (e.g. mistapi, pycentral, pyclearpass), prefer that over hand-rolled httpx.
- **Pagination** — RFC 5988 `Link` headers, OData `$top`/`$skip`, opaque cursors. Different APIs do this differently.
- **Elicitation pattern** — write tools call `confirm_write(ctx, ...)` from `middleware/elicitation.py`. Pattern shown in `tools/example_write.py`.

## Validation

The template stays honest because `tests/unit/test_platform_template.py` imports it and asserts:

- The `@tool` decorator is exported from `_registry.py`
- `READ_ONLY`, `WRITE`, `WRITE_DELETE` are exported from `tools/__init__.py`
- `register_tools(mcp, config)` exists and is callable
- The example tool files import successfully (no broken references)

If you change the conventions in a real platform, update the template + the test in the same PR.
