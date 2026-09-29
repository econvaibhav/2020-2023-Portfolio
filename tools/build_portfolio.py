#!/usr/bin/env python3
"""Build the portfolio and static notebook readers. Original coursework is not executed."""
from __future__ import annotations

import base64
from html import escape
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PROJECTS: list[dict[str, Any]] = json.loads((ROOT / 'catalogue/projects.json').read_text(encoding='utf-8'))
BY_ID = {p['id']: p for p in PROJECTS}


def esc(value: Any) -> str:
    return escape(str(value), quote=True)


def link(path: str, label: str, **attrs: str) -> str:
    other = ''.join(f' {key}="{esc(val)}"' for key, val in attrs.items())
    return f'<a href="{esc(path)}"{other}>{esc(label)}</a>'


def head(title: str, description: str, prefix: str = '') -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Vaibhav Agarwal</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#f8f7f3">
<meta name="color-scheme" content="light">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/portfolio.css">
<script src="{prefix}assets/portfolio.js" defer></script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="topbar"><div class="wrap topbar-inner">
<a class="brand" href="{prefix}index.html"><span class="brand-name">Vaibhav Agarwal</span><span class="brand-year">2020–2023</span></a>
<nav aria-label="Main navigation"><a href="{prefix}index.html#work">Projects</a><a href="{prefix}index.html#gallery">Gallery</a><a href="{prefix}index.html#about">About</a></nav>
</div></header>
'''


def foot(prefix: str = '') -> str:
    return f'''
<footer class="footer"><div class="wrap footer-inner"><span>Vaibhav Agarwal · BA Economics · Azim Premji University</span><a href="{prefix}index.html#work">All projects ↑</a></div></footer>
<dialog class="dialog" id="zoom-dialog" aria-labelledby="zoom-title">
<div class="dialog-head"><h2 id="zoom-title">Image preview</h2><button type="button" data-close>Close ×</button></div>
<img id="zoom-image" class="zoom-image" alt=""><p id="zoom-caption" class="zoom-caption"></p>
</dialog>
</body></html>
'''


def file_label(f: dict[str, Any]) -> str:
    return f"PDF · {f['pages']} {'page' if f['pages'] == 1 else 'pages'}" if 'pages' in f else 'Python notebook'


def preview(p: dict[str, Any], prefix: str = '', eager: bool = False) -> str:
    v = p['preview']
    loading = 'eager' if eager else 'lazy'
    return f'<img src="{prefix}assets/previews/{esc(v["image"])}" alt="{esc(v["alt"])}" loading="{loading}" decoding="async">'


def tags(p: dict[str, Any]) -> str:
    return '<div class="tags">' + ''.join(f'<span>{esc(t)}</span>' for t in p['tags']) + '</div>'


def artifact_list(p: dict[str, Any]) -> str:
    rows = []
    for f in p['files']:
        if f['kind'] == 'Notebook':
            title = link('notebook.html', f['label'] + ' ↗')
            secondary = link(quote(f['name']), 'Download .ipynb', download='', **{'class': 'file-download'})
        else:
            title = link(quote(f['name']), f['label'] + ' ↗')
            secondary = ''
        rows.append(f'<li><div>{title}{secondary}</div><small>{file_label(f)}</small></li>')
    return '<ul class="artifact-list">' + ''.join(rows) + '</ul>'


def project_page(p: dict[str, Any]) -> str:
    pr = p['preview']
    original = quote(pr['file']) + f'#page={pr["page"]}' if pr['page'] else 'notebook.html'
    note = f'<p class="file-note">{esc(p["notes"])}</p>' if p['notes'] else ''
    related = ''.join(
        f'<a href="../{id}/index.html">{esc(BY_ID[id]["title"])} <span>↗</span></a>'
        for id in p['related']
    )
    return head(p['title'], p['short'], '../../') + f'''
