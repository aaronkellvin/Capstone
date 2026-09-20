# Visual Hierarchy Notes — Bloom Teacher Shell

**Audience:** teammates learning *why* Bloom’s teacher UI looks the way it does  
**Grounded in:** `static/css/bloom-pro.css` tokens; `templates/teacher_home.html`, `teacher_monitor.html`, `teacher_hots.html`, `teacher_materials.html`  
**Mode:** design rationale only — not a style guide of every class

---

## 1. What “one coherent design system” means here

Bloom does not invent a new palette per page. In `bloom-pro.css`, three token layers share one identity:

| Layer | Prefix | Role |
| --- | --- | --- |
| Semantic brand | `--bloom-*` | Product meaning: primary, success, warning, error, text, surface |
| Shell / chrome | `--pro-*` | Sidebar, cards, shadows, links, soft state fills, motion timing |
| Work item geometry | `--wic-*` | Shared Practice/Results card geometry (accent width, radius) — pages must not override |

Examples that matter day to day:

- Primary actions use `--pro-blue` / `--bloom-primary` (`#2a57d5`), not a one-off hex in a template.
- Success / caution / danger soft fills are `--pro-green-soft`, `--pro-orange-soft`, `--pro-red-soft`.
- Motion is shared: `--pro-ease-standard`, `--pro-duration-fast|base|slow` (150 / 220 / 320ms).
- Legacy pages still resolve through bridges (`--ink` → `--pro-ink`, `--line` → `--pro-line`) so old markup and new pro pages feel like one product.

**Why this matters for users, not only developers**

A teacher jumping Home → Materials → HOTS → Monitor should not relearn “what green means” or “how urgent a card feels.” Shared tokens encode meaning: blue is the thing you *do*, green is *live / good*, orange is *needs attention*, gray is *quiet / closed*, red is *rejected / low*. When every page pulls from the same `--pro-*` / `--bloom-*` vocabulary, the product’s mental model stays stable. Local one-off colors break that model even if the feature still works.

Developer convenience (DRY CSS) is a side effect. The product goal is recognizability across the teacher workspace.

---

## 2. Case study: status-pill unification

Monitor introduced a reusable status language in `bloom-pro.css`:

- `.teacher-status-pill.is-draft` → orange soft / warning  
- `.teacher-status-pill.is-published` → green soft / success  
- `.teacher-status-pill.is-closed` → muted gray  

Materials and HOTS used to show status as plain `.hub-card-kicker` text (or section context only). That meant “Draft” on HOTS and “Pending” on Materials did not share shape, weight, or color with Monitor’s published/closed chips.

**What we did**

- HOTS set status: `.teacher-status-pill.is-{{ assessment.status }}` for `draft` / `published` / `closed` (same classes as Monitor).
- Materials: aliases that **reuse the same token recipes**, not new colors:
  - `.is-pending` → same as draft (orange)
  - `.is-approved` → same as published (green)
  - `.is-rejected` → same as score-low red (`--pro-red-soft` / `--bloom-error`)
- Non-status text (source, owner, bloom · qtype · citation) stays plain meta beside the pill.

**Why users benefit**

Status is a *glance* channel. If “needs attention” is always the same pill shape and orange fill, the eye learns it once. Inventing a unique badge per page forces re-parsing on every screen — cognitive tax with no information gain. Unifying pills is how Bloom turns three workflows (approve material, publish HOTS, release Monitor) into one visual dialect.

---

## 3. Information hierarchy on Teacher Home

`teacher_home.html` (extends `layouts/pro.html`) is ordered on purpose:

### First: command hero (`page_header` / `.home-command-hero`)

- Eyebrow: “Your day”
- Title: personalized greeting (`Hi, {name}`)
- One supporting sentence (`guide_note`)
- Pulse chips: class avg (or honest “No scores yet”) and unread chats when present

**Why first:** Orient the person and the subject before asking for work. One key signal (class pulse) answers “how is my section doing?” without dumping a dashboard. Cognitive load stays low: identity + one honest metric.

### Second: “Do this next” / Open items queue

- Eyebrow + `section-title-sm` “Open items”
- Count badge for pending count
- Vertical `.hub-list` of `.hub-card` rows (messages / pending materials / draft HOTS), each with a soft CTA — or a compact empty row (“Nothing pending right now”)

**Why second:** After orientation, the next scarce resource is *attention*. The queue is inventory, not celebration — multiple open items at once, scannable, each with one action. This is the primary work surface for the visit.

### Third: “At a glance” workspace stats

- Four `.teacher-stat-card`s (approved materials, draft HOTS, pending uploads, published assessments)

**Why third:** Supporting context and navigation shortcuts. Useful after the queue is clear, or when the teacher wants a map of the workspace — not the first thing to parse when something is on fire.

**Ordering rule in one line:** *Who am I / how’s the class → what needs me → what’s in the inventory.* Reversing that (stats before queue, or a hero full of widgets) raises cognitive load: teachers must filter noise before finding the next action.

Monitor mirrors the same shell pattern (hero + pulse chips, then section eyebrows + scannable cards). HOTS uses the shared pro header blocks (`page_kicker` / `page_title` / `page_subtitle`) then Create → Your sets — same eyebrow + `section-title-sm` rhythm as Home’s content sections.

---

## 4. Cards vs dense forms/tables

### Dense form / table layouts

Legacy staff pages leaned on long forms and tabular density: many fields visible at once, rows competing for equal weight. Fine for data entry; poor for *triage* (who needs me, what’s live, what to release).

### Card / scannable layouts (where Bloom moved)

Teacher pages now prefer bounded cards inside the pro shell:

| Page | Card unit | Job |
| --- | --- | --- |
| Home | `.hub-card` queue rows + `.teacher-stat-card` | Prioritized actions, then inventory |
| Monitor | `.teacher-student-card`, `.teacher-monitor-card` | One student or one assessment as a readable chunk + release actions |
| HOTS | `.lobby-card` per set, nested `.hub-card` per question | Generate form stays a form; review stays a list of discrete items |
| Materials | `.hub-card` lists with status pills | Pending / approved / rejected as scan units |

**Why cards for teachers**

- One unit = one decision (approve, publish, release, message).
- Status pills and soft CTAs sit in a predictable place on the unit.
- Motion utilities (`.pro-stagger-in`, `.pro-card-interactive`) apply cleanly to card lists without animating every table cell.
- Forms remain forms where input is required (HOTS generate, Materials upload) — Bloom did not pretend a multi-field form was a “card”; it nested forms *inside* the shell’s hierarchy instead of making the whole page a spreadsheet.

---

## Takeaway for future UI work

1. Prefer existing `--bloom` / `--pro` / `--wic` tokens over page-local hex.  
2. Prefer extending shared components (e.g. `.teacher-status-pill`) over new status chrome.  
3. Prefer Home’s order: orient → act → inventory.  
4. Prefer scannable cards for triage; keep dense forms only where the user is composing or configuring.

If a new teacher screen feels “off,” check whether it broke one of these four before adding more UI.
