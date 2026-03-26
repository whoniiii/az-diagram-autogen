"""Cross-version sync verification.

Ensures az-diagram-autogen/ (source) and azure-architecture-autopilot/scripts/ (EN)
have matching generator.py and icons.py content (except import style).
"""
import os
import re
import unittest


def _repo_root():
    """Find the repo root (GHCP001/)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while d and os.path.basename(d) != "GHCP001":
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return d


def _read(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


class TestGeneratorSync(unittest.TestCase):
    """generator.py should be identical except for import style."""

    def setUp(self):
        root = _repo_root()
        self.source = _read(os.path.join(
            root, "az-diagram-autogen", "az_diagram_autogen", "generator.py"))
        self.en = _read(os.path.join(
            root, ".github", "skills", "azure-architecture-autopilot",
            "scripts", "generator.py"))

    def _normalize_imports(self, code):
        """Normalize relative/absolute import differences."""
        if code is None:
            return None
        return re.sub(r'from \.icons import', 'from icons import', code)

    def test_both_files_exist(self):
        self.assertIsNotNone(self.source, "Source generator.py not found")
        self.assertIsNotNone(self.en, "EN generator.py not found")

    def test_generator_content_matches(self):
        if self.source is None or self.en is None:
            self.skipTest("File(s) not found")
        src_norm = self._normalize_imports(self.source)
        en_norm = self._normalize_imports(self.en)
        if src_norm != en_norm:
            # Find first difference for debugging
            src_lines = src_norm.splitlines()
            en_lines = en_norm.splitlines()
            for i, (s, e) in enumerate(zip(src_lines, en_lines)):
                if s != e:
                    self.fail(
                        f"generator.py differs at line {i+1}:\n"
                        f"  SOURCE: {s[:100]}\n"
                        f"  EN:     {e[:100]}"
                    )
            if len(src_lines) != len(en_lines):
                self.fail(
                    f"generator.py line count differs: "
                    f"source={len(src_lines)}, EN={len(en_lines)}"
                )

    def test_type_aliases_match(self):
        """_TYPE_ALIASES dict should be identical."""
        if self.source is None or self.en is None:
            self.skipTest("File(s) not found")
        pattern = r'_TYPE_ALIASES\s*=\s*\{[^}]+\}'
        src_match = re.search(pattern, self.source, re.DOTALL)
        en_match = re.search(pattern, self.en, re.DOTALL)
        self.assertIsNotNone(src_match, "_TYPE_ALIASES not found in source")
        self.assertIsNotNone(en_match, "_TYPE_ALIASES not found in EN")
        self.assertEqual(src_match.group(), en_match.group(),
                         "_TYPE_ALIASES content differs between source and EN")


class TestIconsSync(unittest.TestCase):
    """icons.py should be byte-identical between source and EN."""

    def setUp(self):
        root = _repo_root()
        self.source = _read(os.path.join(
            root, "az-diagram-autogen", "az_diagram_autogen", "icons.py"))
        self.en = _read(os.path.join(
            root, ".github", "skills", "azure-architecture-autopilot",
            "scripts", "icons.py"))

    def test_both_files_exist(self):
        self.assertIsNotNone(self.source, "Source icons.py not found")
        self.assertIsNotNone(self.en, "EN icons.py not found")

    def test_icons_content_matches(self):
        if self.source is None or self.en is None:
            self.skipTest("File(s) not found")
        if self.source != self.en:
            src_lines = self.source.splitlines()
            en_lines = self.en.splitlines()
            for i, (s, e) in enumerate(zip(src_lines, en_lines)):
                if s != e:
                    self.fail(
                        f"icons.py differs at line {i+1}:\n"
                        f"  SOURCE: {s[:100]}\n"
                        f"  EN:     {e[:100]}"
                    )
            if len(src_lines) != len(en_lines):
                self.fail(
                    f"icons.py line count differs: "
                    f"source={len(src_lines)}, EN={len(en_lines)}"
                )

    def test_critical_icons_present_in_both(self):
        """microsoft_fabric and ai_foundry must be in both."""
        if self.source is None or self.en is None:
            self.skipTest("File(s) not found")
        for icon_key in ["microsoft_fabric", "ai_foundry"]:
            self.assertIn(f'"{icon_key}"', self.source,
                          f"{icon_key} missing from source icons.py")
            self.assertIn(f'"{icon_key}"', self.en,
                          f"{icon_key} missing from EN icons.py")


if __name__ == "__main__":
    unittest.main()
