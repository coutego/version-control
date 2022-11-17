import tempfile
import shutil
import os.path
import os
from unittest import TestCase
from vc.api import PRepo
from vc.impl import create_repo
from vc.impl.repo import Repo


class StatusTest(TestCase):
    rootdir: str
    repodir: str
    repo: PRepo

    def setUp(self):
        self.rootdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        self.repodir = self.rootdir + "/.vc"
        os.mkdir(self.repodir)
        os.chdir(self.rootdir)
        self.repo = create_repo(self.repodir)

    def tearDown(self):
        shutil.rmtree(self.rootdir)

    def test_empty(self):
        local_repo = create_repo("")
        with self.assertRaises(FileNotFoundError):
            local_repo.status()
        st = self.repo.status()
        self.assertIsNotNone(st)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.staged), 0)

    def test_detect_new_without_any_commit(self):
        f1 = self.create_file("README.org", "abc")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)
        self.repo.index.stage_file(f1)
        st = self.repo.status()
        self.assertEqual(len(st.staged), 1)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 0)
        self.repo.index.commit("Initial import")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 0)

    def test_basic__save(self):
        f1 = self.create_file("README.org", "abc")
        self.create_file("LICENSE", "EUPL")
        self.repo.index.stage_file(f1)
        st = self.repo.status()
        self.assertEqual(len(st.staged), 1)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)
        self.repo.index.commit("Initial import")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)

    def create_file(self, rel_root: str, contents: str) -> str:
        fn = self.rootdir + "/" + rel_root  # FIXME: check '/'
        with open(fn, "w") as f:
            f.write(contents)
            return fn

    def test_avoid_new_after_commit(self):
        f1 = self.create_file("README.org", "abc")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 1)
        self.repo.index.stage_file(f1)
        st = self.repo.status()
        self.assertEqual(len(st.staged), 1)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 0)
        self.repo.index.commit("Initial import")
        st = self.repo.status()
        self.assertEqual(len(st.staged), 0)
        self.assertEqual(len(st.not_staged), 0)
        self.assertEqual(len(st.not_tracked), 0)

if __name__ == "__main__":
    import unittest

    unittest.main()
