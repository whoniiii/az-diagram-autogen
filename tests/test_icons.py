"""Tests for az_diagram_autogen.icons"""
import unittest
from az_diagram_autogen.icons import get_icon_data_uri, search_icons, AZURE_ICONS


class TestIcons(unittest.TestCase):
    def test_icon_count(self):
        self.assertGreaterEqual(len(AZURE_ICONS), 600)

    def test_get_icon_known(self):
        uri = get_icon_data_uri("storage_accounts")
        self.assertTrue(uri.startswith("data:image/svg+xml;base64,"))

    def test_get_icon_unknown(self):
        self.assertEqual(get_icon_data_uri("nonexistent_icon_xyz"), "")

    def test_get_icon_normalization(self):
        uri1 = get_icon_data_uri("key-vaults")
        uri2 = get_icon_data_uri("key_vaults")
        self.assertEqual(uri1, uri2)

    def test_search(self):
        results = search_icons("storage")
        self.assertGreater(len(results), 0)
        self.assertTrue(all(len(r) == 3 for r in results))

    def test_search_empty(self):
        results = search_icons("zzz_nonexistent_zzz")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
