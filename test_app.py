import ipaddress
import unittest
from unittest.mock import patch

import app


class UrlSafetyTests(unittest.TestCase):
    def test_rejects_localhost(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            app.checked_url("http://localhost/secret")

    def test_rejects_loopback(self):
        with self.assertRaisesRegex(ValueError, "blocked"):
            app.checked_url("http://127.0.0.1/secret")

    def test_rejects_private_dns_resolution(self):
        with patch.object(app.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("10.2.3.4", 80))]):
            with self.assertRaisesRegex(ValueError, "blocked"):
                app.checked_url("http://public.example/media.mp4")

    def test_allows_public_dns_resolution(self):
        with patch.object(app.socket, "getaddrinfo", return_value=[(2, 1, 6, "", ("93.184.216.34", 80))]):
            url, host = app.checked_url("http://example.com/media.mp4")
        self.assertEqual(url, "http://example.com/media.mp4")
        self.assertEqual(host, "example.com")

    def test_rejects_non_http_schemes(self):
        with self.assertRaisesRegex(ValueError, "valid HTTP"):
            app.checked_url("file:///etc/passwd")


if __name__ == "__main__":
    unittest.main()
