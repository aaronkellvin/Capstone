# Student UX Audit — Bloom

**Date:** 2026-09-20 (decisions logged 2026-09-21)  
**Mode:** Observational audit + prioritized proposal; N1–N3 / S1–S3 decisions recorded below (S1/S2/N2/N3 code already shipped; decision-log updates are documentation only)  
**Prior art (read first; do not re-litigate):**  
`docs/TEACHER_UX_AUDIT.md` (N1 sidebar reorder + N2 Announce→pro.html = **Deferred — post-defense**), `docs/UI_GAP_ANALYSIS.md`, `docs/MOTION_DESIGN_NOTES.md`, `docs/VISUAL_HIERARCHY_NOTES.md`  

**System to extend (not replace):** `--bloom` / `--pro` / `--wic` in `bloom-pro.css`; components `.hub-card`, `.status-pill` (student), `.teacher-status-pill` (teacher only), `work_item_card`, motion `pro-stagger-in` / `pro-card-interactive` / `pro-toast-in`.

**Student task flow (from `app.py` routes → templates):**

| Route | Template |
| --- | --- |
| `/home` | `student_home.html` |
| `/subjects/<slug>` | `subject_hub.html` |
| `/subjects/<slug>/summaries/<material_slug>` | `summary_reader.html` |
| `/subjects/<subject_slug>/practice/<material_slug>` | `practice_setup.html` |
| `…/take` | `practice_take.html` |
| `/results/<id>` | `practice_result.html` |
| `/assessments/<slug>` | `assessment_lobby.html` |
| `/assessments/<slug>/take` | `assessment_take.html` |
| `/practice` | `practice_hub.html` |
| `/results` | `results.html` |
| `/announcements` | `announcements.html` |
| `/messages`, `/messages/<id>` | `messages_inbox.html`, `messages_thread.html` |
| `/profile` | `profile.html` |
| `/login` | `login.html` (auth surface) |

**Out of scope for content/logic:** Improve-loop branching, material fallback, assessment-exhausted messaging on `practice_result.html` / `results.html` — visual consistency of cards/spacing/components only if flagged; no logic findings.

---

## Design system inventory (already in place)

| Layer | Exists | Student use |
| --- | --- | --- |
| `--bloom-*` / `--pro-*` | Yes | Shell, surfaces, semantic color |
| `--wic-*` + `work_item_card` | Yes | `practice_hub.html`, `results.html` |
| `.hub-card` + `.today-action` | Yes | Subject Hub tabs, profile recent, practice_result next steps |
| `.status-pill` | Yes | Subject/practice/assessment/good/improve — **not** `.teacher-status-pill` (correct) |
| `.empty-state-card` | Yes | Home Today empty, Hub empties, Practice/Results empties, Announce, Messages |
| Motion utilities | Yes | **Wired on student Messages** (+ flash via layout). Mostly **unwired** on Home / Practice / Results / Hub lists |
| Loading | `data-loading` → qol-overlay | Practice setup/submit, assessment submit, profile, login, hub upload |

Student pages all `extends layouts/pro.html`. Sidebar: Home → Practice → Results → Announcements → Messages → Profile.

---

## Per-page findings

### `student_home.html` — already solid

Cognitive: Where / Do / Next / Progress / Attention are clear (command hero, subjects, Today, pulses).

| Finding | Tag |
| --- | --- |
| Subject cards (`.subject-card`) and Today primary (`.today-action`) are intentional, not teacher-queue clones. No forced unify. | — |
| `pro-stagger-in` / `pro-card-interactive` on `.subject-grid`, Today primary/secondary — see Decision log S1. | **Resolved** (S1) |
| Responsive: subject grid + Today already have ≤700px / ≤860px rules in `bloom-pro.css`. No markup red flag. | — |

### `subject_hub.html` — solid shell; intentional density vs global WIC

Cognitive: Hub command + path + tabs answer Where / Do / Next well. Progress is text (`progress_label`), not a meter — acceptable for hub density.

