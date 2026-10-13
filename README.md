# neutron-ai-sdk

Python 3.10+ SDK and CLI helpers for Neutron AI memory and MCP operations. The PyPI distribution is `neutron-ai-sdk`; the import package and console command remain `neutron_ai` and `neutron-ai`.

## Install

```sh
pip install neutron-ai-sdk
```

## Usage

```python
from neutron_ai import NeutronAIClient

client = NeutronAIClient(
    base_url="https://neutronai.dev/api",
    token="your_token",
    nucleus_id="nucleus_demo",
)

client.remember({
    "scopeId": "user:derek",
    "type": "preference",
    "text": "Prefers concise implementation notes",
})
```

The client covers remember, recall, agent context, reflection, skills, knowledge bases, forget, compact, audit, context-cache operations, and MCP tool discovery. `tenant_id` remains a backwards-compatible alias; the SDK rejects a request when both aliases are present but differ.

## CLI

```sh
export NEUTRON_API_URL="https://neutronai.dev/api"
export NEUTRON_API_TOKEN="your_token"
export NEUTRON_NUCLEUS_ID="nucleus_demo"

neutron-ai health
neutron-ai recall --scope user:derek --query "working preferences"
```
