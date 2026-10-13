import unittest

from neutron_ai import NeutronAIClient, NeutronAIError, create_neutron_mcp_server_url


class NeutronAIClientTests(unittest.TestCase):
    def test_remember_injects_nucleus_legacy_alias_and_token(self):
        requests = []

        def transport(url, method, headers, payload, timeout_seconds):
            requests.append((url, method, headers, payload, timeout_seconds))
            return 200, {"memoryId": "mem_1", "accepted": True, "warnings": []}

        client = NeutronAIClient("https://api.example.test", token="secret", nucleus_id="nucleus_demo", transport=transport)
        response = client.remember({"scopeId": "user:derek", "type": "preference", "text": "hello"})

        self.assertEqual(response["memoryId"], "mem_1")
        self.assertEqual(requests[0][2]["authorization"], "Bearer secret")
        self.assertIn(b'"nucleusId": "nucleus_demo"', requests[0][3])
        self.assertIn(b'"tenantId": "nucleus_demo"', requests[0][3])

    def test_mismatched_nucleus_aliases_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "must match"):
            NeutronAIClient("https://api.example.test", nucleus_id="nucleus_a", tenant_id="nucleus_b")

        client = NeutronAIClient("https://api.example.test", nucleus_id="nucleus_a", transport=lambda *_: (200, {}))
        with self.assertRaisesRegex(ValueError, "must match"):
            client.remember({"nucleusId": "nucleus_a", "tenantId": "nucleus_b"})

    def test_empty_base_url_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "base_url is required"):
            NeutronAIClient("  ")

    def test_error_preserves_status_and_body(self):
        def transport(url, method, headers, payload, timeout_seconds):
            return 409, {"error": {"code": "conflict", "message": "No"}}

        client = NeutronAIClient("https://api.example.test", nucleus_id="nucleus_demo", transport=transport)
        with self.assertRaises(NeutronAIError) as error_context:
            client.cache_stats()

        self.assertEqual(error_context.exception.status, 409)
        self.assertEqual(error_context.exception.body["error"]["code"], "conflict")

    def test_mcp_url_normalizes_path(self):
        self.assertEqual(create_neutron_mcp_server_url("https://mcp.neutronai.dev/", "mcp"), "https://mcp.neutronai.dev/mcp")


if __name__ == "__main__":
    unittest.main()
