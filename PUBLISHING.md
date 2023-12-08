# Open and publish the portfolio

The folder is a complete Git repository, including its `.git` directory. Keep that hidden directory when extracting or moving it. The website is already built; no package installation is required to view it.

## View it on your computer

Open `index.html` in a browser. Alternatively, from this folder:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Keep the terminal open while browsing. Stop the server with `Ctrl+C`.

## Publish a new repository

Create an **empty** GitHub repository named **2020-2023-Portfolio**. Leave the automatic README, `.gitignore` and licence options off so the new remote does not have a separate initial commit.

From this extracted folder, check the supplied history:

```bash
git status
git log --oneline --reverse
```

Replace `YOUR-USERNAME` below with the account that owns the new repository:

```bash
git remote add origin https://github.com/YOUR-USERNAME/2020-2023-Portfolio.git
git push -u origin main
```

This pushes the supplied commit history as well as the files. Uploading the visible files through the GitHub website does not transfer the local history. Do not run `git init` again or remove `.git`.

The repository uses the GitHub noreply author address found on the existing EU-Political-NER repository. Check your own identity settings before making future commits.

If a remote called `origin` already exists, inspect it with `git remote -v` before changing anything. These instructions are for a new empty remote, not for overwriting an existing repository. No force-push is needed.

## Enable the portfolio website

In the new repository, open **Settings → Pages**. Under **Build and deployment**, choose:

- **Source:** Deploy from a branch
- **Branch:** `main`
- **Folder:** `/ (root)`

Save the settings. GitHub will show the published website address on that page after deployment. Add that address to the repository’s **About → Website** field. The root `index.html` and `.nojekyll` are already included.

Official instructions: [Configure a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Update the content

Edit project titles, descriptions, reading guides and credits in `catalogue/projects.json`, then rebuild:

```bash
python3 tools/build_portfolio.py
python3 -m unittest discover -s tests -v
```

The generator updates the landing page, root README, individual project pages, project READMEs and static notebook readers. It does not modify or execute the source PDFs or notebooks. Styling and interactions live in `assets/portfolio.css` and `assets/portfolio.js`.

The source-file records include SHA-256 digests so tests can detect accidental changes to original artifacts. If you intentionally replace a source file, update its record and verify the change. Image previews and the screenshot in the README are separate static assets.

## About the notebooks

The HTML readers show the original cell order, code, saved PNG figures and text outputs. They do not execute notebook HTML or JavaScript. Use the original `.ipynb` files for interactive outputs.

The coursework notebooks have not been rerun against live services. Their project pages explain missing inputs and implementation-specific issues. The automated checks validate portfolio structure, links, source integrity and notebook format; they do not certify the original analyses.
