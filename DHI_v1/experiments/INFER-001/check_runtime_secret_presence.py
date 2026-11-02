"""Check only whether an Adaption API key is injected into this runtime.

This probe must never print, hash, serialize, or otherwise expose secret values.
It reports presence booleans only and performs no network request.
"""
from __future__ import annotations

import json
import os

names = ("ADAPTION_API_KEY", "DHI_ADAPTION_API_KEY")
result = {name: bool(os.environ.get(name)) for name in names}
print(json.dumps({
    "probe": "INFER-001-runtime-secret-presence",
    "secret_presence": result,
    "any_adaption_secret_present": any(result.values()),
    "network_requests_made": 0,
    "secret_values_emitted": False,
}, sort_keys=True))