| Finding | Tag |
| --- | --- |
| Practice tab rows = `article.hub-card` + `a.today-action`; Results tab = `hub-card` + soft Review. Global Practice/Results use `work_item_card` + `.wic-btn`. **Resolved — keep split (intentional density)** — see Decision log N1. | **Resolved** (N1) |
| Assessments / practice / results queues: `pro-stagger-in` + `pro-card-interactive` (unlocked). Study list: stagger only — no interactive on multi-CTA `hub-card-stack`. See Decision log S1. | **Resolved** (S1) |
| Tab empties correctly use `.empty-state-card` + `.today-action` (e.g. practice empty → Study). Class pairing vs Practice library empty is intentional — see S3. | — |
| `active_tab = "home"` while inside a subject — sidebar says Home, which matches entry from Home; not a bug. | — |
| Dense hub-path (4 steps) + panels: CSS stacks path on narrow; watch vertical length on phone — no broken fixed widths spotted. | Note only |

### `practice_hub.html` — already solid (WIC language)

| Finding | Tag |
| --- | --- |
| WorkItemCard + filter chips + ready/locked badges — consistent with Results. | — |
| Empty: `.empty-state-card.practice-empty` + `.wic-btn.wic-btn-secondary` → **Go to Study** (`url_for('home')#subjects-title`). Class pairing with Results empty unchanged; destination fixed — see Decision log N2. | **Resolved** (N2) |
| `work-item-grid` `pro-stagger-in`; unlocked cards interactive via macro; filter freeze `is-stagger-done` — see Decision log S1. | **Resolved** (S1) |

### `practice_setup.html` — already solid

| Finding | Tag |
| --- | --- |
| Commit = `.btn-primary.practice-submit-btn` + `data-loading` — matches form-commit rule used on profile/login. | — |
| Hierarchy: lobby card focuses the generate task. Fine. | — |

### `practice_take.html` / `assessment_take.html` — already solid (shared shell)

| Finding | Tag |
| --- | --- |
| Progress bar + pills + `today-action` nav; Submit uses `.today-action` (not `.btn-primary`) inside take chrome — consistent across both take templates. Do not “fix” to btn-primary without a decision. | — |
| `data-loading` / confirm-submit on assessment — loading feedback exists. | — |
| `pro-focus` body — intentional quiet chrome. | — |
| Assessment take sets `active_tab = "none"` (no sidebar highlight); practice take keeps `practice`. Locked-in assessment mode — see Decision log N3. | **Resolved** (N3) |

### `assessment_lobby.html` — already solid

| Finding | Tag |
| --- | --- |
| Primary Start = `.btn-primary.btn-inline`; secondary Ask Teacher = soft — correct weight. | — |
| Title uses `.section-title.section-title-sm` — quieter contextual scale; see Decision log S2. | **Resolved** (S2) |
| Checklist hierarchy is clear; primary action is visually primary. | — |

### `summary_reader.html` — already solid

| Finding | Tag |
| --- | --- |
| Practice this lesson = `.btn-primary.btn-inline`; Ask Teacher soft. Matches lobby pattern. | — |

### `results.html` — already solid (logic out of scope)

| Finding | Tag |
| --- | --- |
| Story + WorkItemCard list + filters — strong Where/Do/Next/Progress. | — |
| Empty uses `.wic-btn` → Practice — consistent with Practice empty using WIC buttons. | — |
| `work-item-list` `pro-stagger-in`; unlocked cards interactive via macro — see Decision log S1. | **Resolved** (S1) |
| **Do not** audit story branching / release / exhausted content here. | — |

### `practice_result.html` — visual only; logic out of scope

| Finding | Tag |
| --- | --- |
| Review cards = `.hub-card.review-card`; next steps = `.hub-card` + `.today-action` — appropriate (not WorkItemCard). | — |
| Ask Teacher / Request attempt = `.btn-primary.btn-inline` — consistent with summary/lobby. | — |
| No motion on review list (teacher lists often stagger). Optional. | **SAFE** |
| **Do not** change Improve / exhausted / pending copy or branching. | — |

