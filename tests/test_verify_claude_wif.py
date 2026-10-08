import contextlib
import importlib.util
import io
import unittest
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "verify_claude_wif", Path(__file__).resolve().parents[1] / "scripts/verify-claude-wif.py"
)
wif = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wif)


class WifVerificationTests(unittest.TestCase):
    def test_missing_variables_never_request_tokens(self):
        with patch.object(wif, "request_json") as request:
            with self.assertRaisesRegex(ValueError, "ANTHROPIC_SERVICE_ACCOUNT_ID"):
                wif.verify({})
            request.assert_not_called()

    def test_exchange_contract_and_no_token_logging(self):
        env = {
            "ANTHROPIC_FEDERATION_RULE_ID": "fdrl_test",
            "ANTHROPIC_ORGANIZATION_ID": "org_test",
            "ANTHROPIC_SERVICE_ACCOUNT_ID": "svac_test",
            "ANTHROPIC_WORKSPACE_ID": "wrkspc_test",
            "ACTIONS_ID_TOKEN_REQUEST_URL": "https://oidc.example/token?foo=bar",
            "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "runner-secret",
        }
        output = io.StringIO()
        with patch.object(wif, "request_json", side_effect=[
            {"value": "oidc-secret"}, {"access_token": "access-secret"}, {"data": []}
        ]) as request, contextlib.redirect_stdout(output):
            wif.verify(env)
        self.assertEqual(request.call_count, 3)
        self.assertIn("&audience=https%3A%2F%2Fapi.anthropic.com", request.call_args_list[0].args[0])
        exchange = request.call_args_list[1].args[2]
        self.assertEqual(exchange["service_account_id"], "svac_test")
        self.assertEqual(exchange["assertion"], "oidc-secret")
        self.assertIn("/v1/models?", request.call_args_list[2].args[0])
        self.assertNotIn("secret", output.getvalue())
