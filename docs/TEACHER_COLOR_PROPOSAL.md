# Teacher Color Proposal — Bloom

**Date:** 2026-09-21  
**Mode:** Audit + proposal only — **no CSS/template implementation in this pass**  
**Primary target:** `templates/teacher_home.html` (+ related rules in `static/css/bloom-pro.css`)  
**Prior art:** `docs/TEACHER_UX_AUDIT.md`, `docs/STUDENT_UX_AUDIT.md`, `docs/VISUAL_HIERARCHY_NOTES.md`, `docs/MOTION_DESIGN_NOTES.md`  
**Constraint:** Extend the **existing** student subject-color system. Do not invent a parallel palette. No fake metrics or fake urgency.

---

## 1. How student subject color works today (reuse this exactly)

### Tokens (already in `bloom-pro.css` `:root`)

| Token | Role |
| --- | --- |
| `--subject-english` / `--subject-english-soft` | Saturated + soft fill |
| `--subject-math` / `--subject-math-soft` | Used by slug `mathematics` |
| `--subject-science` / `--subject-science-soft` | Saturated + soft fill |
| `--subject-general` / `--subject-general-soft` | Fallback |
| (+ filipino / values pairs exist; Grade 7 pilot uses english / mathematics / science) | |

### Class → variable mapping

Two parallel class families set the same CSS variables:

| Class pattern | Sets | Typical use |
| --- | --- | --- |
| `.subject-{slug}` (e.g. `.subject-science`) | `--subject-color`, `--subject-soft` | Subject cards, Today cards, hub-command, pills |
| `.subject-accent-{slug}` | `--subject-color`, `--subject-soft`, **and** `--subject-accent` | Body/shell wrappers, WorkItemCard left accent, chat |

Slug source: `SUBJECTS` keys in `app.py` (`english`, `mathematics`, `science`). Teachers resolve via `teacher_subject_slug(user)` → passed as `subject_slug` into templates. Topbar already shows `Teacher · {subject_name}`.

### Where students *spend* that color (the personality gap)

| Surface | Mechanism | Visual effect |
| --- | --- | --- |
| Home subject cards | `a.subject-card.subject-{slug}` | Colored avatar circle, matching pill, matching meter fill, left border |
| Home Today featured | `.today-featured` + `.subject-{slug}` on the card | Soft radial + linear gradient from `--subject-soft`; stronger left border from `--subject-color` |
| Home Today secondary | Same `--subject-color` left border on `.today-card` | Quieter accent strip |
| Due-soon / assessment type | `.today-assessment` left border → `--letran-red` / error family | Urgency accent **by type**, not by subject |
| Subject Hub command | `.hub-command.subject-{slug}` | Left border + soft gradient — strongest “you are in Science” signal |

**Important:** Student Home’s command **hero** (`.home-command-hero`) is still a **generic** blue soft radial (`--pro-blue-soft`), not subject-tinted. Student personality on Home comes mainly from the **subject grid + tinted Today featured**, not from the hero itself.

### Teacher Home already half-wires the system

```3:3:templates/teacher_home.html
{% block body_class %}home-command teacher-home-command subject-accent-{{ subject_slug }}{% endblock %}
```

So `--subject-color` / `--subject-soft` / `--subject-accent` are **already available** on `.pro-body.teacher-home-command`. Almost nothing on the page consumes them. The gap is **underuse**, not missing infrastructure.

**Soft fills already exist** (`--subject-*-soft`). A teacher-side tinted background can reuse those + existing `color-mix(...)` patterns from `.hub-command` / `.today-featured`. **No new color tokens required** for Options A–C below unless an option explicitly asks for one (none do).

---

## 2. Teacher Home — what is currently colorless