### `announcements.html` — already solid

| Finding | Tag |
| --- | --- |
| List/detail, unread, empties with `.empty-state-card` + soft actions — coherent. | — |
| Custom arrive/skeleton (not `pro-stagger-in`) — intentional async UX; not a defect vs Messages. | — |
| CSS already has ≤839px list/detail swap. Watch complexity on narrow; no fixed-width red flag in markup. | Note |

### `messages_inbox.html` / `messages_thread.html` — already solid (motion reference)

| Finding | Tag |
| --- | --- |
| `.message-row.pro-card-interactive` inside `.pro-stagger-in`; empties `.pro-toast-in` — **student-side standard for interactive lists** (same utilities as teacher motion notes). | — |
| Student search copy is correct (“Search teachers…”); teacher branch already fixed in teacher Phase 3. | — |
| Chat empty `.chat-empty` + `.empty-state-icon` — specialty surface; fine. | — |

### `profile.html` — already solid

| Finding | Tag |
| --- | --- |
| Learning stats + recent `.hub-card` + soft Review; commits `.btn-primary` + `data-loading`. | — |
| Recent activity as hub-card (not WIC) — lighter density OK for profile; consistent with N1 keep-split (hub density for secondary lists). | — |

### `login.html` — already solid enough

| Finding | Tag |
| --- | --- |
| `.btn-primary` Sign In + `data-loading`; pilot fills soft. Flash uses shared partial. | — |

---

## Cross-cutting: component duplication (named)

| Same UI problem | Instance A | Instance B | Tag |
| --- | --- | --- | --- |
| Start / open a practice item | `subject_hub.html` Practice tab: `.hub-card` + `.today-action` | `practice_hub.html`: `work_item_card` + `.wic-btn-primary` | **Resolved** (N1 — keep split) |
| Open a past result row | `subject_hub.html` Results tab: `.hub-card` + `.today-action-soft` | `results.html`: `work_item_card` (+ score meter) | **Resolved** (N1 — keep split) |
| Empty primary CTA class | Hub empties: `.today-action` | Practice/Results empties: `.wic-btn.wic-btn-secondary` | **Resolved** (S3 — context rule) |
| Interactive list entrance/affordance | `messages_inbox.html`: `.pro-stagger-in` + `.pro-card-interactive` | Home / Practice / Results / Subject Hub queues — now wired; Announcements left alone | **Resolved** (S1) |
| Form commit vs take submit | Setup/lobby/summary/profile: `.btn-primary` | Take Submit: `.today-action` | Intentional take chrome — **not** a SAFE unify |

---

## Hierarchy / intention notes (only where weight ≠ importance)

| Screen | Note | Tag |
| --- | --- | --- |
| `assessment_lobby.html` | Title scale aligned to `.section-title.section-title-sm`. | **Resolved** (S2) |
| Subject Hub Practice | Primary Start is solid `.today-action` — correct weight for the row; hub vs WIC atom split is intentional density (N1), not a buried CTA. | — |
| Home / Results / Messages | Primary actions are already the visually loudest controls. | — |

---

## Interaction states (vs teacher motion standard)

| Primary action | Loading / feedback | Affordance vs standard |
| --- | --- | --- |
| Generate practice (`practice_setup`) | `data-loading` → overlay | Good |
| Submit practice/assessment | `data-loading` (+ assess confirm) | Good |
| Start assessment (lobby) | form POST; overlay if wired globally | Good |
| Open message row | CSS `pro-card-interactive` hover/focus | **Reference** |
| Open subject / practice / result cards | `pro-card-interactive` (+ list stagger) where wired in S1 | **Resolved** (S1) |
| Announcement select | Custom JS selection (not pro-card-interactive) | Leave — different interaction model |

---

## Responsive (CSS/markup only)

