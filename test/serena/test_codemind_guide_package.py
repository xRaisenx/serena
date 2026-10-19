"""Sandbox acceptance and fixture-only patch check for the CODEMIND guide slice."""
import html.parser
import re
import subprocess
import tempfile
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/'src/serena/resources/dashboard/codemind'
PATCH=ROOT/'patches/CODEMIND_Operator_Guide_Integration.patch'

class Audit(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=[];self.refs=[];self.labels=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.refs.append(a['href'])
        if tag=='label':self.labels.append(a.get('for'))

def test_html_ids_and_search_label():
    v=Audit();v.feed((WEB/'guide.html').read_text())
    assert len(set(v.ids))==len(v.ids)
    assert set(['howto','readiness','scenarios','faqs','about','guide-search','guide-results']).issubset(v.ids)
    assert 'guide-search' in v.labels
    for ref in v.refs:
        if ref.startswith('#'):assert ref[1:] in v.ids
        if ref.endswith('.html'):assert (WEB/ref).is_file() or ref=='index.html'  # index is in upstream branch

def test_document_alignment():
    guide=(ROOT/'docs/codemind/CODEMIND-OPERATOR-HOWTO-FAQ.md').read_text()
    simulation=(ROOT/'docs/codemind/CODEMIND-ROUTE-SIMULATION.md').read_text()
    for gate in ['G1','G2','G3','G4','G5']:
        assert re.search(r'\| '+gate+r' ',guide)
    for phrase in ['NOT VERIFIED','NOT IMPLEMENTED','How-To','FAQ','selected ≠ loaded ≠ executed','three active']:
        assert phrase.lower() in guide.lower()
    assert 'Selected for this slice' in simulation
    assert 'sandbox' in simulation.lower()

def test_unified_patch_applies_against_exact_source_anchors():
    with tempfile.TemporaryDirectory() as tmp:
        base=Path(tmp)
        idx=base/'src/serena/resources/dashboard/codemind/index.html'
        doc=base/'docs/codemind/ARCHITECTURE-AND-SLICES.md'
        idx.parent.mkdir(parents=True);doc.parent.mkdir(parents=True)
        sys.path.insert(0,str(ROOT/'patches'))
        from build_integration_patch import about
        idx.write_text(('FILLER\n'*167)+about+'LAST\n')
        doc.write_text('# CODEMIND Serena Architecture and Acceptance Slices\n\n## Foundation and provenance\n')
        check=subprocess.run(['git','apply','--check',str(PATCH)],cwd=base,text=True,capture_output=True)
        assert check.returncode==0,check.stderr
        apply=subprocess.run(['git','apply',str(PATCH)],cwd=base,text=True,capture_output=True)
        assert apply.returncode==0,apply.stderr
        assert 'guide.html' in idx.read_text()
        assert 'CODEMIND-OPERATOR-HOWTO-FAQ.md' in doc.read_text()
        # Integration must be idempotence-safe: a second application cannot silently duplicate.
        second=subprocess.run(['git','apply','--check',str(PATCH)],cwd=base,text=True,capture_output=True)
        assert second.returncode!=0