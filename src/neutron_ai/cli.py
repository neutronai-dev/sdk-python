from __future__ import annotations

import argparse
import json
import os
from typing import Sequence

from .client import NeutronAIClient


def _client_from_env() -> NeutronAIClient:
    base_url = os.environ.get("NEUTRON_API_URL")
    if not base_url:
        raise SystemExit("NEUTRON_API_URL is required")
    return NeutronAIClient(
        base_url=base_url,
        token=os.environ.get("NEUTRON_API_TOKEN"),
        nucleus_id=os.environ.get("NEUTRON_NUCLEUS_ID"),
        tenant_id=os.environ.get("NEUTRON_TENANT_ID"),
    )


def _print_json(value: object) -> None:
    print(json.dumps(value, indent=2))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="neutron-ai")
    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("health")

    remember = subcommands.add_parser("remember")
    remember.add_argument("--scope", required=True)
    remember.add_argument("--text", required=True)
    remember.add_argument("--type", default="preference")

    recall = subcommands.add_parser("recall")
    recall.add_argument("--scope", required=True)
    recall.add_argument("--query", required=True)
    recall.add_argument("--limit", type=int, default=10)

    context = subcommands.add_parser("context")
    context.add_argument("--scope", required=True)
    context.add_argument("--task", required=True)

    subcommands.add_parser("mcp-tools")

    args = parser.parse_args(argv)
    client = _client_from_env()

    if args.command == "health":
        _print_json(client.health())
    elif args.command == "remember":
        _print_json(client.remember({"scopeId": args.scope, "type": args.type, "text": args.text}))
    elif args.command == "recall":
        _print_json(client.recall({"scopeIds": args.scope.split(","), "query": args.query, "limit": args.limit}))
    elif args.command == "context":
        _print_json(client.agent_context({"scopeIds": args.scope.split(","), "task": args.task}))
    elif args.command == "mcp-tools":
        _print_json(client.list_mcp_tools())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
