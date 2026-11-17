"""A page cut off by the network is retried, it does not stop the download."""

import http.client
import shutil
import tempfile
import unittest
from unittest import mock

from qnx_portmap import refresh


class _Resp(object):
    def __init__(self, body):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class DownloadRetryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)

    def _downloader(self):
        return refresh.Downloader(self.tmp, delay=0, retries=3)

    def test_incomplete_read_is_retried(self):
        calls = {"n": 0}

        def fake_urlopen(req, timeout=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise http.client.IncompleteRead(b"x" * 10, 90)
            return _Resp(b"<html>page</html>")

        with mock.patch.object(refresh.urllib.request, "urlopen", fake_urlopen), \
                mock.patch.object(refresh.time, "sleep", lambda s: None):
            body = self._downloader().fetch("https://www.qnx.com/a.html")
        self.assertEqual(body, "<html>page</html>")
        self.assertEqual(calls["n"], 2)

    def test_incomplete_read_every_time_is_a_failure_not_a_crash(self):
        def fake_urlopen(req, timeout=None):
            raise http.client.IncompleteRead(b"", 100)

        dl = self._downloader()
        with mock.patch.object(refresh.urllib.request, "urlopen", fake_urlopen), \
                mock.patch.object(refresh.time, "sleep", lambda s: None):
            body = dl.fetch("https://www.qnx.com/b.html")
        self.assertEqual(body, "")
        self.assertEqual(len(dl.failed), 1)


if __name__ == "__main__":
    unittest.main()
