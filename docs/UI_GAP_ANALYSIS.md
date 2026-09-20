# UI Gap Analysis — Teacher-Facing Templates

**Date:** 2026-09-20 (motion verification re-pass)  
**Mode:** Observational inventory only — no fixes, no recommendations  
**Document action:** Overwrote previous version (same tables + motion rows updated to current; typography / card / pill tables left as originally recorded unless unchanged by inspection)  
**Compared against:** `templates/teacher_home.html` as the primary typography / hierarchy reference for the teacher pro shell  

**Templates reviewed**

| File | Shell |
| --- | --- |
| `templates/teacher_home.html` | `layouts/pro.html` (custom command hero) |
| `templates/teacher_materials.html` | `layouts/pro.html` (default `pro-hero` via page blocks) |
| `templates/teacher_hots.html` | `layouts/pro.html` (default `pro-hero` via page blocks) |
| `templates/teacher_monitor.html` | `layouts/pro.html` (custom command hero, same pattern as Home) |
| `templates/messages_inbox.html` | `layouts/pro.html` (default `pro-hero`; shared student/teacher) |
| `templates/messages_thread.html` | `layouts/pro.html` (`page_header` empty; focus chat layout) |
| `templates/staff_page.html` | Legacy staff shell (`staff_topbar` + `app-body staff-body`); Announce + admin |
| `templates/partials/flash.html` | Shared partial (included by `layouts/pro.html` + `login.html`) |
| `templates/login.html` | Standalone login shell (includes flash partial directly) |

**Heading scale reference (from CSS)**

| Class | Approx. scale |
| --- | --- |
| `.pro-hero-title` | `clamp(1.5rem, 2.4vw, 2rem)`, Fredoka 700 (`bloom-pro.css`) |
| `.section-title` (full) | `clamp(1.8rem, 5vw, 2.2rem)`, Fredoka 700 (`style.css`) |
| `.section-title.section-title-sm` | `clamp(1.35rem, 4vw, 1.6rem)` |

---

## `teacher_home.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1: `.pro-hero-title` (greeting). Section H2s: `.section-title.section-title-sm` (“Open items”, “At a glance”). Reference baseline for other pro teacher pages. |
| **Card / list unit** | Queue: `.hub-card` (+ empty `.hub-card`). Stats: `.teacher-stat-card` in `.teacher-stat-grid`. |
| **Color / status** | No `.teacher-status-pill`. Queue uses plain `.hub-card-kicker` for category labels (Messages / Materials / HOTS), not workflow status. |
| **Motion** | Queue: `pro-stagger-in` on `.hub-list`; `pro-card-interactive` on pending `.hub-card`s. Empty queue card: `pro-toast-in` (no interactive). Stats: no motion utilities. Shared flashes: via `layouts/pro.html` → `partials/flash.html` (`pro-toast-in` on each `li.flash`). |

---

## `teacher_materials.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1 via default pro hero: `.pro-hero-title` from `{% block page_title %}` (“Review before class”) — same class/scale as Home hero title. Section H2s: `.section-title.section-title-sm` (aligned with Home section headers). |
| **Card / list unit** | Primary actionable lists: `.hub-card` inside `.hub-list` (pending / deployed / rejected). Empty pending: `.hub-card`. Upload form is a bare form under a section heading (not a list card). |
| **Color / status** | Uses `.teacher-status-pill` (`.is-pending`, `.is-approved`, `.is-rejected`) with attribution in `.hub-card-meta`. No plain status kickers for material status. |
| **Motion** | `pro-stagger-in` on pending / deployed / rejected `.hub-list`s; `pro-card-interactive` on list `.hub-card`s. Empty pending `.hub-card`: `pro-toast-in`. |

---

## `teacher_hots.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1 via default pro hero: `.pro-hero-title` (“HOTS Generator”) — same class as Home. Section H2s: `.section-title.section-title-sm`. |
| **Card / list unit** | Generate block + each assessment set: `section.lobby-card`. Questions: `.hub-card.hub-card-stack` inside `.hub-list.stack-sm`. Empty: `article.empty-state-card`. |
| **Color / status** | Set-level: `.teacher-status-pill.is-{{ assessment.status }}` (draft / published / closed). Question meta: plain `.hub-card-kicker` (bloom · qtype · citation) — not status. |
| **Motion** | `pro-stagger-in` on question `.hub-list`; `pro-toast-in` on empty `.empty-state-card`. Question `.hub-card`s: no `pro-card-interactive` (intentional — action-only cards; Regenerate button handles interaction). `.lobby-card` sets: no interactive. |

