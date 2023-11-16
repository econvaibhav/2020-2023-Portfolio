"""Offline checks for the portfolio, not tests of the original research results."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'catalogue/projects.json').read_text(encoding='utf-8'))

class Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.path = path
        self.ids: list[str] = []
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.scripts: list[dict[str, str]] = []
        self.h1_count = 0
        self.language = ''
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'html': self.language = attrs.get('lang', '')
        if tag == 'h1': self.h1_count += 1
        if tag == 'img': self.images.append(attrs)
        if tag == 'script': self.scripts.append(attrs)
        for name in ('href', 'src'):
            if attrs.get(name): self.links.append(attrs[name])

class PortfolioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {p.resolve(): Page(p) for p in ROOT.rglob('*.html') if '.git' not in p.parts}
        cls.artifacts = {(ROOT / 'projects' / p['id'] / f['name']).resolve(): f for p in PROJECTS for f in p['files']}

    def test_01_project_catalogue(self):
        self.assertEqual(len(PROJECTS), 12)
        ids = [p['id'] for p in PROJECTS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.artifacts), 20)
        for p in PROJECTS:
            for key in ('question','method_question','substance','methods','argument','bridge','scope','credits'):
                self.assertTrue(p[key].strip(), f"Missing {key} in {p['id']}")
            self.assertTrue(set(p['related']).issubset(ids))

    def test_02_original_artifact_integrity(self):
        for path, record in self.artifacts.items():
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertTrue(path.is_file())
                self.assertEqual(path.stat().st_size, record['bytes'])
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['sha256'])

    def test_03_notebook_structure_and_period(self):
        notebooks = [p for p in self.artifacts if p.suffix == '.ipynb']
        self.assertEqual(len(notebooks), 3)
        for path in notebooks:
            nb = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(nb['nbformat'], 4)
            self.assertTrue(nb['cells'])
            for cell in nb['cells']:
                self.assertIn(cell['cell_type'], ('code','markdown','raw'))
                self.assertIn('source', cell)
                timestamp = cell.get('metadata',{}).get('executionInfo',{}).get('timestamp')
                if timestamp:
                    self.assertLess(datetime.fromtimestamp(timestamp/1000, timezone.utc).year, 2024)

    def test_04_local_links_and_page_anchors(self):
        for path, page in self.pages.items():
            for href in page.links:
                u = urlsplit(href)
                if u.scheme or u.netloc: continue
                target = (path.parent / unquote(u.path)).resolve() if u.path else path
                with self.subTest(page=str(path.relative_to(ROOT)), href=href):
                    self.assertTrue(target.is_relative_to(ROOT.resolve()), 'Path escapes repository')
                    self.assertTrue(target.exists(), f'Missing target {target}')
                    if u.fragment and target.suffix == '.html':
                        self.assertIn(unquote(u.fragment), self.pages[target].ids)
                    if u.fragment.startswith('page=') and target.suffix == '.pdf':
                        self.assertIn(target, self.artifacts)
                        number = int(u.fragment.split('=')[1])
                        self.assertTrue(1 <= number <= self.artifacts[target]['pages'])

    def test_05_project_pages_and_readers(self):
        for p in PROJECTS:
            folder = ROOT / 'projects' / p['id']
            self.assertTrue((folder / 'README.md').is_file())
            page = (folder / 'index.html').read_text(encoding='utf-8')
            for marker in ('01 / Substance','02 / Methods','What the work brings out','The connection','Read the work'):
                self.assertIn(marker, page)
            if any(f['kind'] == 'Notebook' for f in p['files']):
                self.assertTrue((folder / 'notebook.html').is_file())

    def test_06_accessible_page_structure(self):
        for path, page in self.pages.items():
            with self.subTest(page=str(path.relative_to(ROOT))):
                self.assertEqual(page.language, 'en')
                self.assertEqual(page.h1_count, 1)
                self.assertEqual(len(page.ids), len(set(page.ids)))
                for image in page.images:
                    self.assertIn('alt', image)
                    if image.get('id') != 'zoom-image': self.assertTrue(image['alt'])

    def test_07_no_external_runtime_dependencies(self):
        for path, page in self.pages.items():
            for script in page.scripts:
                self.assertEqual(script.get('src'), '../../assets/portfolio.js' if path.parent != ROOT else 'assets/portfolio.js')
            for href in page.links:
                if urlsplit(href).scheme in ('http','https'):
                    self.fail(f'Unexpected network dependency in generated page: {path}: {href}')

    def test_08_reading_guides_reference_the_evidence(self):
        for p in PROJECTS:
            files = {f['name']: f for f in p['files']}
            for item in p['inspect']:
                self.assertIn(item['file'], files)
                self.assertTrue(1 <= item['page'] <= files[item['file']]['pages'])
            a = p['argument_source']
            self.assertIn(a['file'], files)
            size = files[a['file']].get('pages',files[a['file']].get('cells'))
            self.assertTrue(1 <= a['page'] <= size)
            self.assertTrue((ROOT/'assets/previews'/p['preview']['image']).exists())

    def test_09_markdown_file_links(self):
        for path in [ROOT/'README.md', ROOT/'PUBLISHING.md', *ROOT.glob('projects/*/README.md')]:
            for href in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
                u = urlsplit(href)
                if u.scheme or u.netloc or not u.path: continue
                self.assertTrue((path.parent/unquote(u.path)).resolve().exists(), f'{path}: {href}')

    def test_10_publication_files_and_file_sizes(self):
        self.assertTrue((ROOT/'.nojekyll').exists())
        self.assertTrue((ROOT/'index.html').exists())
        for path in ROOT.rglob('*'):
            if path.is_file() and '.git' not in path.parts:
                self.assertLess(path.stat().st_size, 95*1024*1024, f'{path} is too large for an ordinary Git upload')

    def test_11_rebuild_is_deterministic(self):
        generated = [ROOT/'index.html', ROOT/'README.md', *ROOT.glob('projects/*/index.html'), *ROOT.glob('projects/*/README.md'), *ROOT.glob('projects/*/notebook.html')]
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in generated}
        subprocess.run([sys.executable, str(ROOT/'tools/build_portfolio.py')], check=True, capture_output=True)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in generated})

if __name__ == '__main__':
    unittest.main()
