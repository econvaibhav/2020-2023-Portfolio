#!/usr/bin/env python3
"""Build the static portfolio and notebook readers without executing coursework.

Run from any directory with Python 3.10 or later. Only the standard library is used.
The project descriptions and source-file records live in catalogue/projects.json.
"""
from __future__ import annotations

import base64
from html import escape
import json
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
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Vaibhav Agarwal</title><meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#f8f7f3"><meta name="color-scheme" content="light">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/portfolio.css"><script src="{prefix}assets/portfolio.js" defer></script>
</head><body><a class="skip" href="#main">Skip to content</a>
<header class="topbar"><div class="wrap topbar-inner"><a class="brand" href="{prefix}index.html"><span class="brand-name">Vaibhav Agarwal</span><span class="brand-year">2020–2023</span></a>
<nav aria-label="Main navigation"><a href="{prefix}index.html#work">Work</a><a href="{prefix}index.html#gallery">Gallery</a><a class="nav-atlas" href="{prefix}index.html#connections">Connections</a><a href="{prefix}index.html#about">About</a></nav></div></header>'''

def foot(prefix: str = '') -> str:
    return f'''<footer class="footer"><div class="wrap footer-inner"><span>Vaibhav Agarwal · BA Economics · Azim Premji University</span><span>Questions, evidence, interpretation. &nbsp; <a href="{prefix}index.html#work">Back to the work ↑</a></span></div></footer>
<dialog class="dialog" id="zoom-dialog" aria-labelledby="zoom-title"><div class="dialog-head"><h2 id="zoom-title">A closer look</h2><button type="button" data-close>Close ×</button></div><img id="zoom-image" class="zoom-image" alt=""><p id="zoom-caption" class="zoom-caption"></p></dialog>
</body></html>'''

def file_label(f: dict[str, Any]) -> str:
    return f"{f['pages']} pages · PDF" if 'pages' in f else f"{f['cells']} cells · Python notebook"

def original_href(p: dict[str, Any], f: dict[str, Any], prefix: str = '') -> str:
    url = prefix + quote(f['name'])
    return url + (f"#page={f.get('start', 1)}" if f['kind'] == 'PDF' else '')

def preview(p: dict[str, Any], prefix: str = '', cls: str = '') -> str:
    v = p['preview']
    return f'<img class="{cls}" src="{prefix}assets/previews/{esc(v["image"])}" alt="{esc(v["alt"])}" loading="lazy" decoding="async">'

def artifact_list(p: dict[str, Any]) -> str:
    rows = []
    for f in p['files']:
        a = link(original_href(p, f), f['label'])
        if f['kind'] == 'Notebook':
            a = link('notebook.html', 'Read the notebook in your browser') + '<br>' + link(f['name'], 'Original .ipynb', **{'class': 'read-link', 'download': ''})
        rows.append(f'<li><div>{a}</div><small>{file_label(f)}</small></li>')
    return '<ul class="artifact-list">' + ''.join(rows) + '</ul>'

def project_page(p: dict[str, Any]) -> str:
    pr = p['preview']; arg = p['argument_source']; arg_href = ('notebook.html#cell-' + str(arg['page'])) if arg['kind'] == 'cell' else quote(arg['file'])+'#page='+str(arg['page']); original = quote(pr['file']) + (f'#page={pr["page"]}' if pr['page'] else '')
    if not pr['page']: original = 'notebook.html'
    guides = ''.join(f'<div>{link(quote(m["file"])+"#page="+str(m["page"]),m["label"]+" ↗")}<p>{esc(m["note"])} <span class="eyebrow">PDF p. {m["page"]}</span></p></div>' for m in p['inspect'])
    if not guides:
        guides = '<div><a href="notebook.html">Read the original cells and saved outputs ↗</a><p>The browser reader shows code, stored text and PNG figures without running the notebook. Cell numbers provide stable reading landmarks.</p></div>'
        if p['id']=='public-distribution-scraping':
            guides += '<div><a href="notebook.html#cell-7">Table extraction · cell 7 ↗</a><p>From HTML rows to a tab-separated representation.</p></div><div><a href="notebook.html#cell-12">Numeric conversion · cell 12 ↗</a><p>Formatting and missing-value handling made explicit.</p></div>'
        elif p['id']=='piotroski-stock-scoring':
            guides += '<div><a href="notebook.html#cell-8">Accounting entries · cell 8 ↗</a><p>The positional indexing on which the calculations depend.</p></div><div><a href="notebook.html#cell-16">Cash flow and score logic · cell 16 ↗</a><p>A concrete condition and score increment.</p></div>'
    tags=' '.join(f'<span class="tag">{esc(t)}</span>' for t in p['method_tags'])
    related=''.join(f'<a href="../{id}/index.html"><span class="eyebrow">{esc(BY_ID[id]["area"])}</span><h3>{esc(BY_ID[id]["title"])} ↗</h3><p>{esc(BY_ID[id]["short"])}</p></a>' for id in p['related'])
    return head(p['title'],p['short'],'../../')+f'''