| Element | Current treatment | Why it feels inert vs student Home |
| --- | --- | --- |
| `.home-command-hero` | White/`--bloom-surface` + generic `--pro-blue-soft` radial; gray border | Same shell as student hero, but teacher has **no** subject-card grid below it to supply color |
| Open items queue (populated) | Plain `.hub-card` (white, soft CTA) | No subject left border / soft fill; kickers are category text only |
| Open items (empty) | Single compact `.hub-card` + soft CTA | Lower presence than student `today-empty today-featured` |
| `.teacher-stat-card` | White card; **only** `.teacher-stat-icon` uses `tone-blue|amber|gray|green` soft fills | Semantic icon chips only — no border/background accent; tones are **workflow** colors, not subject |
| “At a glance” section chrome | Neutral eyebrow + muted subject name badge | Subject name is text only |

Stat tones (`tone-blue` etc.) are intentional **meaning** colors from the teacher shell (Materials / caution / quiet / published) — see `VISUAL_HIERARCHY_NOTES.md`. Any proposal should not erase that semantics unless we deliberately replace it with subject color.

---

## 3. Empty-space diagnosis (actual cause)

**Not** unused grid cells in the stat row. `.teacher-stat-grid` is `repeat(4, minmax(0, 1fr))` — when Open items is empty, all four stat cards still render and fill the row.

**Actual cause — vertical composition / missing mass:**

1. **Student Home** puts a dense, colored **subject grid** in `page_header` under the hero. Even when Today is empty, the first viewport still has three tinted cards.
2. **Teacher Home** `page_header` is **hero only**. Content = Open items + stats.
3. When `attention` is empty, Open items collapses to **one short** plain `hub-card` (not a featured/empty-state block with icon). That section is visually thin.
4. Stats sit below as a single short row. Below that, the remaining `pro-content` / page canvas is empty white — reads as “unfinished trail,” especially on tall viewports.

So the fix is **give the empty queue (and/or the first content region) more intentional presence**, not invent queue items and not stretch the 4-col grid with phantom cells.

Student empty Today already models a higher-presence empty: `empty-state-card today-empty today-featured` with padding + soft treatment. Teacher empty still uses the thin queue `hub-card`.

---

## 4. Options for `teacher_home.html` (choose one)

All options reuse existing `--subject-*` / `--subject-*-soft` / `subject-accent-*` (already on the body). Implementation would be primarily CSS under `.teacher-home-command`, plus small empty-state markup if choosing the empty upgrade. **Do not implement until an option is approved.**

### Option A — Subject-tint the hero + upgrade empty presence (recommended default)

**Color**

- **Hero (`.home-command-hero`):** Switch the hard-coded `--pro-blue-soft` radial to `--subject-soft`, and add a left border using `--subject-color` — same recipe as `.hub-command` / student Today featured. Teacher’s single-subject context makes this the right place for “you are in Science.”
- **Stat cards:** Keep existing `tone-*` **icon** semantics. Optionally add a thin left or top accent using each card’s **existing tone soft fill** (already defined for icons) so the accent is “upgraded from badge-only,” not a new palette. Do **not** paint all four cards with subject green/purple — that would flatten Materials vs Draft vs Pending meaning.
- **Open items (populated):** Optional light left border on queue `.hub-card` via `--subject-accent` (already on body) for quiet continuity — low priority within this option.

**Empty space**

- Replace the thin empty `hub-card` with a higher-presence empty patterned after student Today empty / Practice empty: `.empty-state-card` (or keep `hub-card` but add icon + `today-featured`-like subject-soft background using existing soft tokens).
- Keep the real CTA already in context: “Upload a new lesson” → Materials. No fake pending counts.
- Optional (same option, still SAFE-ish): when queue is empty, slightly increase empty-card min-height / padding so Open items + stats read as one finished block rather than a stub over white.

**Why this option:** Matches how Subject Hub signals subject (command chrome), fixes the biggest “inert hero” gap, and addresses empty trail without fake data. Minimal risk to stat semantics.

**Token adds:** None.

---

### Option B — Subject accent on stats row; hero stays quiet

**Color**

