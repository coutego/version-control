import tempfile
import shutil
import os.path
import os
from unittest import TestCase
from vc.prots import PObjectDB, PRepo, PIndex
from vc.impl.db import DB
from vc.impl.fs import create_vc_root_dir
from vc.impl.repo import Repo
from vc.impl.index import Index


class StatusTest(TestCase):
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

    def test_empty(self):
        local_repo = Repo(self.index, self.db, "")
        with self.assertRaises(FileNotFoundError):
            local_repo.status()
        st = self.repo.status()
        self.assertIsNotNone(st)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.staged), 0)

    def test_basic__save(self):
        f1 = self.create_file("README.org", "abc")
        self.create_file("LICENSE", "EUPL")
        self.index.stage_file(f1)
        st = self.repo.status()
        self.assertEqual(len(st.staged), 1)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)
        self.index.commit("Initial import")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)

    def create_file(self, rel_root: str, contents: str) -> str:
        fn = self.rootdir + "/" + rel_root  # FIXME: check '/'
        with open(fn, "w") as f:
            f.write(contents)
            return fn


if __name__ == "__main__":
    import unittest

    unittest.main()
