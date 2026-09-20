# Teacher UX Audit — Bloom

**Date:** 2026-09-20  
**Mode:** Observational audit + prioritized proposal  
**Scope:** `teacher_home`, `teacher_materials`, `teacher_hots`, `teacher_monitor`, `messages_inbox` / `messages_thread` (teacher), `staff_page` (Announce), `layouts/pro.html`, `partials/pro_sidebar.html`, `partials/pro_topbar.html`, `pro-shell.js`  
**Constraint reminder:** Additive polish only; no token rewrites; no fake metrics; Phase 3 implements **SAFE** items only after explicit approval.

---

## Phase 1 — Findings

### 1. Navigation & information architecture

**Current sidebar order** (`teacher_nav()`):  
Home → Messages → Materials → HOTS → Monitor → Announce → Profile

**Workflow claim in the brief:** upload → generate → publish → monitor → communicate.

| Observation | Detail |
| --- | --- |
| Order vs workflow | Materials → HOTS → Monitor matches create/publish/monitor. **Messages sits before Materials**, so “communicate” is elevated above the production pipeline. Announce sits after Monitor (broadcast after ops) — reasonable. |
| Profile | Correctly last. |
| Icons | Teacher links all use generic `›`; student nav has distinct glyphs. Minor consistency gap, not a workflow blocker. |
| Topbar context | Home/Materials/Monitor: `Teacher · {subject}`. HOTS: `HOTS Generator`. Messages/Announce: page-specific. Slight label drift, not structural. |
| Shell split | Six destinations on `layouts/pro.html`; **Announce still on `staff_page.html`** (legacy body/`section-title` full scale). Largest “left one app” feeling. |

**Verdict on reorder:** A Materials-first order (Home → Materials → HOTS → Monitor → Messages → Announce → Profile) would match the stated pipeline better. Current order prioritizes inbox. **Neither is wrong** — this is a product choice, not a bug. Flagged as **NEEDS DECISION** below.

---

### 2. Redundant or missing functionality

#### Missing (reasonable teacher expectations — not currently present)

| Capability | Notes |
| --- | --- |
| Duplicate / clone HOTS set | No copy-from-existing-draft action |
| Bulk release scores across assessments | Release is per-panel only on Monitor |
| Archive / hide old materials | Rejected list exists; no archive for approved/deployed clutter |
| Delete draft HOTS set | Publish/regenerate only; no discard draft |
| Teacher-initiated message without student-started thread | Monitor “Message” links to `messages_thread`; conversation model historically assumes student start — confirm behavior if empty (efficiency gap if teacher hits a wall) |
| Edit published announcement | Announce is post + history panels; no edit/delete in template inventory |

#### Redundant / dual forms

| Pattern | Where |
| --- | --- |
| Empty states | `hub-card` (Home, Materials pending, Monitor) vs `empty-state-card` (HOTS, Messages) vs plain `section-note` (Materials deployed empty) |
| Status labeling | Home queue: `hub-card-kicker` (category). Materials/HOTS/Monitor: `teacher-status-pill` (workflow status). Messages: `status-pill status-subject` |
| Primary CTA weight | Pending Materials **Review** = solid `today-action`; Home queue CTAs = soft only; forms = `btn-primary` |
| Hero patterns | Command hero (Home, Monitor) vs default `pro-hero` (Materials, HOTS, Messages) vs none (Thread, Announce) |

Nothing critical is *duplicated as two competing features* (e.g. two different release UIs). Duplication is mostly **visual/pattern**, not feature forks.

---

### 3. Component consistency (post motion / pill unification)

| Area | Consistent? | Notes |
| --- | --- | --- |
| `.teacher-status-pill` on workflow lists | Mostly | Materials, HOTS sets, Monitor panels. Home queue intentionally uses kickers (category, not status) — OK. |
| Motion (stagger / interactive / toast) | Mostly | Wired on Home queue, Materials lists, Monitor lists/grid, Messages. HOTS: stagger on questions; empty toast; **set shells are `lobby-card` without interactive** (intentional earlier). |
| Empty-state pattern | **No** | Three patterns still in play (see §2). |
| Button hierarchy | **Partial** | `btn-primary` for commit forms is consistent. List CTAs mix solid vs soft without a clear rule (pending Review solid; deployed View soft — that hierarchy is good; Home soft-only is softer than Materials). |
| Card density | **Partial** | HOTS packs generate form + full question cards in `lobby-card` — denser than Materials list rows. Monitor assessment panels pack release controls + submissions — dense but task-appropriate. |
| Announce shell | **Outlier** | Still `staff_page` / full `section-title` / no `section-eyebrow` — feels like a different app. |

---

### 4. Simplicity vs density (per page)

| Page | Too much at once | Too sparse / extra clicks |
| --- | --- | --- |
| **Home** | Stats grid always shows four tiles even when queue is empty (useful, not noisy). | Queue omits Monitor release holds (see §5). |
| **Materials** | Upload form always expanded above lists (fine for pilot volume). Deployed empty is a one-line note — thinner than other empties. | Review is a separate page (correct for trust); list → review is one intentional click. |
| **HOTS** | Generate form always visible; each draft shows **all questions expanded** with regenerate — heavy when multiple drafts. | No collapse/summary of drafts; publish deadline field always shown on draft. |
| **Monitor** | Three release toggles per assessment always visible when eligible — correct for control, busy when many panels. Pulse chips are **non-clickable** unlike Home’s linked pulses. | Message is on-card (good). No deep link from Home for “scores waiting to release.” |
| **Messages inbox** | Filters OK. | Search label/placeholder still **“Search teachers…”** for teachers — student-copy leak. |
| **Messages thread** | Chat focus layout is appropriately sparse. | — |
| **Announce** | Form + past posts on one staff page — fine for volume. | Typography/shell denser/legacy vs rest of teacher UI. |

