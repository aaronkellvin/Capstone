# Bloom Redesign — Cursor Prompt (Ready to Paste)

**How to use:** Copy everything under “CURSOR PROMPT (START)” through “CURSOR PROMPT (END)” into a new Cursor agent chat. Attach or `@` reference: `docs/STUDENT_UX_AUDIT.md`, `docs/TEACHER_UX_AUDIT.md`, `docs/UI_GAP_ANALYSIS.md`, `static/css/bloom-pro.css`, `layouts/pro.html`.

**Reference video provenance (honesty):** I could **not** watch the YouTube videos as video streams. Principles marked **Verified** come from accessible titles, transcripts, or detailed notes for those exact URLs. Principles marked **Inferred / professional** come from senior UI/UX practice applied to Bloom, or from partial coverage of a tip when the full tip list was incomplete.

| URL | Verified identity | Source of principles |
| --- | --- | --- |
| https://www.youtube.com/watch?v=8pMUkEbAM7g | *Top 5 UX/UI Design Tips… Part 1* (uxpeak) | Transcript / notes — hierarchy, prioritization, soft tinted shadows, presentation/trust |
| https://www.youtube.com/watch?v=EcbgbKtOELY | *Every UI/UX Concept Explained in Under 10 Minutes* | Full transcript — affordances, hierarchy, grids/whitespace, type, color, shadows, states, micro-interactions, overlays |
| https://www.youtube.com/watch?v=Xzh8xjimmp8 | *Top 5 Advanced UX/UI Tips… Part 3* (uxpeak) | Partial transcript — category screens (minimal vs decorative vs usable), appearance≠usability, contrast, visual consistency |

---

## CURSOR PROMPT (START)

