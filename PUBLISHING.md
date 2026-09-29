# Editing the portfolio

## Preview

Open `index.html` in a browser. The site works without an internet connection or an installation.

Alternatively, serve this folder locally:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Stop the server with `Ctrl+C`.

## Change a description

Edit `catalogue/projects.json`. Each entry contains its title, short card description, project description, tags, file records and credits. The `categories` field controls the Papers, Code and Visual work filters. A project can appear in more than one category.

Rebuild the pages and run the checks:

```bash
python3 tools/build_portfolio.py
python3 -m unittest discover -s tests -v
```

The build updates `index.html`, the root README, each project page and README, and the notebook readers. Edit the catalogue or `tools/build_portfolio.py` rather than those generated files. Styling and interactions are in `assets/portfolio.css` and `assets/portfolio.js`.

The README screenshot, `assets/portfolio-preview.jpg`, is a static image. Replace it after a substantial visual change.

## Update the existing repository

From your local repository, review and commit the changes:

```bash
git status
git diff --stat
git add README.md PUBLISHING.md index.html assets catalogue projects tools tests
git commit -m "portfolio: cut the extra text and simplify the project pages"
git push
```

There is no need to create a new repository, remove `.git`, or force-push. Keep your existing Pages settings. The site files are built into the repository root.

## Original files

The PDFs and notebooks are not modified or executed by the build. Their file records include SHA-256 checksums so the tests can detect accidental changes. If you intentionally replace a source file, update its record too.

The notebook readers show saved code, text and PNG outputs. They do not execute notebook HTML or JavaScript. Live services and missing notebook inputs have not been retested; the relevant project pages include short file notes.
