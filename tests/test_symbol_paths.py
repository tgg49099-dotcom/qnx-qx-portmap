"""A file name is not an API symbol (Studio review, 23/11/2026).

The 8.0 migration guide, page bsps.html, lists BSP source files such as
``i2c/imx8/recv.c`` and ``i2c/imx8/send.c``. Before this fix, ``recv`` and
``send`` were reported as "cited by the official migration guide" because
of those file names: a false warning on two of the most common calls.
"""

import unittest

from qnx_portmap.extract import sentences_with, symbol_regex

BSPS = ("i2c i2c/imx8/common.c i2c/imx8/fini.c i2c/imx8/init.c "
        "i2c/imx8/proto.h i2c/imx8/recv.c i2c/imx8/send.c flash")


class FileNameIsNotSymbol(unittest.TestCase):
    def test_path_is_ignored(self):
        for sym in ("recv", "send", "init", "proto"):
            self.assertIsNone(symbol_regex(sym).search(BSPS), sym)
            self.assertEqual(sentences_with(BSPS, sym), [], sym)

    def test_windows_path_is_ignored(self):
        self.assertIsNone(symbol_regex("recv").search(r"src\recv.c"))

    def test_real_mentions_are_kept(self):
        for text in ("Replace InterruptAttach() with InterruptAttachEvent().",
                     "Use InterruptAttach.", "InterruptAttach, then"):
            self.assertIsNotNone(symbol_regex("InterruptAttach").search(text), text)
        self.assertIsNotNone(symbol_regex("recv", call_form=True).search("call recv() here"))
        self.assertEqual(len(sentences_with("Call recv() once. Then stop.", "recv")), 1)

    def test_longer_identifier_still_rejected(self):
        self.assertIsNone(symbol_regex("recv").search("recvfrom() and recvmsg()"))
        self.assertIsNone(symbol_regex("recv", call_form=True).search("_recv()"))


if __name__ == "__main__":
    unittest.main()