- **Hero:** Leave generic blue-soft (parity with student command hero as-is), or only a very light `--subject-soft` wash without a strong left bar.
- **Stat cards:** Each card gets a **top border** (or left border) in `--subject-color` / soft mix — one subject accent shared across the four cards, while **keeping** tone-* icon colors for workflow meaning. The “At a glance” count-badge that already shows `subject_name` becomes redundant with color, which is fine.
- **Open items:** Unchanged visually for color (or same quiet subject left border as A).

**Empty space**

- Same empty-state presence upgrade as Option A (icon + soft subject wash + existing Upload CTA).

**Why this option:** Puts color where the teacher spends time scanning inventory; keeps greeting chrome calm. Risk: four identical subject top-borders can look decorative if icons already carry meaning — subject accent may feel redundant next to “Science” in the badge.

**Token adds:** None.

---

### Option C — Featured “caught up” panel + subject hero (strongest empty-state redesign)

**Color**

- **Hero:** Same subject-tint as Option A (soft + left border).
- **Stats:** Keep tone-* icons; add subject soft wash only to the **stat section heading row** (eyebrow / badge), not every card — avoids competing accents.
- **Open items when populated:** First/primary queue item may optionally use a Today-featured-like subject soft panel (teacher already has `priority` on attention items) — **NEEDS DECISION** if that changes hierarchy of Messages vs Materials vs HOTS.

**Empty space**

- When empty, render a **featured empty panel** (subject-soft background, larger icon, clear title/note, primary soft CTA to Materials) and optionally a **second** soft suggestion that reuses real destinations already in the product (e.g. “Open Monitor” / “Generate HOTS”) — only links that already exist, still no fake counts.
- Layout note (explicit NEEDS DECISION if chosen): consider moving “At a glance” into `page_header` beside/under hero when the queue is empty so the first viewport never collapses to hero + stub. That is a **structure** change, not a paint change.

**Why this option:** Best answer to “unfinished white trail,” closest to student Home’s always-full first region. Cost: more markup / possible IA tweak; easier to over-design if the second suggestion feels like clutter.

**Token adds:** None for color. Layout move is the decision risk, not tokens.

---

## 5. Comparison (quick)

| | Option A | Option B | Option C |
| --- | --- | --- | --- |
| Hero subject tint | Yes (main move) | Mild / none | Yes |
| Stats | Tone icons kept; optional tone border upgrade | Shared subject top/left accent | Tone icons; subject on section chrome only |
| Empty trail | Higher-presence empty card | Same | Featured empty + optional second real CTA / layout move |
| Fake data risk | None | None | None if second CTA is real routes only |
| Decision weight | Lowest | Medium (redundant subject on all stats?) | Highest (structure) |

---

## 6. Follow-up pages (note only — no proposals this pass)

| Page | Same gap? |
| --- | --- |
| `teacher_materials.html` | **Yes, milder.** Body already has `subject-accent-{{ subject_slug }}`; default pro hero + white list cards don’t consume subject soft/color. Status pills carry workflow color instead. |
| `teacher_hots.html` | **Yes, milder.** Same body accent; generate `lobby-card` / lists stay neutral aside from status pills. |
| `teacher_monitor.html` | **Yes, similar to Home.** Uses `.home-command-hero` with the same generic blue-soft radial despite `subject-accent-*` on body — strongest follow-up candidate after Home’s approach is chosen. |

Apply whatever option wins on Home first; then reuse the same hero/empty recipes on Monitor (and only later Materials/HOTS) so teacher pages stay one system.

---

## 7. Out of scope / do not do in implementation later without a new decision

- New hex colors or a “teacher-only” palette  
- Recoloring all teacher pages in one shot  
- Fake pending items to fill space  
- Replacing `tone-*` workflow meaning with subject color on every stat without an explicit choice  
- Re-litigating deferred Teacher UX N1/N2 (sidebar / Announce shell)

---

*End of proposal. Stop for review — implement only after an option (A / B / C) is explicitly approved.*
