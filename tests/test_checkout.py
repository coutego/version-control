import tempfile
import shutil
import os.path
import os
from unittest import TestCase
from vc.api import PRepo
from vc.impl import create_repo


class CheckoutTest(TestCase):
    rootdir: str
    repo: PRepo

    def setUp(self):
        self.rootdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        os.chdir(self.rootdir)
        self.repo = create_repo(self.rootdir, True)

    def tearDown(self):
        shutil.rmtree(self.rootdir)

    def test_basic__save(self):
        freadme = "README.org"
        flicense = "LICENSE"
        f1 = self.create_file(freadme, "abc")
        f2 = self.create_file(flicense, "EUPL")
        self.repo.index.stage_file(f1)
        self.repo.index.stage_file(f2)
        c1msg = "first commit"
        c1 = self.repo.index.commit(c1msg)

        with open(f1, "a") as f:
            f.write("def")
        self.repo.index.stage_file(f1)
        c2msg = "second commit"
        c2 = self.repo.index.commit(c2msg)

        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 0)

        with open(f1, "r") as f:
            self.assertEqual("abcdef", f.read())
        self.repo.checkout(c1)
        with open(f1, "r") as f:
            self.assertEqual(f.read(), "abc")
        self.repo.checkout(c2[:6])  # Check that the commit ids are fully recovered
        with open(f1, "r") as f:
            self.assertEqual(f.read(), "abcdef")
        log = self.repo.log()
        self.assertEqual(c2, log[0].key)

    def create_file(self, rel_root: str, contents: str) -> str:
        fn = self.rootdir + "/" + rel_root
        with open(fn, "w") as f:
            f.write(contents)
            return fn


if __name__ == "__main__":
    import unittest

    unittest.main()
