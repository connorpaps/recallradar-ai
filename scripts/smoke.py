from __future__ import annotations

import argparse
import json
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen


def fetch(url: str, timeout: float) -> tuple[int, object]:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
        try:
            return response.status, json.loads(body)
        except json.JSONDecodeError:
            return response.status, body


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a read-only RecallRadar deployment smoke test.")
    parser.add_argument("--api", required=True, help="Backend base URL, for example https://api.example.com")
    parser.add_argument("--frontend", required=True, help="Frontend URL, for example https://app.example.com")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    checks = {
        "backend_health": f"{args.api.rstrip('/')}/health",
        "backend_dashboard": f"{args.api.rstrip('/')}/dashboard/summary",
        "frontend_home": args.frontend.rstrip("/") + "/",
    }
    failures = []
    for name, url in checks.items():
        try:
            status, payload = fetch(url, args.timeout)
            ok = status == 200 and (name != "backend_health" or payload == {"status": "ok"})
            print(f"{name}: {'ok' if ok else 'failed'} HTTP {status}")
            if not ok:
                failures.append(name)
        except (OSError, URLError) as error:
            print(f"{name}: failed {error}")
            failures.append(name)

    if failures:
        print(f"Smoke test failed: {', '.join(failures)}")
        return 1
    print("Smoke test passed: health, dashboard, and frontend home are reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
