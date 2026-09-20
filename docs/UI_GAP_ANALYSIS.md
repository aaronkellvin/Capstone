# UI Gap Analysis — Teacher-Facing Templates

**Date:** 2026-09-20  
**Mode:** Observational inventory only — no fixes, no recommendations  
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
| **Motion** | Queue: `pro-stagger-in` on `.hub-list`; `pro-card-interactive` on pending `.hub-card`s. Empty queue card: no interactive / toast. Stats: no motion utilities. No `pro-toast-in`. |

---

## `teacher_materials.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1 via default pro hero: `.pro-hero-title` from `{% block page_title %}` (“Review before class”) — same class/scale as Home hero title. Section H2s: `.section-title.section-title-sm` (aligned with Home section headers). |
| **Card / list unit** | Primary actionable lists: `.hub-card` inside `.hub-list` (pending / deployed / rejected). Empty pending: `.hub-card`. Upload form is a bare form under a section heading (not a list card). |
| **Color / status** | Uses `.teacher-status-pill` (`.is-pending`, `.is-approved`, `.is-rejected`) with attribution in `.hub-card-meta`. No plain status kickers for material status. |
| **Motion** | None of `pro-stagger-in`, `pro-card-interactive`, or `pro-toast-in` present on this template. |

---

## `teacher_hots.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1 via default pro hero: `.pro-hero-title` (“HOTS Generator”) — same class as Home. Section H2s: `.section-title.section-title-sm`. |
| **Card / list unit** | Generate block + each assessment set: `section.lobby-card`. Questions: `.hub-card.hub-card-stack` inside `.hub-list.stack-sm`. Empty: `article.empty-state-card`. |
| **Color / status** | Set-level: `.teacher-status-pill.is-{{ assessment.status }}` (draft / published / closed). Question meta: plain `.hub-card-kicker` (bloom · qtype · citation) — not status. |
| **Motion** | No `pro-stagger-in`, `pro-card-interactive`, or `pro-toast-in` on this template. |

---

## `teacher_monitor.html`

| Dimension | Current state |
| --- | --- |
| **Typography** | Page H1: `.pro-hero-title` in custom `.home-command-hero` (same pattern/class as Home). Section H2s: `.section-title.section-title-sm`. |
| **Card / list unit** | Roster: `.teacher-student-card` in `.teacher-student-grid`. Assessments: `.teacher-monitor-card` in `.teacher-monitor-list`. Empties: `.hub-card`. |
| **Color / status** | Assessment cards: `.teacher-status-pill.is-{{ panel.status }}`. Also `.teacher-release-pill`, `.teacher-score-chip` (Monitor-specific). |
| **Motion** | No `pro-stagger-in`, `pro-card-interactive`, or `pro-toast-in` on lists or pulse chips. |

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
| **Motion** | `pro-stagger-in` on `.hub-list`; `pro-card-interactive` on panel `.hub-card`s; `pro-toast-in` on flash `li.flash`. `.lobby-card` forms: no interactive. |

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

### Motion utility wiring

| Template | `pro-stagger-in` | `pro-card-interactive` | `pro-toast-in` |
| --- | --- | --- | --- |
| teacher_home | Yes (queue) | Yes (pending cards) | No |
| teacher_materials | No | No | No |
| teacher_hots | No | No | No |
| teacher_monitor | No | No | No |
| messages_inbox | Yes | Yes | Yes (empties) |
| messages_thread | Yes (thread) | No | Yes (empty + status) |
| staff_page | Yes | Yes (panels) | Yes (flashes) |

---

*End of inventory. No remediation proposed in this document.*