<main id="main" class="wrap">
<section class="case-hero"><p class="breadcrumb"><a href="../../index.html#work">Selected work</a> / {p['number']}</p><p class="eyebrow">{esc(p['area'])}</p><h1>{esc(p['title'])}</h1><p class="case-deck">{esc(p['question'])}</p><div class="hero-actions"><a class="button dark" href="#evidence">Open the work <span>↓</span></a><span>{tags}</span></div></section>
<section class="case-layout" aria-label="Substance and methods"><div class="case-lenses"><article><p class="eyebrow">01 / Substance</p><h2>The question behind the work</h2><p>{esc(p['substance'])}</p></article><article><p class="eyebrow">02 / Methods</p><h2>{esc(p['method_question'])}</h2><p>{esc(p['methods'])}</p></article></div><figure class="case-visual"><a href="../../assets/previews/{pr['image']}" data-zoom data-caption="{esc(pr['caption'])}">{preview(p,'../../')}</a><figcaption>{esc(pr['caption'])} &nbsp; {link(original,'Open the source ↗')}</figcaption></figure></section>
<section class="argument-panel"><p class="eyebrow">Read for the argument</p><h2>What the work brings out</h2><p>{esc(p['argument'])}</p><a class="argument-source" href="{arg_href}">Read it in the original · {arg['kind']} {arg['page']} ↗</a></section>
<section class="bridge"><h2>The connection</h2><p>{esc(p['bridge'])}</p></section>
<section class="section"><p class="eyebrow">From question to evidence</p><h2 style="margin-top:12px">How the work is put together</h2><div class="work-steps">{''.join(f'<div class="work-step"><span class="number">0{i+1}</span>{esc(s)}</div>' for i,s in enumerate(p['steps']))}</div></section>
<section class="section" id="evidence"><div class="evidence-layout"><div><p class="eyebrow">Original artifacts</p><h2 style="margin-top:12px">Read the work</h2>{artifact_list(p)}<p class="source-meta">The original documents and notebooks are kept alongside this project page. Page references count from the first PDF page, including covers.</p></div><div><p class="eyebrow">A way in</p><h2 style="margin-top:12px">Where to look first</h2><div class="reading-guide">{guides}</div></div></div><details class="scope"><summary>Scope, interpretation &amp; what is available</summary><p>{esc(p['scope'])}</p></details><div class="credits"><strong>Credit.</strong> {esc(p['credits'])}</div></section>
<section class="section"><p class="eyebrow">Keep following the question</p><div class="related">{related}</div></section>
</main>'''+foot('../../')

def project_readme(p: dict[str, Any]) -> str:
    pr=p['preview']
    parts=[f"# {p['title']}",f"**{p['question']}**",f"[Back to the portfolio](../../README.md) · [Browser project page](index.html)",f"![{pr['alt']}](../../assets/previews/{pr['image']})",f"*{pr['caption']}*","## Substance",p['substance'],"## Methods",p['methods'],"## What the work brings out",p['argument'],"## The connection",p['bridge'],"## Open the work"]
    for f in p['files']:
        url=quote(f['name']); parts.append(f"- [{f['label']}]({url}) · {file_label(f)}")
        if f['kind']=='Notebook':parts.append('  [Read code and saved outputs in a browser](notebook.html).')
    if p['inspect']:
        parts.append('## Where to look first')
        for m in p['inspect']: parts.append(f"**[{m['label']}]({quote(m['file'])}#page={m['page']})**, PDF p. {m['page']}. {m['note']}")
    parts.extend(['<details>\n<summary>Scope, interpretation and available material</summary>\n',p['scope'],'\n</details>','## Credit',p['credits'],'## Connected work'])
    parts.append(' · '.join(f"[{BY_ID[id]['title']}](../{id}/)" for id in p['related']))
    return '\n\n'.join(parts)+'\n'

def source_text(value: Any) -> str:
    if isinstance(value,list): return ''.join(str(item) for item in value)
    return str(value or '')

def notebook_page(p: dict[str, Any], f: dict[str, Any]) -> str:
    nb=json.loads((ROOT/'projects'/p['id']/f['name']).read_text(encoding='utf-8'))
    cells=[]
    for i,cell in enumerate(nb['cells'],1):
        code=cell['cell_type']=='code'
        source=esc(source_text(cell.get('source','')))
        outputs=[]
        for out in cell.get('outputs',[]):
            data=out.get('data',{})
            png=source_text(data.get('image/png',''))
            if png:
                # Only a validated base64 PNG is embedded; notebook HTML/JS is never executed.
                raw=base64.b64decode(png,validate=False)
                if not raw.startswith(b'\x89PNG\r\n\x1a\n'): raise ValueError(f'Invalid PNG in {f["name"]}, cell {i}')
                safe=base64.b64encode(raw).decode('ascii')
                outputs.append(f'<img src="data:image/png;base64,{safe}" alt="Original saved plot from notebook cell {i}" loading="lazy">')
            txt=source_text(out.get('text','')) or source_text(data.get('text/plain',''))
            if txt and not (png and txt.lstrip().startswith('<Figure')):
                outputs.append(f'<details><summary>Saved text output</summary><pre>{esc(txt)}</pre></details>')
            if out.get('output_type')=='error':
                outputs.append(f'<details><summary>Saved error from the original run</summary><pre>{esc(out.get("ename", "Error"))}: {esc(out.get("evalue", ""))}</pre></details>')
            if 'text/html' in data and not png and not txt:
                outputs.append('<p class="omitted">Active HTML/interactive output remains in the original notebook. This reader does not execute it.</p>')
        kind='code-source' if code else 'markdown-source'
        cells.append(f'<section class="notebook-cell" id="cell-{i}"><div class="cell-label"><a href="#cell-{i}">CELL {i:02}</a><br>{"PYTHON" if code else "MARKDOWN"}</div><div class="cell-body"><pre class="{kind}">{source}</pre><div class="cell-output">{"".join(outputs)}</div></div></section>')
    return head(p['title']+' / Notebook', 'The original notebook, readable without execution.','../../')+f'''<main id="main" class="wrap"><div class="reader-header"><p class="breadcrumb"><a href="index.html">← {esc(p['title'])}</a></p><p class="eyebrow">Original notebook / {len(nb['cells'])} cells</p><h1>Inside the work.</h1><p>This reader preserves the original cell order, code, stored text and PNG outputs. It does not run code or replay active HTML and Plotly outputs. Saved errors remain available to inspect. For the complete notebook, including interactive outputs, use the file below.</p><p>{link(f['name'],'Download the original .ipynb',download='')}</p><div class="reader-controls js-only js-flex"><button data-reader-toggle="code" aria-pressed="true">Hide code</button><button data-reader-toggle="output" aria-pressed="true">Hide saved outputs</button></div></div><div class="reader">{''.join(cells)}</div></main>'''+foot('../../')

def card(p: dict[str, Any]) -> str:
    attrs={
        'id':p['id'],'title':p['title'],'area':p['area'],
        'subjects':'|'.join(p['substance_tags']),'methods':'|'.join(p['method_tags']),
        'search':' '.join([p['title'],p['question'],p['method_question'],p['substance'],p['methods'],*p['method_tags'],*p['substance_tags']]).lower(),
        'substance':p['substance'],'methodtext':p['methods'],'bridge':p['bridge'],
        'evidence':'; '.join(f"{f['label']} ({file_label(f)})" for f in p['files'])
    }
    data=' '.join(f'data-{k}="{esc(v)}"' for k,v in attrs.items())
    return f'''<article class="project-card" {data} id="project-{p['id']}"><a href="projects/{p['id']}/index.html" class="card-image">{preview(p)}</a><div class="card-meta"><span>{p['number']} / {esc(p['area'])}</span><span>{'COLLABORATIVE' if p['credits'].startswith('Group') else 'PROJECT'}</span></div><h3><a href="projects/{p['id']}/index.html">{esc(p['title'])}</a></h3><div class="lens-content" data-view="substance"><p class="lens-question">{esc(p['question'])}</p><p class="lens-text">{esc(p['short'])}</p></div><div class="lens-content" data-view="methods"><p class="lens-question">{esc(p['method_question'])}</p><p class="lens-text">{esc(p['methods'])}</p></div><div class="tagline">{''.join(f'<span class="tag">{esc(t)}</span>' for t in p['method_tags'])}</div><div class="card-bottom"><a href="projects/{p['id']}/index.html">Read the project ↗</a><label class="compare-check js-only"><input type="checkbox" data-compare="{p['id']}" aria-label="Compare {esc(p['title'])}"> Compare</label></div></article>'''

def gallery_piece(id: str, title: str, tall: bool = False) -> str:
    p=BY_ID[id];pr=p['preview']
    return f'''<figure class="gallery-piece {'tall' if tall else ''}"><a class="mat" href="assets/previews/{pr['image']}" data-zoom data-caption="{esc(pr['caption'])}">{preview(p)}</a><figcaption><strong>{esc(title)}</strong><a href="projects/{id}/index.html">View project ↗</a></figcaption></figure>'''

def root_page() -> str:
    subs=sorted({t for p in PROJECTS for t in p['substance_tags']})
    meth=sorted({t for p in PROJECTS for t in p['method_tags']})
    options=lambda tags: ''.join(f'<option value="{esc(t)}">{esc(t)}</option>' for t in tags)
    artifact_count=sum(len(p['files']) for p in PROJECTS)
    families=[('Model','Regression'),('Build data','Data assembly'),('Microdata','Microdata'),('Design','Visualisation'),('Measurement','Measurement'),('Code','Python')]
    rows=''.join('<tr><th scope="row">'+link(f'projects/{p["id"]}/index.html',p['title'])+'</th>'+''.join('<td>'+('<span class="dot" aria-hidden="true"></span><span class="sr-only">Included</span>' if t in p['method_tags'] else '<span aria-label="Not a focus">·</span>')+'</td>' for _,t in families)+'</tr>' for p in PROJECTS)
    # Labels inside sr-only spans preserve the matrix meaning for screen readers.
    return head('2020–2023 Portfolio','Selected economics, computational and visual work. Substance and methods, read together.')+f'''