| Area | Observation |
| --- | --- |
| Pro shell ≤860px | Sidebar off-canvas — established |
| Home / WIC / results | Stack rules exist in `bloom-pro.css` |
| Announce ≤839px | List/detail mode switch — complex but intentional |
| Subject hub path | Multi-step; stacks on narrow — possible long scroll, not overflow breakage |
| No student template found with obvious `width: NNpx` fixed content columns without media fallback in this pass | — |

No definite “will break” markup smoking gun; subject hub length + announce split remain **watch** items for a later mobile pass (teacher audit already treats full mobile as bigger track — do not re-open as new IA).

---

## Already-solid vs closed polish

**Already solid (dedicated redesigns held up):**  
`student_home`, `practice_hub`, `practice_setup`, take shells, `summary_reader`, `results` (presentation), `announcements`, `messages_*`, `profile`, login.

**Intentional (not a defect — Decision log):**  
Hub vs WorkItemCard density split (N1); empty CTA class pairing by context (S3); Announcements custom selection (no `pro-card-interactive`).

**Closed SAFE (code shipped):**  
S1 motion affordance parity; S2 assessment lobby title scale.

---

## Prioritized summary

### SAFE — quick / high value

| ID | Item | Status |
| --- | --- | --- |
| S1 | Opt-in `pro-card-interactive` (+ parent `pro-stagger-in` where lists enter) on clickable student list surfaces — matching Messages / MOTION notes | **Resolved & implemented** (2026-09-21) |
| S2 | Align `assessment_lobby.html` title class to quieter existing pattern (`.section-title.section-title-sm`) | **Resolved & implemented** (2026-09-21) |
| S3 | Empty CTA class rule by context (hub/today → `.today-action`; WIC library → `.wic-btn`) — document only; no markup unify | **Resolved — documented** (2026-09-21); see Decision log |

### NEEDS DECISION

| ID | Item | Status |
| --- | --- | --- |
| N1 | Subject Hub vs global Practice/Results list atom (hub-card vs WorkItemCard) | **Resolved — keep split (intentional density)** (2026-09-21) |
| N2 | Practice hub empty CTA destination | **Resolved & implemented** (2026-09-21) |
| N3 | Assessment take `active_tab` highlighting | **Resolved & implemented** (2026-09-21) |

### Explicitly not re-opened here

- Teacher sidebar reorder / Announce shell migration — already **Deferred** in `TEACHER_UX_AUDIT.md`. Student Announce is already on `pro.html`; no parallel finding.  
- Improve-loop logic / exhausted / material fallback — out of scope.  
- New tokens, gradients, glass, or competing design language — rejected.

---

## Decision log — Gate

**Decisions recorded 2026-09-21:** N1 (keep split), N2 (Practice empty → Study entry), N3 (assessment-take no nav highlight), S1 (motion parity), S2 (lobby title scale), S3 (empty CTA class rule).  
**Code already shipped for S1, S2, N2, N3;** later gate entries for S1/S2 are documentation only. **No code** toward unifying hub → WIC (N1 rejected unify path).  
**Student audit SAFE + N\* set fully closed** (S1–S3, N1–N3).

### N1 — Resolved — keep split (intentional density)

**Not** unifying Subject Hub Practice/Results onto `work_item_card`. The two atoms stay because **context and scan density differ**, not because the pages drifted by accident.

| Context | Atom | Why |
| --- | --- | --- |
| In-subject list rows (Subject Hub Practice / Results tabs) | `.hub-card` + `.today-action` (soft for Review) | Dense scan list: many items in one subject; student is already inside a subject flow |
| Global Practice / Results library | `work_item_card` + `.wic-btn` | Page primary focus is the library (single item or smaller curated set), not a dense in-subject scan |

Both share `--bloom` / `--pro` / `--wic` tokens where applicable; do not invent a third card system. Profile recent activity staying on `.hub-card` is consistent with this density rule.

### N2 — Resolved & implemented

