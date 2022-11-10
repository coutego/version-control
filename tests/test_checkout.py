import tempfile
import shutil
import os.path
import os
from unittest import TestCase
from vc.prots import PObjectDB, PRepo, PIndex
from vc.impl.db import DB
from vc.impl.repo import Repo
from vc.impl.index import Index


class CheckoutTest(TestCase):
    rootdir: str
    repodir: str
    db: PObjectDB
    repo: PRepo
    index: PIndex

    def setUp(self):
        self.rootdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        self.repodir = self.rootdir + "/.vc"
        os.mkdir(self.repodir)
        os.chdir(self.rootdir)
        self.db = DB(self.repodir)
        self.index = Index(self.db, self.repodir)
        self.repo = Repo(self.index, self.db, self.repodir)

    def tearDown(self):
        shutil.rmtree(self.rootdir)

    def test_basic__save(self):
        freadme = "README.org"
        flicense = "LICENSE"
        f1 = self.create_file(freadme, "abc")
        f2 = self.create_file(flicense, "EUPL")
        self.index.stage_file(f1)
        self.index.stage_file(f2)
        c1msg = "first commit"
        c1 = self.index.commit(c1msg)

        with open(f1, "a") as f:
            f.write("def")
        self.index.stage_file(f1)
        c2msg = "second commit"
        c2 = self.index.commit(c2msg)

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
