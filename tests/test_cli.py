"""Tests for az_diagram_autogen.cli"""
import unittest
import os
import json
import tempfile
from unittest.mock import patch
from az_diagram_autogen.cli import main, _load_json


class TestLoadJson(unittest.TestCase):
    def test_inline_json(self):
        data = _load_json('[{"id": "s1"}]', "test")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "s1")

    def test_file_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([{"id": "s1"}], f)
            f.flush()
            path = f.name
        try:
            data = _load_json(path, "test")
            self.assertEqual(data[0]["id"], "s1")
        finally:
            os.unlink(path)

    def test_invalid_json(self):
        with self.assertRaises(SystemExit):
            _load_json("not-a-file-and-not-json", "test")


class TestCLI(unittest.TestCase):
    def test_cli_produces_output(self):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            outpath = f.name
        try:
            with patch("sys.argv", [
                "az-diagram-autogen",
                "-s", '[{"id":"s1","name":"F","type":"ai_foundry"}]',
                "-c", "[]",
                "-o", outpath,
            ]):
                main()
            self.assertTrue(os.path.exists(outpath))
            with open(outpath, encoding="utf-8") as f:
                html = f.read()
            self.assertIn("<!DOCTYPE html>", html)
        finally:
            os.unlink(outpath)


if __name__ == "__main__":
    unittest.main()