<main id="main" class="wrap">
<header class="project-heading">
<p class="breadcrumb"><a href="../../index.html#work">← All projects</a><span>{p['number']}</span></p>
<h1>{esc(p['title'])}</h1>
{tags(p)}
</header>
<div class="project-detail">
<figure class="project-media">
<a href="../../assets/previews/{pr['image']}" data-zoom data-caption="{esc(pr['caption'])}">{preview(p, '../../', eager=True)}</a>
<figcaption>{esc(pr['caption'])} {link(original, 'Open file ↗')}</figcaption>
</figure>
<div class="project-info">
<p class="project-description">{esc(p['description'])}</p>
<section class="project-files" id="files"><h2>Files</h2>{artifact_list(p)}{note}</section>
<p class="credits"><strong>By</strong> {esc(p['credits'])}</p>
</div>
</div>
<section class="more-work"><h2>More projects</h2><div>{related}</div></section>
</main>
''' + foot('../../')


def project_readme(p: dict[str, Any]) -> str:
    pr = p['preview']
    parts = [
        f"# {p['title']}",
        '[← All projects](../../README.md) · [Project page](index.html)',
        p['description'],
        ' · '.join(p['tags']),
        f"![{pr['alt']}](../../assets/previews/{pr['image']})",
        f"*{pr['caption']}*", '## Files',
    ]
    for f in p['files']:
        parts.append(f"- [{f['label']}]({quote(f['name'])}) · {file_label(f)}")
        if f['kind'] == 'Notebook':
            parts.append('  [Read code and saved outputs](notebook.html).')
    if p['notes']:
        parts.append(p['notes'])
    parts.append(f"**By:** {p['credits']}")
    return '\n\n'.join(parts) + '\n'


def source_text(value: Any) -> str:
    return ''.join(str(item) for item in value) if isinstance(value, list) else str(value or '')


def preformatted(value: Any) -> str:
    # Encode line-end whitespace without changing the displayed notebook text.
    return re.sub(r'[ \t]+(?=\n|$)',
                  lambda match: ''.join('&#32;' if c == ' ' else '&#9;' for c in match[0]),
                  esc(source_text(value)))


def notebook_page(p: dict[str, Any], f: dict[str, Any]) -> str:
    nb = json.loads((ROOT / 'projects' / p['id'] / f['name']).read_text(encoding='utf-8'))
    cells = []
    for i, cell in enumerate(nb['cells'], 1):
        code = cell['cell_type'] == 'code'
        source = preformatted(cell.get('source', ''))
        outputs = []
        for out in cell.get('outputs', []):
            data = out.get('data', {})
            png = source_text(data.get('image/png', ''))
            if png:
                # Embed only validated PNG data. Never execute notebook HTML or JavaScript.
                raw = base64.b64decode(png, validate=False)
                if not raw.startswith(b'\x89PNG\r\n\x1a\n'):
                    raise ValueError(f'Invalid PNG in {f["name"]}, cell {i}')
                safe = base64.b64encode(raw).decode('ascii')
                outputs.append(f'<img src="data:image/png;base64,{safe}" alt="Original saved plot from notebook cell {i}" loading="lazy">')
            txt = source_text(out.get('text', '')) or source_text(data.get('text/plain', ''))
            if txt and not (png and txt.lstrip().startswith('<Figure')):
                outputs.append(f'<details><summary>Saved text output</summary><pre>{preformatted(txt)}</pre></details>')
            if out.get('output_type') == 'error':
                outputs.append(f'<details><summary>Saved error</summary><pre>{esc(out.get("ename", "Error"))}: {esc(out.get("evalue", ""))}</pre></details>')
            if 'text/html' in data and not png and not txt:
                outputs.append('<p class="omitted">Interactive output is available in the original notebook.</p>')
        kind = 'code-source' if code else 'markdown-source'
        cells.append(f'<section class="notebook-cell" id="cell-{i}"><div class="cell-label"><a href="#cell-{i}">CELL {i:02}</a><br>{"PYTHON" if code else "MARKDOWN"}</div><div class="cell-body"><pre class="{kind}">{source}</pre><div class="cell-output">{"".join(outputs)}</div></div></section>')
    return head(f['label'], p['short'], '../../') + f'''
<main id="main" class="wrap">
<div class="reader-header"><p class="breadcrumb"><a href="index.html">← {esc(p['title'])}</a></p><h1>{esc(f['label'])}</h1>
<p>{len(nb['cells'])} cells · Code and saved outputs. This view does not execute the notebook.</p>
<p>{link(quote(f['name']), 'Download .ipynb ↓', download='')}</p>
<div class="reader-controls js-only"><button type="button" data-reader-toggle="code" aria-pressed="true">Hide code</button><button type="button" data-reader-toggle="output" aria-pressed="true">Hide saved outputs</button></div></div>
<div class="reader">{''.join(cells)}</div></main>
''' + foot('../../')


def card(p: dict[str, Any]) -> str:
    href = f'projects/{p["id"]}/index.html'
    searchable = ' '.join([p['title'], p['short'], p['description'], *p['tags']]).lower()
    count = len(p['files'])
    return f'''
<article class="project-card" id="project-{p['id']}" data-categories="{'|'.join(p['categories'])}" data-search="{esc(searchable)}">
<a href="{href}" class="card-image">{preview(p)}</a>
<div class="card-meta"><span>{p['number']} / {esc(p['area'])}</span><span>{count} {'file' if count == 1 else 'files'}</span></div>
<h3><a href="{href}">{esc(p['title'])}</a></h3>
<p class="card-description">{esc(p['short'])}</p>
{tags(p)}
<div class="card-bottom"><a href="{href}">View project ↗</a></div>
</article>
'''


def gallery_piece(id: str, title: str, tall: bool = False) -> str:
    p = BY_ID[id]
    pr = p['preview']
    return f'''<figure class="gallery-piece {'tall' if tall else ''}"><a class="mat" href="assets/previews/{pr['image']}" data-zoom data-caption="{esc(pr['caption'])}">{preview(p)}</a><figcaption><strong>{esc(title)}</strong><a href="projects/{id}/index.html">View project ↗</a></figcaption></figure>'''


def root_page() -> str:
    filters = ''.join(f'<button type="button" data-category="{value}" aria-pressed="{str(not value).lower()}">{name}</button>' for value, name in [('', 'All work'), ('papers', 'Papers'), ('code', 'Code'), ('visuals', 'Visual work')])
    return head('2020–2023 Portfolio', 'Papers, notebooks and visual projects from my BA in Economics at Azim Premji University.') + f'''