---

### 5. Cross-page connective tissue (Home “Do this next”)

**Currently surfaces:**

1. Unread messages → Messages  
2. Pending materials → review / materials list  
3. Draft HOTS → HOTS  

**Does not surface (actionable elsewhere):**

| State | Exists on | Gap |
| --- | --- | --- |
| Published HOTS with submissions but scores/answers/feedback not released | Monitor | Teacher must open Monitor; Home stays “Nothing pending” |
| Closed assessment needing reopen / extra attempt | Monitor | Same |
| Rejected materials awaiting teacher follow-up | Materials rejected section | Optional; lower priority |
| Zero approved materials (block HOTS generate) | HOTS empty materials note | Home empty CTA points to Materials upload — partial coverage |

**Already good connective tissue:**

- Home pulse → Monitor (class avg) / Messages (unread)  
- Monitor student **Message** soft action  
- Materials empty → soft CTA; HOTS no-materials → Materials; Monitor no assessments → HOTS  

---

## Phase 2 — Prioritized proposal

### SAFE (apply in Phase 3 after approval — UI consistency only)

| ID | Change | Why |
| --- | --- | --- |
| S1 | Unify empty states on teacher pro pages to one pattern: prefer **`hub-card` + `pro-toast-in`** (Home/Materials/Monitor) for list empties; convert HOTS empty `empty-state-card` to the same hub-card pattern **or** document HOTS as the sole `empty-state-card` exception — recommend converting HOTS to hub-card for parity. | Removes “different app” empty chrome. |
| S2 | Materials deployed empty: replace bare `section-note` with same hub-card empty as pending. | Same job, same component. |
| S3 | Button hierarchy rule, applied consistently: **commit forms** → `btn-primary`; **primary list decision** (Review, Reopen+extra, Publish-adjacent) → solid `today-action`; **secondary navigation** (View, Open, Message, Back, Regenerate) → `today-action-soft`. Audit Materials/Monitor/HOTS/Home against this — soft Home queue CTAs may stay soft (queue is triage) or promote Review-equivalent to solid when type is Materials. Prefer: keep Home soft; ensure Monitor Close stays soft, Reopen stays solid (already). | One CTA language. |
| S4 | Messages inbox teacher copy: search label/placeholder → “Search students or messages…” when `user.role == 'teacher'`. | Fixes student-copy leak; no backend change. |
| S5 | Monitor pulse chips: if Home pulses are links, make Monitor pulses links to the same destinations where hrefs already exist (or leave non-link but match visual quiet state) — **only** if hrefs are obvious without new routes. Prefer linking class-avg region stays on-page; practice count could scroll to roster. If no clean target, skip. | Consistency without new IA. |
| S6 | Topbar subtitle consistency: HOTS uses `Teacher · {subject}` like Materials/Monitor (drop unique “HOTS Generator” sub or keep page title in hero only). | Shell chrome parity. |
| S7 | Spacing/density CSS only where teacher pages diverge from established `.home-section` / `.section-heading-row` / `.hub-list.stack-md` gaps — no new tokens. | Finish polish. |
| S8 | Announce: **do not** migrate shell in SAFE set (that’s S/N below). SAFE-only: if Announce stays on staff_page for now, align flash/`pro-toast-in` and panel motion already present — no further SAFE work unless a one-line class parity is trivial. | Avoid half-migration. |

### NEEDS DECISION (wait for explicit approval)

| ID | Change | Why it needs a call |
| --- | --- | --- |
| N1 | **Reorder sidebar** to Home → Materials → HOTS → Monitor → Messages → Announce → Profile | Matches upload→generate→monitor→communicate; demotes Messages. **Deferred — post-defense follow-up** |
| N2 | **Migrate Announce to `layouts/pro.html`** (same hero/eyebrow pattern as Materials) | Biggest shell consistency win; touches route template choice + staff_page usage for teachers only. **Deferred — post-defense follow-up** |
| N3 | **Extend Home queue** with Monitor items: e.g. “N assessments waiting for score release” → Monitor | Changes what counts as “pending”; backend attention builder change. **Approved & implemented in Phase 3** (2026-09-20). |
| N4 | Collapse / accordion for HOTS draft question lists | Progressive disclosure; changes interaction model. |
| N5 | Duplicate HOTS set / delete draft / archive materials / bulk release | New features; out of finishing-pass scope unless prioritized. |
| N6 | Teacher-start conversation guarantee from Monitor Message | May already work via `get_or_create`; if not, behavior change. Confirm before coding. |
| N7 | Add teacher-facing icons in sidebar (match student glyph richness) | Visual only but product taste; low value pre-defense. |

### Efficiency note (no new shortcuts without decision)

- Monitor → Message: **already present** and consistent on student cards.  
- Do **not** add Home → deep-link “message this student” or Materials → “generate HOTS from this row” without **N-class** approval.  
- Home → Materials (empty CTA) and HOTS → Materials (no materials) already cover the main pipeline shortcuts.

---

## Phase 3 — Gate

**Phase 3 implemented 2026-09-20:** S1, S2, S4, S6, and N3 (approved).  
**Deferred — post-defense follow-up:** N1 (sidebar reorder), N2 (Announce → pro.html). No code changes toward N1/N2.

Suggested Phase 3 batch if approved as-is: **S1, S2, S4, S6** (clear, low-risk).  
Treat **S3, S5, S7** as optional follow-ons in the same pass if time allows.  
Hold remaining **N\*** (N4–N7) until individually approved.

---

*End of audit. Phase 1–2 written observationally; Phase 3 SAFE + N3 applied in a later turn.*
