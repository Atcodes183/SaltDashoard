#!/usr/bin/env python3
"""
add_topic.py — Quick-add a new topic/section to the salt-analysis-site.

USAGE:
    python3 add_topic.py spec.json

spec.json shape:
{
  "key":       "cation",                  // short lowercase id, no spaces
  "title":     "Cation Analysis",         // shown on cards/headers
  "desc":      "Group-wise cation ...",   // one-line description for the nav card
  "chapter":   "salt",                    // must be an EXISTING chapter key (e.g. "salt" or "hydro")
  "icon":      "\ud83e\uddea",                     // one emoji
  "iconColor": "#fbbf24",                 // hex color for the icon
  "wide":      false,                     // true = full-width card on the dashboard grid
  "catColors": { "CATEGORY NAME": "#hex", ... },
  "notes":     { "CATEGORY NAME": "<p>...</p>", ... },   // STUDY_NOTES html, keyed by category
  "questions": [
    {"cat": "CATEGORY NAME", "q": "...", "options": ["a","b","c","d"], "correct": 0, "expl": "..."},
    ...
  ]
}

The "cat" values used inside "questions" MUST match keys used in "catColors"
(and ideally in "notes") — that's how the Study/Revision views group things.

This script only supports adding a section to an EXISTING chapter (salt or
hydro right now). It edits questions.json and index.html in place. Always
run it on a fresh copy / after a git commit so changes are easy to diff or
revert.
"""
import json, re, sys, pathlib

SITE_DIR = pathlib.Path(__file__).parent
HTML_PATH = SITE_DIR / "index.html"
JSON_PATH = SITE_DIR / "questions.json"

CHAPTER_MORE_NOTE = {
    "salt": "More sections (e.g. cation analysis, systematic scheme) can be added here as separate cards.",
    "hydro": "More sections (e.g. aromatic hydrocarbons) can be added here as separate cards.",
}

# The chapter's Test Report card must always be the LAST card in the
# section-grid. New topic cards are inserted immediately before this
# anchor (not before more-note, which sits outside/after the grid) so
# Test Report never ends up above a newly-added section.
CHAPTER_HISTORY_ANCHOR = {
    "salt": '<div class="section-card wide" id="cardHistory">',
    "hydro": '<div class="section-card wide" id="cardHistoryHydro">',
}


def cap(key):
    return key[0].upper() + key[1:]


def build_notes_block(key, notes):
    parts = [f"{key}: {{\n"]
    cats = list(notes.keys())
    for i, cat in enumerate(cats):
        parts.append(f"'{cat}': `\n{notes[cat]}\n`")
        parts.append(",\n\n" if i < len(cats) - 1 else "\n\n")
    parts.append("}")
    return "".join(parts)


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python3 add_topic.py spec.json")
    spec = json.loads(pathlib.Path(sys.argv[1]).read_text())

    key = spec["key"]
    title = spec["title"]
    desc = spec["desc"]
    chapter = spec["chapter"]
    icon = spec["icon"]
    icon_color = spec["iconColor"]
    wide = spec.get("wide", False)
    cat_colors = spec["catColors"]
    notes = spec.get("notes", {})
    questions = spec["questions"]

    if chapter not in CHAPTER_MORE_NOTE:
        sys.exit(f"Unknown chapter '{chapter}'. Known: {list(CHAPTER_MORE_NOTE)}. "
                  f"New chapters need a manual dashboard block first — ask Claude to add one.")

    html = HTML_PATH.read_text()
    data = json.loads(JSON_PATH.read_text())

    if key in data:
        sys.exit(f"'{key}' already exists in questions.json — pick a different key or remove it first.")

    # ---------- 1. questions.json ----------
    data[key] = {"questions": questions, "catColors": cat_colors}
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # ---------- 2. nav card on the chapter dashboard ----------
    card_id = f"card{cap(key)}"
    wide_cls = " wide" if wide else ""
    card_html = (
        f'      <div class="section-card{wide_cls}" id="{card_id}">\n'
        f'        <div class="icon" style="background:{icon_color}1f; color:{icon_color};">{icon}</div>\n'
        f'        <h3>{title}</h3>\n'
        f'        <p>{desc}</p>\n'
        f'        <div class="meta">\u2192 <span id="{key}Count">0</span> questions</div>\n'
        f'      </div>\n'
    )
    if chapter not in CHAPTER_HISTORY_ANCHOR:
        sys.exit(f"Unknown chapter '{chapter}'. Known: {list(CHAPTER_HISTORY_ANCHOR)}. "
                  f"New chapters need a manual dashboard block first — ask Claude to add one.")
    history_anchor = CHAPTER_HISTORY_ANCHOR[chapter]
    if history_anchor not in html:
        sys.exit("Could not find the chapter's Test Report card anchor — site layout may have changed.")
    html = html.replace(history_anchor, card_html + "      " + history_anchor, 1)

    # ---------- 3. app-shell container ----------
    shell_anchor = "  <!-- ======= HISTORY VIEW ======= -->"
    shell_html = f'  <!-- ======= {title.upper()} APP ======= -->\n' \
                 f'  <div class="app-shell" id="app-{key}" data-title="{title}"></div>\n\n'
    if shell_anchor not in html:
        sys.exit("Could not find HISTORY VIEW anchor for app-shell insertion.")
    html = html.replace(shell_anchor, shell_html + shell_anchor, 1)

    # ---------- 4. STUDY_NOTES ----------
    notes_anchor = "\n};\n\nconst SECTION_META = {"
    if notes_anchor not in html:
        sys.exit("Could not find STUDY_NOTES closing anchor.")
    notes_block = build_notes_block(key, notes)
    idx = html.index(notes_anchor)
    html = html[:idx] + f",\n\n{notes_block}" + html[idx:]

    # ---------- 5. SECTION_META ----------
    meta_anchor = "\n};\nlet currentSection = null;"
    meta_entry = f",\n  {key}: {{ title:'{title}', desc:'{desc}' }}"
    idx = html.index(meta_anchor)
    html = html[:idx] + meta_entry + html[idx:]

    # ---------- 6. SECTION_CHAPTER ----------
    sc_pattern = re.search(r"const SECTION_CHAPTER = \{([^}]*)\};", html)
    if not sc_pattern:
        sys.exit("Could not find SECTION_CHAPTER line.")
    old = sc_pattern.group(0)
    new = old.replace("};", f", {key}:'{chapter}' }};")
    html = html.replace(old, new, 1)

    # ---------- 7. BOOTSTRAP block ----------
    boot_anchor = "  })\n  .catch(err => {"
    boot_lines = (
        f"\n    const {key}App = initQuizApp('app-{key}', data.{key}.questions, data.{key}.catColors, '{title}', '{key}');\n"
        f"    SECTION_APPS.{key} = {key}App;\n"
        f"    document.getElementById('{key}Count').textContent = data.{key}.questions.length;\n"
        f"    document.getElementById('{card_id}').addEventListener('click', ()=> openSubmenu('{key}'));\n"
    )
    if boot_anchor not in html:
        sys.exit("Could not find BOOTSTRAP closing anchor.")
    html = html.replace(boot_anchor, boot_lines + boot_anchor, 1)

    HTML_PATH.write_text(html)
    print(f"Added '{key}' ({title}) under chapter '{chapter}' \u2014 "
          f"{len(questions)} questions, {len(cat_colors)} categories.")


if __name__ == "__main__":
    main()
