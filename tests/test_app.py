import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from threading import Thread

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app


class APITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.APIHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = Path(self.temp_dir.name) / "messages.json"
        self.patcher = patch.object(app, "DATA_FILE", self.data_file)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def request(self, method, path, payload=None):
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urlopen(req) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())

    def test_health_endpoint(self):
        status, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "active")

    def test_get_messages_empty(self):
        status, body = self.request("GET", "/messages")
        self.assertEqual(status, 200)
        self.assertEqual(body["total"], 0)

    def test_create_message(self):
        status, body = self.request("POST", "/messages", {"message": "Test CI/CD"})
        self.assertEqual(status, 201)
        self.assertEqual(body["message"]["message"], "Test CI/CD")

    def test_reject_empty_message(self):
        status, body = self.request("POST", "/messages", {"message": " "})
        self.assertEqual(status, 400)

    def test_delete_message(self):
        self.request("POST", "/messages", {"message": "Message to delete"})
        status, body = self.request("DELETE", "/messages?index=0")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "deleted")


if __name__ == "__main__":
    unittest.main()
