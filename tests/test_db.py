import tempfile
import shutil
from unittest import TestCase
from vc.prots import PObjectDB
from vc.impl.db import DB
from vc.impl.sha1hasher import SHA1Hasher
from vc.impl.fs import create_vc_root_dir


class DBTest(TestCase):
    root: str
    db: PObjectDB

    def setUp(self):
        h = SHA1Hasher()
        self.root = tempfile.mkdtemp(dir=tempfile.gettempdir())

        create_vc_root_dir(self.root)
        self.db = DB(h, self.root)

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_not_found(self):
        db = self.db
        r = db.get("I dont exist")
        self.assertEqual(r, None)
        r = db.get(None)
        self.assertEqual(r, None)

    def test_basic_save(self):
        db = self.db
        c = "abc"
        h = db.put(c)
        ob = db.get(h).text
        self.assertEqual(c, ob)

    def test_incorrect_root(self):
        db = DB(SHA1Hasher(), "i dont exist sldkfjsdlkfjds")
        try:
            db.get("abcdefgh")
            self.fail("FileNotFoundError expected")
        except FileNotFoundError:
            pass
        try:
            db.put("abcdefgh")
            self.fail("FileNotFoundError expected")
        except FileNotFoundError:
            pass
