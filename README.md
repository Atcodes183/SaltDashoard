# Chemistry Dashboard — Salt Analysis

A self-contained, single-page study + quiz app for qualitative salt
analysis. Built as a static site — no backend required.

## Navigation structure

```
Chemistry
 ├─ Salt Analysis
 │   ├─ Anion Analysis
 │   │   ├─ Study               (full, nothing-skipped overview)
 │   │   ├─ 30-Min Quick Revision (condensed cheat sheet)
 │   │   └─ Flashcards / Quick Quiz (105-question MCQ run)
 │   ├─ Preliminary Tests & Cation Groups
 │   │   ├─ Study                (full overview)
 │   │   ├─ 30-Min Quick Revision
 │   │   └─ Flashcards / Quick Quiz (74-question MCQ run)
 │   └─ Test Report              (common to both sections above —
 │                                 past attempts & accuracy trend)
 └─ Hydrocarbons
     ├─ Alkane
     │   ├─ Study                (full overview)
     │   ├─ 30-Min Quick Revision
     │   └─ Flashcards / Quick Quiz (35-question MCQ run)
     └─ Test Report              (past attempts & accuracy trend
                                   for this chapter's sections)
```

- **Study** renders the full transcribed class notes for that category
  (group reagents, every confirmatory test, every color reaction and
  equation) first, followed by a collapsible list of every question in
  that category from the quiz bank (question + correct answer + full
  explanation). A jump-to-category nav sits at the top. Nothing is
  shortened or left out.
- **30-Min Quick Revision** condenses the same material to one line per
  fact (answer + the first clause of its explanation), grouped by
  category in a two-column scan layout, meant to be read start to
  finish in about half an hour.
- **Flashcards / Quick Quiz** is the original multiple-choice run with
  instant feedback, a question navigator, and an end-of-run report.
- **Test Report** is scoped per chapter — Salt Analysis and
  Hydrocarbons each have their own Test Report card, and each shows
  every past quiz attempt for that chapter's sections only (e.g. the
  Hydrocarbons report shows Alkane attempts, not Anion/Prelim ones),
  without needing to submit a new run to check.

Study and Revision content is generated at runtime directly from the
question bank in `questions.json` (see "Editing questions" below) —
there's no separate content file to keep in sync.

Adding a new chapter (beyond Salt Analysis / Hydrocarbons) means: a
chapter card in `#chem-hub`, a chapter dashboard `<div class="app-shell">`
(copy `#dashboard-hydro` as a template), an entry in `CHAPTER_META` and
one `SECTION_CHAPTER` mapping per section it contains — everything else
(Study/Revision/Flashcards/quiz app/history) is already generic and
keys off those two lookups.

## Contents

| File             | Purpose                                                            |
|-------------------|---------------------------------------------------------------------|
| `index.html`      | The app: markup, styles, all navigation/quiz/study/revision logic, and the transcribed `STUDY_NOTES` reference content (fetches `questions.json` at load time) |
| `questions.json`  | All question banks (anion analysis, preliminary tests/cation groups, and alkane) and their category color maps — powers Flashcards and the 30-Min Revision cheat sheet |
| `netlify.toml`    | Deploy configuration for Netlify (publish directory, headers, SPA redirect) |
| `README.md`       | This file |

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

All questions live in `questions.json`, grouped under `anion`, `prelim`,
and `alkane`, each with a `questions` array and a `catColors` map
(category name → hex color used throughout the UI). Each question has
the shape:

```json
{
  "cat": "CATEGORY NAME",
  "q": "Question text (HTML tags like <sub>/<sup> are allowed)",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "expl": "Explanation shown after answering, and used verbatim in Study/Revision"
}
```

Add a new question by appending an object to the relevant array — it
will automatically appear in Flashcards, Study, and 30-Min Revision for
that section. Add a new category by adding an entry to the
corresponding `catColors` map; the first question tagged with that
`cat` name will create the new section automatically.

## Study reference notes

The rich per-category notes shown at the top of each Study category
(reagents, tests, equations, tables) live in the `STUDY_NOTES` constant
near the top of the JS in `index.html`, keyed by section → category
name — the category names must match the `cat` values used in
`questions.json` exactly. The `anion`/`prelim` notes were transcribed
from "Class Notes/Assignment Part 01" (Preliminary Tests & Cation
Groups) and "Part 02" (Anion Analysis) by Vikrant Kumar (VCH Sir); the
`alkane` notes were compiled from the Hydrocarbons "Part 01" class
notes covering nomenclature, isomerism, preparation methods, physical
properties, free-radical halogenation, combustion/oxidation/cracking,
and ethane conformations. To add or correct notes for a category, edit
the matching template-literal string in `STUDY_NOTES`.

The quiz-bank facts shown further down each Study category (and all of
30-Min Revision) are generated purely from `questions.json`'s `q` /
`options[correct]` / `expl` fields, so any question you add there
automatically appears in Flashcards, Study, and Revision.