<main id="main"><div class="wrap">
<section class="hero" aria-label="Portfolio introduction">
<div><p class="eyebrow">BA Economics · Azim Premji University</p><h1>2020–2023<br><em>Portfolio</em></h1>
<p class="hero-lead">Papers, notebooks and visual projects from my undergraduate studies.</p>
<div class="hero-actions"><a class="button dark" href="#work">Browse projects ↓</a><a href="#gallery">View gallery ↗</a></div></div>
<div class="hero-art" aria-label="Portfolio previews">
<a class="plate one" href="projects/india-china-development/index.html" aria-label="India and China timeline">{preview(BY_ID['india-china-development'], eager=True)}</a>
<a class="plate two" href="projects/data-visualization/index.html" aria-label="Data visualisation poster">{preview(BY_ID['data-visualization'], eager=True)}</a>
<a class="plate three" href="projects/ccus-india/index.html" aria-label="Carbon capture presentation">{preview(BY_ID['ccus-india'], eager=True)}</a>
</div>
</section>
<section class="section" id="work">
<div class="section-head"><h2>Selected projects</h2><span class="section-count">{len(PROJECTS):02} projects</span></div>
<div class="filter-panel js-only"><div class="filter-row"><div class="category-filters" role="group" aria-label="Filter projects">{filters}</div><label class="search-box"><span class="sr-only">Search projects</span><input id="project-search" type="search" placeholder="Search projects…" autocomplete="off"></label></div><div class="filter-state"><span id="result-count" role="status" aria-live="polite">{len(PROJECTS)} projects</span><button type="button" id="reset-filters" hidden>Clear filters</button></div></div>
<div class="project-grid">{''.join(card(p) for p in PROJECTS)}</div>
<p id="empty-state" class="empty" hidden>No projects found. Try a different search.</p>
</section>
<section class="section" id="gallery"><div class="section-head"><h2>Gallery</h2><span class="section-count">Posters, timelines &amp; slides</span></div>
<div class="gallery-grid">{gallery_piece('india-china-development', 'India & China timeline')}{gallery_piece('data-visualization', 'Colour-blind-friendly visualisation', True)}{gallery_piece('ccus-india', 'Carbon capture in India')}</div></section>
<section class="section about" id="about"><div><h2>About</h2><p class="name">Vaibhav Agarwal</p></div><div><p>I studied Economics at Azim Premji University from 2020 to 2023. This is a selection of my papers, coding assignments and visual projects from that time.</p><p>Several pieces were group coursework. Co-authors are listed on the project pages.</p></div></section>
</div></main>
''' + foot()


def root_readme() -> str:
    rows = []
    for p in PROJECTS:
        files = ', '.join('notebook' if f['kind'] == 'Notebook' else f['label'].lower() for f in p['files'])
        rows.append(f"| [{p['title']}](projects/{p['id']}/) | {p['short']} | {files} |")
    return '''# 2020–2023 Portfolio

**Vaibhav Agarwal · BA Economics · Azim Premji University**

A selection of my papers, notebooks and visual projects from 2020–2023.

[View the portfolio](https://econvaibhav.github.io/2020-2023-Portfolio/) · [Browse projects](#projects)

![The portfolio website](assets/portfolio-preview.jpg)

## Projects

| Project | Description | Files |
| --- | --- | --- |
''' + '\n'.join(rows) + '''

## Visual work

<table><tr>
<td width="33%" valign="top"><a href="projects/india-china-development/"><img src="assets/previews/timeline.jpg" alt="India and China historical timeline"></a><p>India &amp; China timeline</p></td>
<td width="33%" valign="top"><a href="projects/data-visualization/"><img src="assets/previews/visualisation.jpg" alt="Colour-blind-friendly visualisation poster"></a><p>Colour-blind-friendly visualisation</p></td>
<td width="33%" valign="top"><a href="projects/ccus-india/"><img src="assets/previews/ccus.jpg" alt="Carbon capture presentation cover"></a><p>Carbon capture in India</p></td>
</tr></table>

Group contributors are credited on each project page. References and figure credits are in the original documents.

## View locally

Open `index.html` in a browser. No installation is needed. The notebook pages display code and saved outputs without running it.

To edit the site, see [PUBLISHING.md](PUBLISHING.md).
'''


def main() -> None:
    readers = 0
    for p in PROJECTS:
        path = ROOT / 'projects' / p['id']
        (path / 'index.html').write_text(project_page(p), encoding='utf-8')
        (path / 'README.md').write_text(project_readme(p), encoding='utf-8')
        for f in p['files']:
            if f['kind'] == 'Notebook':
                (path / 'notebook.html').write_text(notebook_page(p, f), encoding='utf-8')
                readers += 1
    (ROOT / 'index.html').write_text(root_page(), encoding='utf-8')
    (ROOT / 'README.md').write_text(root_readme(), encoding='utf-8')
    print(f'Built {len(PROJECTS)} project pages, {readers} notebook readers and the home page.')


if __name__ == '__main__':
    main()
