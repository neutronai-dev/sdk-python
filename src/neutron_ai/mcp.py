from __future__ import annotations

from typing import Any

neutron_mcp_tools: list[dict[str, Any]] = [
    {"name": "memory_agent_context", "description": "Build a scoped Neutron AI agent context pack.", "readOnlyHint": True, "destructiveHint": False},
    {"name": "memory_recall", "description": "Recall relevant scoped Neutron AI memory summaries.", "readOnlyHint": True, "destructiveHint": False},
    {"name": "memory_remember", "description": "Store compressed scoped memory for Neutron AI agents.", "readOnlyHint": False, "destructiveHint": False},
    {"name": "memory_reflect", "description": "Store post-task experience and reusable tool lessons.", "readOnlyHint": False, "destructiveHint": False},
    {"name": "memory_cache_stats", "description": "Return context-cache metrics.", "readOnlyHint": True, "destructiveHint": False},
    {"name": "memory_cache_warm", "description": "Prebuild safe context packs for repeated agent workflows.", "readOnlyHint": False, "destructiveHint": False},
    {"name": "memory_cache_invalidate", "description": "Invalidate cached context packs by scope or cache key.", "readOnlyHint": False, "destructiveHint": True},
    {"name": "memory_forget", "description": "Tombstone memory and remove external references.", "readOnlyHint": False, "destructiveHint": True},
    {"name": "memory_compact", "description": "Expire and deduplicate memories in a scope.", "readOnlyHint": False, "destructiveHint": True},
]


def create_neutron_mcp_server_url(base_url: str, path: str = "/mcp") -> str:
    normalized_base_url = base_url.rstrip("/")
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{normalized_base_url}{normalized_path}"


def create_openai_mcp_tool(
    server_url: str,
    server_label: str = "neutron_memory",
    server_description: str | None = None,
    authorization: str | None = None,
    headers: dict[str, str] | None = None,
    allowed_tools: list[str] | None = None,
    require_approval: str | dict[str, Any] = "never",
) -> dict[str, Any]:
    tool: dict[str, Any] = {
        "type": "mcp",
        "server_label": server_label,
        "server_url": server_url,
        "require_approval": require_approval,
    }
    if server_description:
        tool["server_description"] = server_description
    if authorization:
        tool["authorization"] = authorization
    if headers:
        tool["headers"] = headers
    if allowed_tools:
        tool["allowed_tools"] = allowed_tools
    return tool


def create_anthropic_mcp_connector(
    server_url: str,
    server_label: str = "neutron_memory",
    authorization: str | None = None,
    default_config: dict[str, Any] | None = None,
    tool_configs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    server: dict[str, Any] = {"type": "url", "url": server_url, "name": server_label}
    if authorization:
        server["authorization_token"] = authorization

    toolset: dict[str, Any] = {"type": "mcp_toolset", "mcp_server_name": server_label}
    if default_config:
        toolset["default_config"] = default_config
    if tool_configs:
        toolset["configs"] = tool_configs

    return {"mcp_servers": [server], "tools": [toolset], "betas": ["mcp-client-2025-11-20"]}
