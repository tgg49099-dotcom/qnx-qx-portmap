"""Tests of scripts/qnx8_target_check.sh: a rehearsal never looks like the proof.

The script is run with a fake ``uname`` (QNX 8.0.0, QNX 7.1.0, Linux) and a
fake interpreter that answers ``--version`` and ``-m qnx_portmap`` without a
corpus, so the logic of the verdict is tested on any machine, with no network
and no QNX documentation.  The real interpreter still runs the ``compat``
check.  Only the verdict changes with the system: the corpus and the tool are
the same in every case.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "qnx8_target_check.sh")


def _write_exe(path, text):
    with open(path, "w") as fh:
        fh.write(text)
    os.chmod(path, 0o755)


@unittest.skipIf(shutil.which("sh") is None, "no POSIX shell on this system")
class TargetCheckVerdict(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="qx-target-")
        self.bin = os.path.join(self.tmp, "bin")
        os.mkdir(self.bin)
        self.corpus = os.path.join(self.tmp, "corpus")
        os.mkdir(self.corpus)
        with open(os.path.join(self.corpus, "MANIFEST.json"), "w") as fh:
            fh.write("{}\n")
        self.python = os.path.join(self.tmp, "fake-python")
        _write_exe(self.python, (
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  --version) echo 'Python 3.13.7'; exit 0 ;;\n"
            "  -c) exec %s \"$@\" ;;\n"
            "esac\n"
            "case \"$*\" in\n"
            "  *--verify-corpus*) exit \"${FAKE_VERIFY_RC:-0}\" ;;\n"
            "esac\n"
            "exit \"${FAKE_SYMBOLS_RC:-1}\"\n") % sys.executable)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self, system, release, **extra):
        _write_exe(os.path.join(self.bin, "uname"), (
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  -s) echo '%s' ;;\n"
            "  -r) echo '%s' ;;\n"
            "  -m) echo 'x86_64' ;;\n"
            "esac\n") % (system, release))
        env = dict(os.environ)
        env["PATH"] = self.bin + os.pathsep + env.get("PATH", "")
        env["QX_PORTMAP_PYTHON"] = self.python
        env.pop("QX_PORTMAP_REQUIRE_QNX8", None)
        env.update(extra)
        proc = subprocess.run(["sh", SCRIPT, self.corpus], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, timeout=60)
        return proc.returncode, proc.stdout

    def test_qnx8_target_is_the_proof(self):
        rc, out = self.run_check("QNX", "8.0.0")
        self.assertEqual(rc, 0, out)
        self.assertIn("QNX 8 system detected (release 8.0.0)", out)
        self.assertIn("QNX 8 target            : yes", out)
        self.assertIn("RESULT      : PASS - on a QNX 8 target", out)
        self.assertNotIn("rehearsal", out)

    def test_qnx8_target_passes_the_strict_mode(self):
        rc, out = self.run_check("QNX", "8.0.0", QX_PORTMAP_REQUIRE_QNX8="1")
        self.assertEqual(rc, 0, out)

    def test_qnx71_is_not_the_qnx8_proof(self):
        rc, out = self.run_check("QNX", "7.1.0")
        self.assertEqual(rc, 0, out)
        self.assertIn("release 7.1.0 is not 8.x", out)
        self.assertIn("PASS (rehearsal only - this is NOT a run on QNX 8.0)", out)
        self.assertNotIn("PASS - on a QNX 8 target", out)

    def test_linux_is_a_rehearsal(self):
        rc, out = self.run_check("Linux", "6.8.0")
        self.assertEqual(rc, 0, out)
        self.assertIn("NOT a QNX system", out)
        self.assertIn("QNX 8 target            : no", out)
        self.assertIn("PASS (rehearsal only - this is NOT a run on QNX 8.0)", out)
        self.assertNotIn("PASS - on a QNX 8 target", out)

    def test_strict_mode_refuses_a_rehearsal(self):
        for system, release in (("Linux", "6.8.0"), ("QNX", "7.1.0")):
            rc, out = self.run_check(system, release, QX_PORTMAP_REQUIRE_QNX8="1")
            self.assertEqual(rc, 3, out)
            self.assertIn("exit code 3", out)

    def test_corrupted_corpus_fails_even_on_qnx8(self):
        rc, out = self.run_check("QNX", "8.0.0", FAKE_VERIFY_RC="1")
        self.assertEqual(rc, 1, out)
        self.assertIn("RESULT      : FAIL", out)
        self.assertNotIn("PASS", out.split("-- verdict --")[1])


if __name__ == "__main__":
    unittest.main()