---

## `teacher_monitor.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1: `.pro-hero-title` in custom `.home-command-hero` (same pattern/class as Home). Section H2s: `.section-title.section-title-sm`. |
| **Card / list unit** | Roster: `.teacher-student-card` in `.teacher-student-grid`. Assessments: `.teacher-monitor-card` in `.teacher-monitor-list`. Empties: `.hub-card`. |
| **Color / status** | Assessment cards: `.teacher-status-pill.is-{{ panel.status }}`. Also `.teacher-release-pill`, `.teacher-score-chip` (Monitor-specific). |
| **Motion** | `pro-stagger-in` on `.teacher-student-grid` and `.teacher-monitor-list`; `pro-card-interactive` on student + assessment cards; `pro-toast-in` on pulse chips and empty roster / assessments `.hub-card`s. |

---

## `messages_inbox.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1 via default pro hero: `.pro-hero-title` (“Messages”). Content H2: `.section-title.section-title-sm` (“Student conversations” / “Your teachers”). |
| **Card / list unit** | Primary list: `a.message-row` inside `.hub-list.message-list` (not `.hub-card`). Empties: `.empty-state-card`. |
| **Color / status** | No `.teacher-status-pill`. Unread via `.is-unread` + `.message-unread-dot`. Subject via `.status-pill.status-subject`. |
| **Motion** | `pro-stagger-in` on `.message-list`; `pro-card-interactive` on `.message-row`; `pro-toast-in` on empty states. |

---

## `messages_thread.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | No `.pro-hero-title` / `.section-title` page header (`{% block page_header %}{% endblock %}`). Thread title: `h1.chat-name` (chat-specific scale, not Home hero). |
| **Card / list unit** | Not a list-of-work-items page. Units: `article.chat-bubble` (`.is-mine` / `.is-theirs`); empty: `#chat-empty.chat-empty`. |
| **Color / status** | No `.teacher-status-pill`. Delivery via `.chat-stamp` text (Sent / Read). Subject pill on header person row. |
| **Motion** | `pro-stagger-in` on `#chat-thread`; `pro-toast-in` on `#chat-empty` and `#chat-status`. No `pro-card-interactive` on bubbles. |

---

## `staff_page.html` (Announce + admin)

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1: `.section-title` **without** `.section-title-sm` — full legacy scale (`clamp(1.8rem–2.2rem)`), **larger than** Home’s `.pro-hero-title` and **larger than** Home’s section `.section-title-sm`. Not on `pro.html` hero pattern. |
| **Card / list unit** | Panels: `.hub-card.hub-card-stack` in `.hub-list`. Forms: `section.lobby-card`. Same structural family as Materials/HOTS list+form, different shell. |
| **Color / status** | No `.teacher-status-pill`. Panel status-like info (if any) is plain `.hub-card-kicker` text from route-supplied `panel.kicker`. |
| **Motion** | `pro-stagger-in` on `.hub-list`; `pro-card-interactive` on panel `.hub-card`s; `pro-toast-in` on **inline** flash `li.flash` (does **not** use `partials/flash.html`). `.lobby-card` forms: no interactive. |

---

## `partials/flash.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | N/A (message copy only). |
| **Card / list unit** | `ul.flash-list.home-flash` → `li.flash.flash-{category}` with `.flash-text` + `.flash-dismiss`. |
| **Color / status** | Category via `flash-{{ category }}` + `data-flash-category`. |
| **Motion** | `pro-toast-in` on each `li.flash`. No `pro-toast-out`. |
| **Include path** | `{% include "partials/flash.html" %}` in `layouts/pro.html` (line 27) and `login.html` (line 23). |

**Inheritance spot-check**

| Consumer | Extends / include | Flash animation present in rendered tree? |
| --- | --- | --- |
| `teacher_home.html` | `{% extends "layouts/pro.html" %}` → layout includes flash partial | Yes — layout include; partial markup carries `pro-toast-in` |
| `student_home.html` | `{% extends "layouts/pro.html" %}` → layout includes flash partial | Yes — same include path as teacher Home |
| `profile.html` | `{% extends "layouts/pro.html" %}` | Yes — same |
| `login.html` | Direct `{% include "partials/flash.html" %}` | Yes — direct include of same partial |
| `staff_page.html` | Inline flashes only | N/A for this partial (already has its own `pro-toast-in`) |

---

