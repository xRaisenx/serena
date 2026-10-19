"""Source contract for the CODEMIND operator guide and integrated SCC navigation."""

import html.parser
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "src/serena/resources/dashboard/codemind"


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
    audit.feed((WEB / "guide.html").read_text(encoding="utf-8"))
    assert len(set(audit.ids)) == len(audit.ids)
    assert {"howto", "readiness", "scenarios", "faqs", "about", "guide-search", "guide-results"}.issubset(audit.ids)
    assert "guide-search" in audit.labels
    for reference in audit.refs:
        if reference.startswith("#"):
            assert reference[1:] in audit.ids
        if reference.endswith(".html"):
            assert (WEB / reference).is_file()


def test_document_alignment():
    guide = (ROOT / "docs/codemind/CODEMIND-OPERATOR-HOWTO-FAQ.md").read_text(encoding="utf-8")
    simulation = (ROOT / "docs/codemind/CODEMIND-ROUTE-SIMULATION.md").read_text(encoding="utf-8")
    for gate in ["G1", "G2", "G3", "G4", "G5"]:
        assert re.search(r"\| " + gate + r" ", guide)
    for phrase in ["NOT VERIFIED", "NOT IMPLEMENTED", "How-To", "FAQ", "selected ≠ loaded ≠ executed", "three active"]:
        assert phrase.lower() in guide.lower()
    assert "Selected for this slice" in simulation
    assert "sandbox" in simulation.lower()


def test_existing_dashboard_and_architecture_link_to_guide():
    dashboard = (WEB / "index.html").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/codemind/ARCHITECTURE-AND-SLICES.md").read_text(encoding="utf-8")
    assert 'href="guide.html"' in dashboard
    assert "CODEMIND-OPERATOR-HOWTO-FAQ.md" in architecture
    assert "CODEMIND-ROUTE-SIMULATION.md" in architecture
    assert (WEB / "guide.html").is_file()