<main id="main">
<div class="wrap"><section class="hero"><div><p class="eyebrow">Selected work / BA Economics / Azim Premji University</p><h1>Questions first.<br><em>Methods that<br>follow.</em></h1><p class="hero-lead">A portfolio about development, inequality and the environment. And about what it takes to turn a question into evidence someone else can inspect.</p><div class="hero-actions"><a href="#work" class="button dark">Explore the work <span>↓</span></a><a class="text-link" href="#argument">The connection between them ↗</a></div></div><div class="hero-art" aria-label="A selection of original portfolio work"><a class="plate one" href="projects/india-china-development/index.html"><img src="assets/previews/timeline.jpg" alt="Original India–China historical timeline"></a><a class="plate two" href="projects/data-visualization/index.html"><img src="assets/previews/visualisation.jpg" alt="Original colour-blind-friendly visualisation poster"></a><a class="plate three" href="projects/ccus-india/index.html"><img src="assets/previews/ccus.jpg" alt="Original CCUS presentation cover"></a><p class="artifact-caption">Original pages, posters and presentations from the work.</p></div></section>
<div class="ledger"><div class="statement">Substance gives the question.<br>Methods make it inspectable.</div><div><strong>{len(PROJECTS)}</strong><span>selected projects</span></div><div><strong>{artifact_count}</strong><span>original artifacts</span></div><div><strong>Two lenses</strong><span>substance + methods</span></div></div>
<section class="section" id="argument"><div class="thesis-grid"><div><p class="eyebrow" style="margin-bottom:17px">The argument running through the work</p><h2>Not a move away<br>from economics.<br>A wider way to study it.</h2></div><div class="copy"><p>The subjects change: renewable investment, household health expenditure, education, public-service data. The recurring task does not. Define a question, decide what would count as evidence, and make the analytical choices visible.</p><p><strong>The substance matters.</strong> Growth is not the same question as distribution. Recorded spending is not the same measure as health. An administrative category is not the social event itself.</p><p><strong>The method matters just as much.</strong> Models, scraping, microdata and visual design each make some things easier to see and leave other things unresolved. That connection is what this portfolio brings into focus.</p></div></div><div class="thought-line"><div><strong>Question</strong><span>What am I trying to understand?</span></div><div><strong>Measurement</strong><span>What would stand for it in data?</span></div><div><strong>Method</strong><span>How can the evidence be examined?</span></div><div><strong>Interpretation</strong><span>What does the result actually support?</span></div></div></section>
<section class="section" id="work"><div class="section-head"><div><p class="eyebrow">01 / Selected work</p><h2>One collection.<br>Two ways in.</h2></div><p>Read for the subject, or switch to the method. Open any project for its argument, analytical steps and original work. Select two to compare how their evidence is built.</p></div>
<noscript><p class="noscript">All projects and both reading lenses are available below. Search, filters and comparison become available with JavaScript enabled.</p></noscript>
<div class="filter-panel js-only" style="display:block" id="filter-panel"><div class="filter-row"><div class="lens" role="group" aria-label="Reading lens"><button data-lens="substance" aria-pressed="true">Substance</button><button data-lens="methods" aria-pressed="false">Methods</button></div><label class="filter-control"><span class="filter-label">Subject</span><select id="subject-filter"><option value="">All subjects</option>{options(subs)}</select></label><label class="filter-control"><span class="filter-label">Method</span><select id="method-filter"><option value="">All methods</option>{options(meth)}</select></label><label class="search-box"><span class="sr-only">Search projects</span><input class="search" id="project-search" type="search" placeholder="Search a question, dataset or tool…" autocomplete="off"></label></div><div class="filter-state"><span id="result-count" role="status" aria-live="polite">12 projects</span><button class="reset" id="reset-filters">Reset filters</button></div></div>
<div class="project-grid">{''.join(card(p) for p in PROJECTS)}</div><p id="empty-state" class="empty" hidden>No matching projects. Try another subject, method or search term.</p>
</section>
<section class="section" id="gallery"><div class="section-head"><div><p class="eyebrow">02 / Visual work</p><h2>Evidence has a<br>visual language.</h2></div><p>A timeline, an accessibility poster and an interdisciplinary presentation. These are pages from the original work, not illustrations made to decorate the portfolio. Open an image for a closer look.</p></div><div class="gallery-grid">{gallery_piece('india-china-development','History as a visual comparison')}{gallery_piece('data-visualization','Designing for different readers',True)}{gallery_piece('ccus-india','Explaining a technical system')}</div></section>
<section class="section" id="connections"><div class="section-head"><div><p class="eyebrow">03 / Connections</p><h2>Follow a question<br>across the portfolio.</h2></div><p>These are reading paths, not rankings. Each connects a substantive problem to a different way of constructing or questioning its evidence.</p></div><div class="routes"><article class="route"><span class="eyebrow">Path 01 / Theory into evidence</span><h3>How would we know?</h3><p>Start with a model, examine a published study, then ask what changes across groups.</p><ol><li><a href="projects/renewable-energy-growth/index.html">Renewable energy &amp; growth</a></li><li><a href="projects/replication-water-pricing/index.html">Water-pricing replication</a></li><li><a href="projects/education-and-wages/index.html">Education &amp; labour markets</a></li></ol></article><article class="route"><span class="eyebrow">Path 02 / Building the observation</span><h3>Before the model.</h3><p>Retrieve the table, define the measure, then question the categories you inherited.</p><ol><li><a href="projects/public-distribution-scraping/index.html">Public-distribution scraping</a></li><li><a href="projects/health-and-livelihoods/index.html">Household health &amp; livelihoods</a></li><li><a href="projects/crime-data-categories/index.html">Crime-data categorisation</a></li></ol></article><article class="route"><span class="eyebrow">Path 03 / Making an argument visible</span><h3>For the reader.</h3><p>Try different encodings, add historical context and explain a complex system.</p><ol><li><a href="projects/data-visualization/index.html">Accessible visualisation</a></li><li><a href="projects/india-china-development/index.html">India–China timeline</a></li><li><a href="projects/ccus-india/index.html">CCUS report &amp; presentation</a></li></ol></article></div>
<details class="scope"><summary>See the methods across all 12 projects</summary><div class="atlas-wrap"><table class="atlas"><caption class="sr-only">Methods represented across the portfolio. A dot marks a method present in the project, not a skill score.</caption><thead><tr><th>PROJECT</th>{''.join('<th scope="col">'+esc(name)+'</th>' for name,_ in families)}</tr></thead><tbody>{rows}</tbody></table></div><p class="source-meta">A filled dot indicates a method represented in the work. It is not a rating or a claim that every project includes runnable code.</p></details></section>
<section class="section about" id="about"><div><p class="eyebrow">About this collection</p><p class="name">Vaibhav Agarwal</p><p class="muted">BA Economics, 2020–2023<br>Azim Premji University</p></div><div><p>This is a selection of the written, empirical, computational and visual work from my undergraduate portfolio. I have organised it around questions and methods rather than semesters.</p><p>The collection shows the foundations of my move towards computer science and social data science: working with imperfect evidence, making data usable, writing analytical logic and communicating what a result can support.</p><p>Several projects were collaborative. Their project pages name the contributors recorded in the original work; the documents retain the original author lists, figure credits and references.</p></div></section></div></main>
<div class="compare-tray" id="compare-tray" hidden><span id="compare-status" role="status" aria-live="polite"></span><button id="compare-open" disabled>Compare →</button><button id="compare-clear" class="close" aria-label="Clear comparison">×</button></div><dialog class="dialog" id="compare-dialog" aria-labelledby="compare-title"><div class="dialog-head"><div><p class="eyebrow">Substance × methods</p><h2 id="compare-title">Different questions. Different evidence.</h2></div><button data-close>Close ×</button></div><div class="compare-grid" id="compare-body"></div></dialog>
'''+foot()

def root_readme() -> str:
    return '''# 2020–2023 Portfolio