```markdown
# Mission

You are acting as a **senior UI/UX designer, product designer, design-system architect, and frontend design reviewer** working inside the Bloom Capstone codebase.

Bloom already works. Your job is **not** to rebuild features, routes, auth, CSRF, scoring, messaging, HOTS generation, or release controls.

Your job is to make Bloom feel like **one professionally designed modern product** — cohesive visual language + UX language — by consolidating what already exists (`--bloom`, `--pro`, `--wic`, WorkItemCard, hub-card, status-pill, motion utilities, pro shell) and fixing inconsistencies that make pages feel like different templates.

Read first (do not skip):
- `docs/STUDENT_UX_AUDIT.md`
- `docs/TEACHER_UX_AUDIT.md`
- `docs/UI_GAP_ANALYSIS.md`
- Current tokens in `static/css/bloom-pro.css` and base patterns in `static/css/style.css`

Then produce work in this order:
1. **Audit confirmation** (short) — what is already good vs what still fragments the language
2. **Bloom Design System consolidation plan** (tokens + component rules) — additive, mapped to existing classes
3. **Page-by-page redesign notes** for every major screen (student first, then teacher)
4. **SAFE implementation batch** only after I approve the plan — unless I explicitly say “implement SAFE now”

If I have not approved implementation yet: **output the plan only; do not edit files.**

---

# Non-negotiable product constraints

- Additive polish only. Do **not** invent a second design language alongside `--bloom` / `--pro` / `--wic`.
- Preserve backend logic, routes, CSRF, auth, WorkItemCard contracts, ChatMessage.read_at, Monitor release controls, AI fallbacks.
- No fake metrics, no invented progress, no placeholder content presented as real data.
- Reuse existing components for the same job (`work_item_card`, `.hub-card`, `.status-pill`, `.today-action` / `.btn-primary` / `.wic-btn`, `.empty-state-card`, motion utilities). Do not create duplicate “Card2” / “ButtonNew” systems.
- Student-friendly ≠ childish. Personality via type, soft color, microcopy, subtle motion — not cartoon chrome.
- Prefer **comfortable + efficient** density (educational product students use for real sessions). Not a sparse marketing site. Not a packed admin spreadsheet.

---

# Design philosophy (teach this to yourself on every screen)

## Modern ≠ more effects

Quality comes from hierarchy, typography, spacing, alignment, composition, consistency, contrast, rhythm, component rules, interaction states, IA, density, intentional color, and **meaningful** motion.

Avoid decoration that does not help the task.

## Anti–AI-generated UI (hard ban)

Do **not** produce the predictable “vibe-coded SaaS” look:
- purple/indigo gradient everything
- glassmorphism stacks
- identical mega-rounded cards (`border-radius: 20px` everywhere)
- giant blurry shadows on every card
- floating cards / blob decorations / sparkle icon noise
- excessive empty whitespace with little information
- every section wrapped in a card “because cards”
- generic dashboard chrome that could belong to any product after removing the logo

Bloom must look like **deliberate decisions**, not an assembled component collage.

## Evaluate every screen with these questions

**Hierarchy**
- What is the single most important thing?
- What is second?
- What must be visually quiet?

**User intention**
- Why is the student/teacher here?
- What is the primary task?
- Is the primary action obvious within ~3 seconds?

**Cognitive load**
- What competing elements can be removed, merged, or demoted?
- Unnecessary cards / borders / icons / buttons?

**Navigation**
- Where am I?
- Where can I go?
- Can I predict what a click does?

**Consistency**
- Same job → same component, same CTA weight, same empty pattern, same heading scale?

**Signifiers & affordances** (from verified UI fundamentals)
- Does interactive UI *show* it is interactive (hover/focus/active/disabled) without instructions?
- Does grouping (proximity, enclosure, shared background) show what belongs together?
- Are inactive states visually inactive?

---

# Principles extracted from reference material

## Verified — Video 1 (uxpeak Part 1, `8pMUkEbAM7g`)

1. **Differentiate with size, weight, color, and cues** — same-weight label/value grids feel like spreadsheets, not products.
2. **Prioritize before decorating** — rank what users need; emphasize values/actions, de-emphasize labels.
3. **Soft, background-tinted shadows** — harsh pure black/gray shadows look cheap; if shadow is the first thing you notice, it is wrong.
4. **Presentation builds trust** — show the real content of the product (for Bloom: real lesson titles, real feedback, real next steps — never fake polish over empty honesty).
5. **Iterate** — improve hierarchy and clarity in passes; do not “one-shot restyle.”

## Verified — Video 2 (UI/UX concepts crash course, `EcbgbKtOELY`)

1. **Affordances / signifiers** — containers, selection, disabled gray, nav active, hover, tooltips communicate behavior.
2. **Hierarchy = contrast** — size, position, color; primary content larger/higher; metadata smaller/quieter.
3. **Grids are guidelines** — 4-point / 8-point rhythm matters more than rigid 12-column fetish; **whitespace + grouping** matter more than grid theater.
4. **Typography** — prefer a tight system; for denser product UI keep display sizes restrained; tighten large headings slightly (tracking/line-height) for polish.
5. **Color with purpose** — one primary brand ramp + semantic colors (success/warn/danger/info); color is meaning, not fill.
6. **Shadows by elevation** — cards lighter than canvas; popovers stronger than resting cards; never “shadow first.”
7. **Icons sized to text line-height**; ghost buttons for secondary; primary/secondary pairing.
8. **Full interaction lifecycle** — default → hover → focus → active → loading → success/error → disabled.
9. **Micro-interactions confirm outcomes** (e.g. copied, sent, saved) — not decorative bounce.
10. **Overlays** — protect text contrast; prefer gradient/controlled overlays over crushing the content.

## Verified (partial) — Video 3 (uxpeak Part 3, `Xzh8xjimmp8`)

On **category / chooser screens** (maps to Bloom subject pickers, Practice library filters, hub tabs):
1. **Plain equal lists** force users to read everything — add rhythm/hierarchy without clutter.
2. **Junior “designed” versions** often prioritize looks over usability (busy images, weak contrast, inconsistent art).
3. **Professional version** uses consistent, soft color-coded surfaces, readable type, and scannable structure — cohesive brand, not stock-photo collage.
4. **Appearance ≠ usability** — reject redesigns that look richer but scan worse.

## Inferred / professional (applied to Bloom; not claimed as video quotes)

- Educational products need **honest empty/loading states** and **clear next actions** after weak results (Bloom already started this — extend consistently).
- Student and teacher shells should feel like **one product family**, not two apps (Announce-on-staff_page is a known teacher outlier — do not expand that pattern).
- Subject Hub Practice vs Practice library WorkItemCard split is the largest student “two products” problem — resolve by consolidating to one list atom for the same job, or explicitly document two densities with shared tokens (prefer one atom).
- Density: dashboards/hubs denser than marketing; take flows quieter and more focused.

---

# Bloom Design System — consolidate, don’t reinvent

## Tokens (extend existing)

Work inside `bloom-pro.css` families already present:
- `--bloom-*` brand
- `--pro-*` shell/surface/motion
- `--wic-*` work items
- subject accents

Define/confirm explicit rules for:
- primary / secondary / accent
- background / surface / elevated surface
- text / muted text
- border / focus ring
- success / warning / error / info

Do **not** introduce a parallel purple SaaS palette. Bloom’s blue educational brand stays.

Document a **spacing scale** (4-point based: 4/8/12/16/24/32/48) and stop inventing one-off gaps unless task-justified.

Document a **radius scale** (e.g. sm/md/lg) — not everything is heavily rounded.

Document **elevation**: 0 (flat), 1 (resting card), 2 (dropdown/popover), 3 (modal) — shadows optional at 0–1.

## Typography hierarchy (map to existing classes where possible)

| Role | Intent | Prefer existing |
| --- | --- | --- |
| Display / greeting | Rare, Home command | `.pro-hero-title` |
| Page title | One per page | `.pro-hero-title` |
| Section title | Section H2 | `.section-title.section-title-sm` |
| Card title | List/work item | `.hub-card-title` / WIC title |
| Body | Reading | default content |
| Supporting / meta | Quiet | `.hub-card-meta`, `.section-note` |
| Label / eyebrow | Uppercase/small | `.section-eyebrow`, `.hub-card-kicker` |
| Button | Action | button text styles already on `.btn-primary` / `.today-action` / `.wic-btn` |

Rule: **hierarchy from type first**, borders/cards second.

## Components — one job, one component

| Job | Canonical |
| --- | --- |
| Navigable work item (practice/result rows) | `work_item_card` + `wic-btn` |
| In-flow list decision row (hub study/assessments, queues) | `.hub-card` + `.today-action` / soft |
| Workflow status (teacher) | `.teacher-status-pill` |
| Student status/subject chips | `.status-pill` (+ tones) |
| Empty list | `.empty-state-card` or hub-card empty (pick one rule per context; document it) |
| Primary commit | `.btn-primary` |
| Primary list decision | solid `.today-action` or `.wic-btn-primary` by context |
| Secondary | `.today-action-soft` / `.wic-btn-secondary` |
| Filters | `.chip-link` |
| Motion enter lists | `.pro-stagger-in` + `.pro-card-interactive` |
| Toast/flash enter | `.pro-toast-in` (no dead `pro-toast-out` without dismiss JS) |

If two pages solve the same job with different atoms, **unify** — do not “both are fine.”

## Interaction states (required)

For buttons, links, chips, inputs, cards-as-links, send controls:
default → hover → focus-visible → active → disabled → loading (when async) → error/success when applicable.

Respect `prefers-reduced-motion`. Motion must explain change (enter list, open panel, confirm send) — never ambient decoration.

## Empty / loading / error

- Empty: title + one-sentence why + **one** honest next action (no fake sample data).
- Loading: skeletons / stable layout (`pro-skeleton` if present) — no content jump.
- Error: plain language + recovery action; never silent failure.

## Responsive

- Desktop/laptop: sidebar + content (existing pro shell).
- Narrow: existing off-canvas sidebar behavior — improve hierarchy, don’t invent a second app.
- Do not only scale down: stack, prioritize primary CTA, collapse secondary chrome.
- Touch targets ≥ ~44px where primary actions sit.
- Propose bottom nav **only** as NEEDS DECISION if truly necessary; do not implement without approval.

## Accessibility

- Contrast for text and pills
- Visible focus rings
- Semantic headings in order
- Labeled inputs
- Don’t rely on color alone for score/unread
- Reduced motion respected

---

# Page-by-page review (mandatory)

For each page below, write: **Purpose → Primary action → Hierarchy (1st/2nd/quiet) → Current language issues → Target pattern (which existing components) → SAFE vs NEEDS DECISION changes**.

### Student
- `student_home.html`
- `subject_hub.html` (all tabs)
- `practice_hub.html`
- `practice_setup.html`
- `practice_take.html`
- `assessment_lobby.html`
- `assessment_take.html`
- `summary_reader.html`
- `results.html`
- `practice_result.html`
- `announcements.html`
- `messages_inbox.html` / `messages_thread.html` (student)
- `profile.html`
- Login / auth surfaces if in scope

### Teacher (keep family consistency; don’t fork a new theme)
- `teacher_home.html`
- `teacher_materials.html`
- `teacher_hots.html`
- `teacher_monitor.html`
- Messages (teacher)
- Announce (`staff_page` — known shell outlier; prefer documenting as deferred unless I approve migration)

### Shared chrome
- `layouts/pro.html`, `pro_sidebar`, `pro_topbar`, flashes, overlays/modals/loading

Known audit hotspots to address in the plan (from STUDENT/TEACHER audits):
1. Subject Hub practice rows vs Practice library WorkItemCard (**highest priority student consistency**)
2. Empty-state / CTA class drift
3. Motion unevenness (Messages polished; Home/Practice/Results quieter)
4. Teacher Announce shell outlier (usually deferred)
5. Home queue completeness (teacher release items — already partly addressed; don’t regress)

---

# Delivery format

## If planning only
1. Executive diagnosis (½ page)
2. Design system rules table (tokens/type/spacing/radius/elevation/components)
3. Page-by-page notes
4. Prioritized backlog: **SAFE** vs **NEEDS DECISION**
5. Explicitly list what you will **not** change (routes, fake metrics, new purple theme, etc.)

## If implementing (only after approval)
- SAFE items first, small diffs, reuse classes
- Show diffs
- Confirm no behavioral regressions on practice submit, assessment attempts, messaging, release controls
- Update or append a short note in `docs/STUDENT_UX_AUDIT.md` / teacher audit under “Redesign pass” if structure rules change

## Stop and ask when
- A change would alter task flow, IA/nav order, or add/remove primary actions
- Unifying components would break a meaningful density difference you believe should stay
- You are tempted to add new CSS frameworks, icon packs, or illustration systems

---

# Success criteria

Bloom feels like **one product**:
- A student can move Home → Subject → Practice → Results → Messages without feeling a template switch
- A teacher’s Materials/HOTS/Monitor/Home share the same language as the student shell family
- Screens answer Where / Do / Next / Progress / Attention without visual noise
- The UI looks designed, not generated
- Personality is warm and educational, not childish or corporate-SaaS

Begin with the planning deliverable. Do not edit code until I say which SAFE items to implement.
```

## CURSOR PROMPT (END)

---

## How to brief Cursor in one line

> Implement the Bloom redesign plan using `@docs/BLOOM_REDESIGN_CURSOR_PROMPT.md` — planning only first; consolidate `--bloom/--pro/--wic`; no rebuild; no AI-SaaS aesthetics; unify same-job components per STUDENT/TEACHER audits.

---

## Optional: what to say after the plan

> Implement SAFE items S… only. Hold all NEEDS DECISION. Show diffs. Do not touch N1 sidebar / N2 Announce unless I name them.
