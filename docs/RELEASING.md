# Releasing the data and getting DOIs

The repository is archived on [Zenodo](https://zenodo.org) through Zenodo's
GitHub integration. Every time a **GitHub release** is published, Zenodo
downloads that release, stores it permanently and gives it a DOI. Zenodo also
keeps one **concept DOI** that always points to the newest release ("Cite all
versions"). The database pages show the concept DOI.

Zenodo copies cannot be deleted, so check a release before publishing it.

## What Zenodo receives

- The whole repository at the release tag, except the folders marked
  `export-ignore` in `.gitattributes` (book covers and photographs in
  `site/images/`, and `site/press/`), which carry their own rights.
- The title, authors, description, licence and keywords from `.zenodo.json`.
  (`CITATION.cff` gives the same details to GitHub's "Cite this repository"
  button and to reference managers.)
- The version number from the release tag.

## One-time setup (the repository owner, about 10 minutes)

1. Go to <https://zenodo.org> and choose **Log in**, then **Log in with GitHub**,
   using the account that owns this repository. If you already have a Zenodo
   account, log in and connect GitHub under **Settings → Linked accounts**.
2. Optional but useful: under **Settings → Linked accounts**, connect ORCID too,
   and send the ORCID iD to the editors so it can be added to `.zenodo.json`
   and `CITATION.cff`.
3. Open the GitHub page in Zenodo: click your name (top right) → **GitHub**, or
   go to <https://zenodo.org/account/settings/github/>.
4. Click **Sync now**. Find `pranotoiskandar-collab/compmigrationlaw` in the
   list and switch it **On**. (If GitHub asks you to approve Zenodo's access,
   approve it.)

Nothing is archived yet. Archiving starts with the first release.

## Making a release

1. Bring the database versions up to date. If a database changed since the last
   release, raise its version in its page (the `version` and `dateModified` in
   the page's Dataset metadata and the visible version line), then run
   `python3 tools/cite_blocks.py` so its citation follows.
2. Add a section to `CHANGELOG.md` with the new tag, the table of database
   versions and a few lines on what changed.
3. Merge these changes into `main`.
4. On GitHub, open the repository → **Releases** → **Draft a new release**.
   - **Choose a tag**: type the new tag, for example `v2026.11`, and pick
     *Create new tag on publish*. Target: `main`.
   - **Release title**: for example *Migration Jurisprudence from the South,
     November 2026*.
   - **Description**: paste the new section of `CHANGELOG.md`.
   - Click **Publish release**.
5. After a few minutes the release appears on Zenodo's GitHub page with a DOI
   badge. Open the record and check the authors, title and files.

## After the first release: put the DOI on the site

1. On the Zenodo record, find **Versions → Cite all versions?** The DOI shown
   there (for example `10.5281/zenodo.1234567`) is the concept DOI.
2. In `tools/citation.json`, set `"doi"` to that DOI and `"collection_version"`
   to the release tag without the `v` (for example `2026.11`).
3. Run `python3 tools/cite_blocks.py`. It adds the DOI to the citation on every
   database page, to each page's Dataset metadata and to `CITATION.cff`.
4. Add the Zenodo DOI badge to the top of `README.md` (Zenodo shows the
   Markdown for it on the record page).
5. Open a pull request with these changes.

For later releases, only `"collection_version"` changes; the concept DOI stays
the same.

## Release rhythm

One release a month, together with the monthly update, is enough. Make an
extra release when a database gets a new major version or a correction that
readers should be able to cite (tag it `vYYYY.MM.1`).

## Keeping the citation blocks in step

The "How to cite" block on each database page is written by
`tools/cite_blocks.py` between `<!-- imr-cite:start -->` and
`<!-- imr-cite:end -->`. The check that runs on every pull request fails if a
page's citation no longer matches its version. Run the script after rebuilding
any page with the older build scripts in `build/`.
