from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

JsonDict = dict[str, Any]
Transport = Callable[[str, str, dict[str, str], Optional[bytes], float], Tuple[int, Any]]


class NeutronAIError(RuntimeError):
    def __init__(self, status: int, body: Any):
        super().__init__(f"Neutron AI request failed: {status}")
        self.status = status
        self.body = body


@dataclass(frozen=True)
class NeutronAIClient:
    base_url: str
    token: str | None = None
    nucleus_id: str | None = None
    tenant_id: str | None = None
    timeout_seconds: float = 30.0
    transport: Transport | None = None

    def __post_init__(self) -> None:
        base_url = self.base_url.strip().rstrip("/")
        if not base_url:
            raise ValueError("base_url is required")
        object.__setattr__(self, "base_url", base_url)
        if self.nucleus_id and self.tenant_id and self.nucleus_id != self.tenant_id:
            raise ValueError("nucleus_id and tenant_id must match when both are provided")

    def _request(self, path: str, method: str = "GET", body: Mapping[str, Any] | None = None) -> Any:
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "content-type": "application/json",
            "user-agent": "neutron-ai-python/0.3.0",
        }
        if self.token:
            headers["authorization"] = f"Bearer {self.token}"

        if self.transport:
            status, response_body = self.transport(f"{self.base_url}{path}", method, headers, payload, self.timeout_seconds)
            if status >= 400:
                raise NeutronAIError(status, response_body)
            return response_body

        request = Request(f"{self.base_url}{path}", data=payload, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                return json.loads(raw_body) if raw_body else None
        except HTTPError as error:
            raw_body = error.read().decode("utf-8")
            try:
                parsed_body: Any = json.loads(raw_body)
            except json.JSONDecodeError:
                parsed_body = raw_body
            raise NeutronAIError(error.code, parsed_body) from error

    def _with_nucleus(self, body: Mapping[str, Any]) -> JsonDict:
        body_nucleus_id = body.get("nucleusId") or body.get("nucleus_id")
        body_tenant_id = body.get("tenantId") or body.get("tenant_id")
        if body_nucleus_id and body_tenant_id and body_nucleus_id != body_tenant_id:
            raise ValueError("nucleusId and tenantId must match when both are provided")

        nucleus_id = body_nucleus_id or body_tenant_id or self.nucleus_id or self.tenant_id
        if not isinstance(nucleus_id, str) or not nucleus_id.strip():
            raise ValueError("nucleus_id is required")
        output = dict(body)
        output.pop("nucleus_id", None)
        output.pop("tenant_id", None)
        output["nucleusId"] = nucleus_id
        output["tenantId"] = nucleus_id
        return output

    def health(self) -> Any:
        return self._request("/health")

    def remember(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/remember", "POST", self._with_nucleus(body))

    def recall(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/recall", "POST", self._with_nucleus(body))

    def agent_context(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/agent-context", "POST", self._with_nucleus(body))

    def reflect(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/reflect", "POST", self._with_nucleus(body))

    def learn_skill(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/skills/learn", "POST", self._with_nucleus(body))

    def upsert_knowledge(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/kb/upsert", "POST", self._with_nucleus(body))

    def forget(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/forget", "POST", self._with_nucleus(body))

    def compact(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/compact", "POST", self._with_nucleus(body))

    def audit(
        self,
        scope_id: str,
        limit: int = 50,
        since: int | None = None,
        until: int | None = None,
        nucleus_id: str | None = None,
        tenant_id: str | None = None,
    ) -> Any:
        scoped = self._with_nucleus({"nucleus_id": nucleus_id, "tenant_id": tenant_id})
        query_params: dict[str, Any] = {
            "nucleusId": scoped["nucleusId"],
            "scopeId": scope_id,
            "limit": limit,
        }
        if since is not None:
            query_params["since"] = since
        if until is not None:
            query_params["until"] = until
        return self._request(f"/v1/memory/audit?{urlencode(query_params)}")

    def cache_stats(
        self,
        nucleus_id: str | None = None,
        agent_id: str | None = None,
        tenant_id: str | None = None,
    ) -> Any:
        scoped = self._with_nucleus({"nucleus_id": nucleus_id, "tenant_id": tenant_id})
        query_params = {"nucleusId": scoped["nucleusId"]}
        if agent_id:
            query_params["agentId"] = agent_id
        return self._request(f"/v1/memory/cache/stats?{urlencode(query_params)}")

    def invalidate_cache(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/cache/invalidate", "POST", self._with_nucleus(body))

    def warm_cache(self, body: Mapping[str, Any]) -> Any:
        return self._request("/v1/memory/cache/warm", "POST", self._with_nucleus(body))

    def list_mcp_tools(self) -> Any:
        return self._request("/mcp/tools")
