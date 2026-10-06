"""Offline HTTP boundary tests; no credentials or network calls."""
import io
import unittest
import urllib.error
from unittest.mock import patch, MagicMock
from test_advisor import collector


class TransportTests(unittest.TestCase):
    def response(self, body):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = body
        return response

    def test_valid_json_and_timeout(self):
        opener = MagicMock()
        opener.open.return_value = self.response(b'{"ok":true}')
        with patch.object(collector.urllib.request, 'build_opener', return_value=opener):
            self.assertEqual(collector.fetch_json(collector.GMI_URL, 'fixture-only'), {'ok': True})
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertEqual(request.full_url, collector.GMI_URL)
        self.assertEqual(opener.open.call_args.kwargs['timeout'], 30)

    def test_http_error_does_not_echo_body_or_key(self):
        opener = MagicMock()
        opener.open.side_effect = urllib.error.HTTPError(collector.GMI_URL, 401, 'secret-marker', {}, io.BytesIO(b'secret-marker'))
        with patch.object(collector.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaises(collector.EvidenceError) as error:
                collector.fetch_json(collector.GMI_URL, 'secret-marker')
        self.assertEqual(str(error.exception), 'HTTP 401; no automatic retry')
        self.assertEqual(opener.open.call_count, 1)

    def test_redirect_never_forwards_credential(self):
        with self.assertRaises(collector.EvidenceError):
            collector.NoRedirect().redirect_request(None, None, 302, 'Found', {}, 'https://example.test/steal')

    def test_invalid_json_rejected(self):
        opener = MagicMock()
        opener.open.return_value = self.response(b'<html>error</html>')
        with patch.object(collector.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(collector.EvidenceError, 'not valid JSON'):
                collector.fetch_json(collector.GMI_URL, 'fixture-only')

    def test_size_limit(self):
        opener = MagicMock()
        opener.open.return_value = self.response(b'x' * (collector.MAX_BYTES + 1))
        with patch.object(collector.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaisesRegex(collector.EvidenceError, 'too large'):
                collector.fetch_json(collector.GMI_URL, 'fixture-only')

    def test_network_error_redacted(self):
        opener = MagicMock()
        opener.open.side_effect = urllib.error.URLError('secret-marker')
        with patch.object(collector.urllib.request, 'build_opener', return_value=opener):
            with self.assertRaises(collector.EvidenceError) as error:
                collector.fetch_json(collector.GMI_URL, 'fixture-only')
        self.assertNotIn('secret-marker', str(error.exception))


if __name__ == '__main__':
    unittest.main()
