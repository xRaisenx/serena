"""Sandbox acceptance and fixture-only patch check for the CODEMIND guide slice."""

import html.parser
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "src/serena/resources/dashboard/codemind"
PATCH = ROOT / "patches/CODEMIND_Operator_Guide_Integration.patch"


class Audit(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.labels = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
        if tag == "a" and "href" in attributes:
            self.refs.append(attributes["href"])
        if tag == "label":
            self.labels.append(attributes.get("for"))


def test_html_ids_and_search_label():
    audit = Audit()
    audit.feed((WEB / "guide.html").read_text())
    assert len(set(audit.ids)) == len(audit.ids)
    assert {"howto", "readiness", "scenarios", "faqs", "about", "guide-search", "guide-results"}.issubset(audit.ids)
    assert "guide-search" in audit.labels
    for reference in audit.refs:
        if reference.startswith("#"):
            assert reference[1:] in audit.ids
        if reference.endswith(".html"):
            assert (WEB / reference).is_file() or reference == "index.html"  # Index is in the upstream branch.


def test_document_alignment():
    guide = (ROOT / "docs/codemind/CODEMIND-OPERATOR-HOWTO-FAQ.md").read_text()
    simulation = (ROOT / "docs/codemind/CODEMIND-ROUTE-SIMULATION.md").read_text()
    for gate in ["G1", "G2", "G3", "G4", "G5"]:
        assert re.search(r"\| " + gate + r" ", guide)
    for phrase in ["NOT VERIFIED", "NOT IMPLEMENTED", "How-To", "FAQ", "selected ≠ loaded ≠ executed", "three active"]:
        assert phrase.lower() in guide.lower()
    assert "Selected for this slice" in simulation
    assert "sandbox" in simulation.lower()


def test_unified_patch_applies_against_exact_source_anchors():
    with tempfile.TemporaryDirectory() as temporary_directory:
        base = Path(temporary_directory)
        index = base / "src/serena/resources/dashboard/codemind/index.html"
        document = base / "docs/codemind/ARCHITECTURE-AND-SLICES.md"
        index.parent.mkdir(parents=True)
        document.parent.mkdir(parents=True)
        sys.path.insert(0, str(ROOT / "patches"))
        from build_integration_patch import about

        index.write_text(("FILLER\n" * 167) + about + "LAST\n")
        document.write_text("# CODEMIND Serena Architecture and Acceptance Slices\n\n## Foundation and provenance\n")
        check = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=base, text=True, capture_output=True)
        assert check.returncode == 0, check.stderr
        applied = subprocess.run(["git", "apply", str(PATCH)], cwd=base, text=True, capture_output=True)
        assert applied.returncode == 0, applied.stderr
        assert "guide.html" in index.read_text()
        assert "CODEMIND-OPERATOR-HOWTO-FAQ.md" in document.read_text()
        # A second application must not silently duplicate the integration.
        second = subprocess.run(["git", "apply", "--check", str(PATCH)], cwd=base, text=True, capture_output=True)
        assert second.returncode != 0