**Vaibhav Agarwal · BA Economics · Azim Premji University**

## Questions first. Methods that follow.

Development, inequality, the environment, and the work of turning a question into evidence someone else can inspect.

[Selected work](#selected-work) · [The visual work](#the-visual-work) · [Connections](#follow-a-question) · [Browse the website](#the-portfolio-website)

![A preview of the portfolio website](assets/portfolio-preview.jpg)

### Substance gives the question. Methods make it inspectable.

This collection is not just a record of moving from economics towards coding. It is about holding two things together: a question worth asking and a way of studying it that another person can examine.

**Substance:** how economies develop; how resources, costs and opportunities are distributed; how technologies interact with institutions; and what the categories in our data leave out.

**Methods:** economic modelling, household microdata, empirical replication, public-data scraping, rule-based computation and visual explanation.

The connection between them is the point. A regression needs a substantive question. A compelling social argument needs evidence. A carefully built dataset still needs an account of what its variables mean.

## Selected work

### 01 / Climate, development and a model that can be inspected

**[Renewable energy & economic growth](projects/renewable-energy-growth/)**

Can renewable investment fit into a model of how economies grow? This project connects an augmented Solow framework to cross-country data, alternative proxies and robustness checks. The research paper, short summary and SRC presentation show the same argument at different levels of detail.

**Substance:** climate and growth. **Methods:** theory-to-variable translation, cross-country data assembly and regression.

### 02 / Everyday conditions, household-level evidence

**[Health & livelihoods](projects/health-and-livelihoods/)**

A group project using NSS social-consumption health data to study household facilities and treatment expenditure. The report, descriptive tables and regression analysis are kept together, making the steps from measurement to interpretation visible.

**Substance:** household amenities, access and the financial burden of illness. **Methods:** microdata, recoding, grouped comparisons and regression.

### 03 / The work before an analysis can begin

**[From a public webpage to a dataset](projects/public-distribution-scraping/)**

A Python notebook that extracts a block-level Jharkhand public-distribution table, cleans its rows, assigns a schema and converts numeric columns. The contribution is the transformation from published information to usable data, not simply the use of a scraping library.

**Substance:** public-service information. **Methods:** Requests, BeautifulSoup, pandas and explicit cleaning rules.

### 04 / The categories are part of the argument

**[What a crime category can hide](projects/crime-data-categories/)**

A 62-page group booklet on categorisation and interpretation, with comparative visual analysis for four states. It connects the recorded series to the definitions, denominators and reporting questions behind them. The closing measurement discussion is worth reading alongside the charts.

**Substance:** administrative records and social interpretation. **Methods:** category review, comparative graphics and measurement critique.

## The visual work

<table>
<tr>
<td width="50%" valign="top">
<a href="projects/data-visualization/"><img src="assets/previews/visualisation.jpg" alt="Original colour-blind-friendly visualisation poster"></a>
<h3>Making evidence legible</h3>
<p>A colour-blind-friendly visualisation poster alongside a Python sketchbook. Design is part of whether an analytical comparison can be understood.</p>
<p><a href="projects/data-visualization/">Poster + notebook →</a></p>
</td>
<td width="50%" valign="top">
<a href="projects/india-china-development/"><img src="assets/previews/timeline.jpg" alt="Original India–China historical timeline"></a>
<h3>Two development paths</h3>
<p>A two-page historical timeline paired with comparisons of social indicators, employment and structural change.</p>
<p><a href="projects/india-china-development/">Timeline + data assignments →</a></p>
<a href="projects/ccus-india/"><img src="assets/previews/ccus.jpg" alt="Original CCUS presentation cover"></a>
<h3>Beyond the technology</h3>
<p>A CCUS review and presentation connecting technical processes to economic, environmental and institutional conditions.</p>
<p><a href="projects/ccus-india/">Report + presentation →</a></p>
</td>
</tr>
</table>

## More questions, different methods

| Work | Substance | Methodological contribution |
|:--|:--|:--|
| [Water-pricing replication](projects/replication-water-pricing/) | Incentives and a water-saving practice | Reconstructing eight published tables; interpreting treatment interactions and specifications |
| [Education & wages](projects/education-and-wages/) | Education across different labour-market settings | PLFS microdata, employment groups, regression and rural–urban interactions |
| [Renewable-energy finance](projects/renewable-finance-geopolitics/) | The geography and form of development finance | Separating loans, grants and equity; country classifications, maps and grouped comparisons |
| [Financial ideas in code](projects/piotroski-stock-scoring/) | Translating an accounting framework into rules | Statement retrieval, ratios and inspectable conditional Python logic |
| [Rajasthan data story](projects/rajasthan-suicide-data-story/) | Interpreting a reported social pattern | Combining maps, tables and narrative while keeping aggregate inference limits visible |

## Follow a question

**How would we know?** [Growth modelling](projects/renewable-energy-growth/) → [Water-pricing replication](projects/replication-water-pricing/) → [Education & wages](projects/education-and-wages/).

**Before the model.** [Scraping administrative data](projects/public-distribution-scraping/) → [Defining household measures](projects/health-and-livelihoods/) → [Questioning inherited categories](projects/crime-data-categories/).

**For the reader.** [Accessible visualisation](projects/data-visualization/) → [Historical context](projects/india-china-development/) → [Explaining a technical system](projects/ccus-india/).

## The portfolio website

The repository includes a complete static website in `index.html`: a substance/methods switch, subject and method filters, search, two-project comparison, a visual gallery, individual project pages and browser-readable notebooks.

To browse locally, open `index.html` in a browser. No installation is needed. To use a local server instead:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8000`. [Publishing instructions](PUBLISHING.md) explain how to put the same site on GitHub Pages.

Project descriptions live in `catalogue/projects.json`. After editing them, run `python3 tools/build_portfolio.py` and `python3 -m unittest discover -s tests -v`. The build never executes the original notebooks.

## The original work

The collection contains **12 projects and 20 original artifacts**. Papers, presentations and notebooks are kept alongside a short account of the substance, methods, available evidence and interpretation limits. A PDF-only project is not presented as a runnable pipeline, and exploratory notebooks remain distinguishable from tested software.

Several pieces were group coursework. Contributors are credited on the individual project pages and in the original author lists. Figure credits and references remain in the source documents.
'''

def main() -> None:
    for p in PROJECTS:
        path=ROOT/'projects'/p['id']
        (path/'index.html').write_text(project_page(p),encoding='utf-8')
        (path/'README.md').write_text(project_readme(p),encoding='utf-8')
        for f in p['files']:
            if f['kind']=='Notebook': (path/'notebook.html').write_text(notebook_page(p,f),encoding='utf-8')
    (ROOT/'index.html').write_text(root_page(),encoding='utf-8')
    (ROOT/'README.md').write_text(root_readme(),encoding='utf-8')
    print(f'Built {len(PROJECTS)} project pages, 3 notebook readers and the portfolio landing page.')

if __name__=='__main__':
    main()
