"""List model IDs available to the current Adaption API key.

Set ADAPTION_API_KEY (or DHI_ADAPTION_API_KEY) first. Prefer an exact returned
hosted model ID for fair base-model screening. stack:<slug> calls a saved
Inference Stack and may add its configured tools, datasets, and memory.
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
    models = client.list_models(hosted_only=True)
    print(json.dumps(models, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
