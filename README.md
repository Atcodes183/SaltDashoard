# Chemistry Dashboard — Salt Analysis

A self-contained, single-page quiz app for practicing qualitative salt
analysis: anion analysis, preliminary tests, and the cation group
division scheme. Built as a static site — no backend required.

## Contents

| File             | Purpose                                                            |
|-------------------|---------------------------------------------------------------------|
| `index.html`      | The app: markup, styles, and all quiz logic (fetches `questions.json` at load time) |
| `questions.json`  | All question banks (anion analysis + preliminary tests/cation groups) and their category color maps |
| `netlify.toml`    | Deploy configuration for Netlify (publish directory, headers, SPA redirect) |
| `README.md`       | This file |

## Features

- **Anion Analysis** and **Preliminary Tests & Cation Groups** sections,
  each a self-contained multiple-choice run with instant feedback
- Question navigator grid with per-question status (current / correct /
  wrong / skipped)
- End-of-run report and persisted **test history** across attempts
  (stored in the browser)
- Smooth animated transitions between dashboard, quiz, report, and
  history views

## Running locally

Because `index.html` loads `questions.json` via `fetch()`, opening the
file directly as `file://` will fail in most browsers (CORS restrictions
on local file fetches). Serve the folder over HTTP instead, e.g.:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

or any static file server of your choice.

## Deploying

### Netlify

Push this repo to GitHub and connect it to Netlify (or drag-and-drop the
folder into Netlify's dashboard). `netlify.toml` is already configured
with `publish = "."`, so no extra build step is needed.

### GitHub Pages

Enable Pages for this repo (Settings → Pages → Deploy from branch) and
point it at the branch/root containing `index.html`. No build step is
required.

## Editing questions

All questions live in `questions.json`, grouped under `anion` and
`prelim`, each with a `questions` array and a `catColors` map (category
name → hex color used in the UI). Each question has the shape:

```json
{
  "cat": "CATEGORY NAME",
  "q": "Question text (HTML tags like <sub>/<sup> are allowed)",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "expl": "Explanation shown after answering"
}
```

Add a new question by appending an object to the relevant array; add a
new category by adding an entry to the corresponding `catColors` map.