## `login.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Brand: `.pro-login-title`; form heading: `.section-title.section-title-sm.pro-login-heading`. Not teacher pro-hero pattern. |
| **Card / list unit** | `.pro-login-card` shell; no work-item list. |
| **Color / status** | N/A for teacher-status-pill. |
| **Motion** | No page-local stagger / interactive. Flashes: via shared `partials/flash.html` → `pro-toast-in` on each flash item. |

---

## Cross-page snapshot

### Typography vs Home

| Template | Page title class | Matches Home `.pro-hero-title`? | Section headers match Home `.section-title-sm`? |
| --- | --- | --- | --- |
| teacher_home | `.pro-hero-title` | Reference | Yes |
| teacher_materials | `.pro-hero-title` (default pro hero) | Yes (same class) | Yes |
| teacher_hots | `.pro-hero-title` (default pro hero) | Yes | Yes |
| teacher_monitor | `.pro-hero-title` (command hero) | Yes | Yes |
| messages_inbox | `.pro-hero-title` (default pro hero) | Yes | Yes |
| messages_thread | `.chat-name` only | No (different component) | N/A (no section-title-sm blocks) |
| staff_page | `h1.section-title` (full) | No — larger legacy scale | No equivalent sm section pattern |

### Primary actionable-list components (same job, different classes)

| Template | Primary list unit class(es) |
| --- | --- |
| teacher_home | `.hub-card` (+ `.teacher-stat-card` for stats) |
| teacher_materials | `.hub-card` |
| teacher_hots | `.lobby-card` (sets) + `.hub-card` (questions) |
| teacher_monitor | `.teacher-student-card` + `.teacher-monitor-card` |
| messages_inbox | `.message-row` |
| messages_thread | `.chat-bubble` |
| staff_page | `.hub-card` (+ `.lobby-card` for forms) |

### `.teacher-status-pill` usage

| Template | Uses `.teacher-status-pill`? |
| --- | --- |
| teacher_home | No |
| teacher_materials | Yes (pending / approved / rejected) |
| teacher_hots | Yes (set draft / published / closed) |
| teacher_monitor | Yes (plus release/score chips) |
| messages_inbox | No |
| messages_thread | No |
| staff_page | No (kickers only) |

### Motion utility wiring (verified)

| Template | `pro-stagger-in` | `pro-card-interactive` | `pro-toast-in` |
| --- | --- | --- | --- |
| teacher_home | Yes (queue) | Yes (pending cards) | Yes (empty queue); Yes via shared flash partial |
| teacher_materials | Yes (all three lists) | Yes (list cards) | Yes (empty pending card) |
| teacher_hots | Yes (question lists) | No — intentional (action-only cards, Regenerate button handles interaction, not the whole card) | Yes (empty state) |
| teacher_monitor | Yes (roster + assessments) | Yes (student + monitor cards) | Yes (pulse chips + empty hub-cards) |
| messages_inbox | Yes | Yes | Yes (empties) |
| messages_thread | Yes (thread) | No | Yes (empty + status) |
| staff_page | Yes | Yes (panels) | Yes (inline flashes) |
| partials/flash.html | N/A | N/A | Yes (`li.flash`) |
| login.html | No | No | Yes (via flash partial) |

### Materials / HOTS / Monitor consistency check (vs intended stagger + interactive on lists, toast-in on empties)

| Template | Stagger on lists? | Interactive on list units? | Toast-in on empty states? |
| --- | --- | --- | --- |
| teacher_materials | Yes | Yes | Yes (pending empty `.hub-card`) |
| teacher_hots | Yes | No — intentional (action-only question cards) | Yes (`.empty-state-card`) |
| teacher_monitor | Yes | Yes | Yes (roster + assessments empty `.hub-card`s; also chips) |

---

## Verified — motion-wiring closure

Original analysis had Materials / HOTS / Monitor with **no** motion utilities. Those three now have list stagger (and Materials/Monitor have interactive cards). Shared `partials/flash.html` now carries `pro-toast-in`, inherited by all `layouts/pro.html` pages (spot-checked `teacher_home.html`, `student_home.html`) and by `login.html`. Messages + staff_page motion unchanged and still wired.

**Remaining motion gaps in this review set:** None for the intended wiring. HOTS question cards omit `pro-card-interactive` by deliberate design (button-driven actions only).

---

**Verdict:** Motion-wiring gap is **fully closed** across reviewed templates (HOTS question-card interactive omitted intentionally, not unresolved).
