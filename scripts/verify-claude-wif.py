#!/usr/bin/env python3
"""Verify GitHub OIDC -> Claude WIF -> read-only Models API without inference."""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def request_json(url, headers, payload=None):
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read(1_000_000))


def verify(env):
    names = (
        "ANTHROPIC_FEDERATION_RULE_ID", "ANTHROPIC_ORGANIZATION_ID",
        "ANTHROPIC_SERVICE_ACCOUNT_ID", "ANTHROPIC_WORKSPACE_ID",
        "ACTIONS_ID_TOKEN_REQUEST_URL", "ACTIONS_ID_TOKEN_REQUEST_TOKEN",
    )
    missing = [name for name in names if not env.get(name)]
    if missing:
        raise ValueError("Missing variables: " + ", ".join(missing))
    oidc_url = env["ACTIONS_ID_TOKEN_REQUEST_URL"]
    separator = "&" if "?" in oidc_url else "?"
    oidc = request_json(
        oidc_url + separator + urllib.parse.urlencode({"audience": "https://api.anthropic.com"}),
        {"Authorization": "Bearer " + env["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]},
    )["value"]
    # D5: never log or persist tokens; costs post-mortem payload inspection.
    # Escape hatch: inspect provider authentication history using request IDs.
    print("GitHub OIDC: obtained (token hidden)")
    result = request_json(
        "https://api.anthropic.com/v1/oauth/token",
        {"Content-Type": "application/json", "anthropic-version": "2023-06-01"},
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": oidc,
            "federation_rule_id": env["ANTHROPIC_FEDERATION_RULE_ID"],
            "organization_id": env["ANTHROPIC_ORGANIZATION_ID"],
            "service_account_id": env["ANTHROPIC_SERVICE_ACCOUNT_ID"],
            "workspace_id": env["ANTHROPIC_WORKSPACE_ID"],
        },
    )
    access_token = result["access_token"]
    if not isinstance(access_token, str) or not access_token:
        raise ValueError("Token exchange returned no access token")
    print("Claude WIF: token exchange succeeded (token hidden)")
    models = request_json(
        "https://api.anthropic.com/v1/models?limit=1",
        {"Authorization": "Bearer " + access_token, "anthropic-version": "2023-06-01"},
    )
    if not isinstance(models.get("data"), list):
        raise ValueError("Models API response is invalid")
    print("Models API: authorized; no model generation requested")


def main():
    try:
        verify(os.environ)
    except urllib.error.HTTPError as exc:
        # Provider bodies may echo credentials; report only status and request ID.
        print(f"WIF verification failed: HTTP {exc.code}; request-id={exc.headers.get('request-id', 'unknown')}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (urllib.error.URLError, TimeoutError, KeyError, TypeError):
        print("WIF verification failed: transport or response format error", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
