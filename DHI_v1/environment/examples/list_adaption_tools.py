"""List Adaption's live host-side connector catalogue and account availability.

Set ADAPTION_API_KEY (or DHI_ADAPTION_API_KEY) first. Results distinguish
available connectors from missing scopes, plan access, disabled or unimplemented
capabilities; the catalogue call itself does not execute any connector action.
"""
from __future__ import annotations

import json
import os

from DHI_v1.environment.adaption_responses import AdaptionResponsesClient


def main() -> int:
    api_key = os.environ.get("ADAPTION_API_KEY") or os.environ.get("DHI_ADAPTION_API_KEY") or ""
    base_url = os.environ.get("DHI_ADAPTION_API_BASE_URL", "https://api.prod.adaptionlabs.ai")
    organization_id = os.environ.get("DHI_ADAPTION_ORGANIZATION_ID") or None
    if not api_key:
        raise SystemExit("Set ADAPTION_API_KEY (or DHI_ADAPTION_API_KEY) first.")
    client = AdaptionResponsesClient(
        api_key=api_key, base_url=base_url, organization_id=organization_id
    )
    tools = client.list_tools_catalogue()
    print(json.dumps(tools, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
