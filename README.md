# The Vinland Herald

The Vinland Herald is the Commonwealth's newspaper of record, founded in 1867 in Karontoborg.

Read the paper at <https://arttuahola-beep.github.io/vinland-herald/>.

The site is plain static files, published from the root of this repository. There is no build step on the server.

## Adding an issue

1. Create `issues/YYYY-MM-DD/` with the edition's `index.html` and `issue.md`.
2. On the issue page, keep the navigation bar at the top. From that folder the links are relative: Front page is `../../`, Archive is `../../archive/`, and the favicon is `../../favicon.svg`.

```html
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<nav class="site-nav" aria-label="The Vinland Herald"><a class="nav-home" href="../../">Front page</a><a class="nav-archive" href="../../archive/">Archive</a></nav>
```

3. Add an entry to `issues/issues.json`. Entries use these fields:

| Field | Meaning |
| --- | --- |
| `date` | Publication date, `YYYY-MM-DD` |
| `volume` | Volume as printed, e.g. `CLX` |
| `number` | Issue number as printed, e.g. `49,318` |
| `lead_headline` | Front-page lead headline |
| `path` | Path from the site root, e.g. `issues/2026-09-26/` |

4. From the repository root, regenerate the front page and the archive:

```sh
python3 scripts/build_site.py
```

The script (Python standard library only) copies the newest issue to `index.html`, adjusts that copy's navigation and favicon links for the site root, and writes `archive/index.html` with every issue, newest first.

5. Commit the new issue, `issues/issues.json`, and the generated pages.

Use relative links throughout. The paper is served under `/vinland-herald/`, so a leading-slash path would leave the project site.