**Shipped:** `practice_hub.html` empty-state CTA changed from Announcements (`url_for('announcements')` / “Check announcements”) to **Go to Study** → `url_for('home')#subjects-title`. Class pairing unchanged (`.empty-state-card.practice-empty` + `.wic-btn.wic-btn-secondary`). Label wording matches Subject Hub’s practice-tab empty CTA (“Go to Study”).

**Rejected alternative:** a literal `url_for('subject_hub', slug=…, tab='study')` deep link. `practice_hub.html` has **no subject in context**; defaulting to an arbitrary slug (e.g. always English) would be a fake affordance — inconsistent with this project’s no-fake-data / no-fake-affordance principle. The honest global entry (Home subjects → then Study) was used instead.

**Future log (follow-up only, no schema now):** Possible future enhancement: route to last-opened subject’s Study tab directly, once a “last opened subject” value is tracked — no schema change made now, logged as follow-up only. Same posture as Gap 1 `material_id` / nearest-material TODO.

### N3 — Resolved & implemented

**Shipped:** `assessment_take.html` sets `active_tab = "none"` (sentinel matching no nav key), so **no** sidebar item is highlighted while the student is in the locked-in assessment-taking flow. Highlighting Home or Practice would imply normal browsing is available mid-assessment, which is inaccurate given attempt limits and task mode.

**Why Option C worked:** `partials/pro_sidebar.html` already supports a truthy non-matching `active_tab` (no `.is-active` applied). CSS does not assume an active item always exists. No fallback to subject/Practice highlight was needed.

**Scope:** `assessment_take.html` only. Lobby / results / review / practice-take `active_tab` behavior unchanged.

### S1 — Resolved & implemented

**Shipped:** `pro-card-interactive` + `pro-stagger-in` wired for student motion parity with Messages / teacher Materials–Monitor patterns. Existing `bloom-pro.css` utilities only — **no new animation rules**. `prefers-reduced-motion` coverage was already built into those utilities and inherited; not re-implemented.

| Surface | What shipped |
| --- | --- |
| Home | `.subject-grid` stagger + interactive subject links; Today primary/secondary cards interactive; secondary list stagger |
| Practice / Results | Parent stagger on `work-item-grid` / `work-item-list`; unlocked `work_item_card` gets `pro-card-interactive` via the existing macro |
| Subject Hub | Assessments / practice / results queues staggered like Teacher Home (interactive on unlocked queue cards); Study list stagger only — **no** interactive lift on multi-CTA `hub-card-stack`, per `docs/MOTION_DESIGN_NOTES.md` (multi-action cards must not imply a single whole-card hit target) |
| Practice filter | `is-stagger-done` freeze in `practice_hub.js` after first entrance — same pattern as Messages, so subject-filter show/hide does not replay stagger |

**Explicitly left untouched:** `announcements.html` — custom JS selection logic, not a simple clickable-row list. Consistent with leaving specialized JS interaction models alone during the teacher-side motion pass (and with Messages filter/JS ownership of stagger freeze rather than inventing a second announce motion system).

### S2 — Resolved & implemented

**Shipped:** `assessment_lobby.html` title class changed from `.section-title` to `.section-title.section-title-sm`, matching the quieter contextual/secondary heading scale used elsewhere in the pro shell (Practice library, Results history, Materials section heads, etc.).

### S3 — Resolved — documented (empty CTA class rule)

Same density/context reasoning as N1 — not a new invention; records what the audit already observed working correctly.

| Context | Empty primary CTA | Examples |
| --- | --- | --- |
| Hub / Today / in-subject empties | `.empty-state-card` + `.today-action` (soft secondary where needed) | Subject Hub tab empties |
| WIC library empties | `.empty-state-card` + `.wic-btn.wic-btn-secondary` | `practice_hub.html`, `results.html` |

**Rule:** only change markup if a single empty state **mixes** both button systems. Do not force one class everywhere.

---

*End of audit. N1 / N2 / N3 / S1 / S2 / S3 closed in the Decision log. Student SAFE + N\* set complete.*
