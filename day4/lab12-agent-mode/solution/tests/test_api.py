import os
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from kaveridesk.api import app

DATA = Path(__file__).resolve().parent.parent / "data"


class TestApi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for f in DATA.glob("*.json"):
            shutil.copy(f, self.tmp)
        os.environ["KAVERIDESK_DATA"] = self.tmp
        os.environ["KAVERIDESK_NOW"] = "2026-11-20 11:00"
        self.client = TestClient(app)

    def tearDown(self):
        os.environ.pop("KAVERIDESK_DATA", None)
        os.environ.pop("KAVERIDESK_NOW", None)
        shutil.rmtree(self.tmp)

    def test_health(self):
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})

    def test_list_open_and_all(self):
        self.assertEqual(len(self.client.get("/tickets").json()), 10)
        self.assertEqual(len(self.client.get("/tickets", params={"all": "true"}).json()), 14)

    def test_list_by_team(self):
        ids = [t["id"] for t in self.client.get("/tickets", params={"team": "security ops"}).json()]
        self.assertEqual(ids, ["INC-1013", "INC-1004"])

    def test_get_one_and_404(self):
        r = self.client.get("/tickets/INC-1013")
        self.assertEqual(r.json()["sla"], "BREACHED")
        self.assertEqual(r.json()["due"], "2026-11-20T11:00")
        r = self.client.get("/tickets/INC-9999")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {"detail": "No ticket INC-9999"})

    def test_create(self):
        r = self.client.post("/tickets", json={"title": "Mouse not working", "category": "IT", "requester": "you"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["assignee"], "A03")
        self.assertEqual(r.json()["priority"], "P3")
        self.assertEqual(self.client.get(f"/tickets/{r.json()['id']}").status_code, 200)

    def test_create_invalid(self):
        bad = [{"title": "Hi", "category": "IT", "requester": "you"},
               {"title": "Coffee machine empty", "category": "Pantry", "requester": "you"},
               {"title": "Mouse not working", "category": "IT", "priority": "P9", "requester": "you"},
               {"title": "Mouse not working", "category": "IT"}]
        for body in bad:
            self.assertEqual(self.client.post("/tickets", json=body).status_code, 422, body)

    def test_breaches(self):
        self.assertEqual([t["id"] for t in self.client.get("/breaches").json()], ["INC-1003", "INC-1009", "INC-1013"])


if __name__ == "__main__":
    unittest.main()
