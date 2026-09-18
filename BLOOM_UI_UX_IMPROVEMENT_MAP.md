# Bloom UI/UX Improvement Map

**Date:** 2026-09-18  
**Basis:** Live screenshots in `docs/audit-screenshots/` + prior system audit  
**Mode:** Visual product decisions only — no code changes yet  
**Aligned roadmap:** Trust → Design system → Student UX → Teacher UX → Learning loop → Mobile/a11y → Polish

This map answers, per screen: **Keep / Polish / Redesign**, what to change, and what not to touch.

Screenshots folder: [`docs/audit-screenshots/`](docs/audit-screenshots/)

---

## How to read this map

| Tag | Meaning |
| --- | --- |
| **KEEP** | Structure and intent are right; protect the pattern |
| **POLISH** | Same page, better hierarchy / color / empty states / copy |
| **REDESIGN** | Same purpose, substantially new composition |
| **TRUST FIX** | Correctness/labeling before visual investment |
| **DEFER** | Important later; not next |

Decision rule used here: **do not redesign what already feels intentional**; invest redesign energy where Bloom still feels like a dashboard or account form.

---

## Global findings (all screens)

### Already one product (student shell)

Across Home → Practice → Results → Announcements → Messages → Profile:

- Shared navy sidebar + Bloom crest + “Study assistant”
- Shared topbar utilities (bell, messages, avatar, gear)
- Shared light canvas + white cards + Bloom-blue primary
- Subject color accents appear on several student surfaces

**Verdict:** Student Pro shell is the visual identity to **extend**, not replace.

### Not yet one product (staff)

Teacher Materials / HOTS / Monitor / Announce / Admin:

- Same sidebar brand, but thinner topbar (often no messages/bell)
- Form-first “management console” density
- Less subject storytelling, fewer learning-oriented headers
- Chevron-only nav icons vs student icon set

**Verdict:** Unify onto student shell language in Phase 4 — **do not invent a second brand**.

### Cross-cutting trust/UX mismatches (fix before polish)

| Issue | Seen on | Fix type |
| --- | --- | --- |
| Gear looks like Settings; password lives on Profile | All student/staff topbars | TRUST FIX — decide Profile vs Settings |
| Bell implies notifications without a clear destination | Student topbar | TRUST FIX — wire to announcements unread or remove badge ambiguity |
| Progress / “0% complete” reads as curriculum completion | Home, Subject hub | TRUST FIX — relabel or redefine metric |
| Demo chat content inappropriate | Messages inbox + thread | TRUST FIX — replace seed content |
| Assessment flow invisible in demo (0 published) | Teacher home/admin content cards | TRUST FIX — seed published assessment |
| Result review “Nice work” with unanswered / weak score story | Result review | TRUST FIX + POLISH — honesty in feedback framing |
| Dual CSS (`style.css` + `bloom-pro.css`) | All pro pages | Phase 2 design-system consolidation |

---

## Screen-by-screen map

### 1. Login — `01-login.png`

**Disposition: POLISH (light)**

**What works**
- Clear brand moment: crest + “Bloom” + school name
- Soft atmospheric background (not flat admin gray)
- Strong primary Sign In CTA; focus ring visible on email
- Show password affordance

**Change**
- Keep pilot accounts collapsed/dev-only visually quiet (already muted)
- Ensure login stays the brand entry — don’t restyle toward dashboard chrome

**Leave alone**
- Card structure, field labels, keep-signed-in checkbox pattern

---

### 2. Home — `02-home.png`

**Disposition: REDESIGN (composition) + TRUST FIX (progress)**

**What works**
- “YOUR DAY” framing and Today CTA are the right product idea
- Subject color coding on My Subjects
- Primary action “Start now” is findable

**Problems (visual)**
- Four equal metric cards compete with Today (dashboard, not command center)
- Subject progress bars empty + “0% / Not started” dominate the story with little encouragement
- Welcome flash stacks above hero — fine functionally, noisy visually for first impression

**Problems (trust)**
- “Progress 0% · Across your subjects” implies completion, not score average

**Target composition**
1. Greeting + **one** primary Today action (hero)
2. Optional slim “next up” strip (max 1–2 secondary cues)
3. My Subjects as the secondary region (bridge into Subject Hub)
4. Metrics only if they earn trust (or demote/remove until metric is honest)

**Leave alone**
- Sidebar IA; Today concept; subject color system

---

### 3. Practice library — `03-practice.png`

**Disposition: POLISH**

**What works**
- Hero kicker “BUILD YOUR SKILLS” + clear purpose copy
- WorkItemCard pattern (subject rail, Ready tag, Start practice CTA)
- Subject filter chips

**Problems**
- Large empty lower canvas with only one item — feels unfinished, not “calm”
- Topbar shows school name instead of page title (inconsistent with other pages)

**Change**
- Stronger empty/populated density (when few items, reduce dead vertical space or show guided next step)
- Align topbar title behavior with Home/Practice setup (“Practice”)
- Keep WorkItemCard; don’t fork a new card type

**Leave alone**
- Library metaphor; filter chips; Start practice as primary

---

### 4. Practice setup — `09-practice-setup.png` (also mislabeled capture in `15-practice-take.png`)

**Disposition: KEEP + light POLISH**

**What works (best student flow on Bloom today)**
- Numbered Choose → Focus → Build → Generate
- Blue selection language vs green subject meaning
- Compact 1–15 stepper; type checkboxes; full-width Generate CTA
- Clear back + subject tags

**Problems**
- Error flash “Generate a Practice Check from the setup screen first” when hitting take without draft — correct, but tone can be calmer
- True **practice take** UI was not successfully captured in this set (gap)

**Change**
- Microcopy/loading state for generation
- Ensure take page follows same calm quiz language when captured next

**Leave alone**
- Step structure, selection cards, CTA — do not redesign

---

### 5. Results history — `04-results.png`

**Disposition: POLISH → later storytelling upgrade**

**What works**
- WorkItemCard reuse with Practice library (architecture win)
- Filters All / Assessments / Practice
- “Review →” as clear next action

**Problems**
- Feels like a filing cabinet when sparse (1 result + lots of white)
- Little “how am I doing over time?” narrative

**Change (near-term polish)**
- Stronger section hierarchy; friendlier empty/sparse states
- Surface score/outcome tone on the card (not only after Review)

**Change (Phase 5 learning loop — later)**
- “What to practice next” recommendation strip

**Leave alone**
- Shared WorkItemCard; filter model

---

### 6. Result review — `13-result-review.png`

**Disposition: POLISH (high value) + TRUST FIX**

**What works**
- Blue encouragement hero is more “learning product” than spreadsheet
- Per-item cards with Bloom tags, Your answer / Suggested, Why this matters, Rubric, Source
- Footer path: Ask Teacher / Back to Practice / Home — supports Improve → Continue

**Problems**
- Hero says “Nice work” while answers show “(No answer)” and score “0/1 automatic items” — **trust break**
- Three improve items + celebratory hero conflict
- Suggested answer only clear on some item types

**Change**
- Tone hero from attempt outcome (celebratory vs “Let’s review together”)
- Clarify auto-scored vs open-response scoring in the score chip
- Make “Practice this again” / “Re-read summary” a first-class next step (feeds Phase 5)

**Leave alone**
- Item review structure; Ask Teacher path; source citations

---

### 7. Announcements — `05-announcements.png`

**Disposition: POLISH**

**What works**
- Split inbox is a modern pattern
- Subject accent rails on list items
- Search + All/Unread filters
- Empty detail state exists (not a hard crash)

**Problems**
- Detail pane is a large blank with weak “select something” energy
- No auto-selected newest/unread — first paint feels unfinished
- Header blue bar vs list green accents — coherent enough, but selection state must be louder

**Change**
- Auto-select first unread (or newest) on load
- Stronger selected row + richer detail typography
- Tighten empty illustration so it doesn’t dominate half the viewport

**Leave alone**
- Split-pane model; filters; subject rails

---

### 8. Messages inbox — `06-messages.png`

**Disposition: POLISH (conversation list is already good)**

**What works**
- Modern messaging list: search, All/Unread/subject filters
- Subject-colored left borders + teacher identity
- Empty-thread preview copy for Math

**Problems**
- Inappropriate demo message preview (content, not chrome)
- Unread visual weight not strongly differentiated in this capture (all look similar)
- “3 conversations” includes empty threads — OK, but empty ones could be visually quieter

**Change**
- Replace demo fixtures
- Stronger unread (weight/badge/dot)
- Keep filters; don’t rebuild list architecture

**Leave alone**
- Row layout; subject filters; teacher-per-subject model

---

### 9. Messages thread — `12-messages-thread.png`

**Disposition: POLISH**

**What works**
- Back to conversations; teacher header; subject pill
- Sent bubble (blue) vs received (white); Read receipt on sent
- Composer + Enter/Shift+Enter hint + send button

**Problems**
- Short threads leave a tall empty chat well
- Teacher identity is initials-only (“DT”) — fine for pilot, thin for trust
- Demo content destroys perceived professionalism
- Thread appears without student sidebar in this capture (layout variant?) — verify consistency with pro shell

**Change**
- Better empty/short-thread vertical rhythm
- Composer polish (focus, disabled send, character limit feedback)
- Optional subject color whisper in header (already has English pill)

**Leave alone**
- Bubble model; polling architecture; student-initiates rule (product decision)

---

### 10. Profile — `07-profile.png`

**Disposition: REDESIGN (biggest student visual opportunity)**

**What works**
- Pro shell consistency
- Password form is complete and clear
- Basic identity header (name, email, section pills)

**Problems**
- Reads as **account admin**, not “me in Bloom”
- Stat row (Subjects / Activities / Unread) is generic dashboard residue
- Account details duplicate the header
- Gear still present in topbar → Settings/Profile confusion peaks here

**Target**
- Hero identity (avatar, name, section, subjects)
- Learning snapshot (recent practice, strengths, next step) — honest metrics only
- Account & security as a secondary section (not the whole page)
- Resolve Settings: either move prefs here, or make gear open a labeled Preferences panel and keep Profile for identity + security

**Leave alone**
- Password change capability; role/section facts

---

### 11. Subject hub — `08-subject-hub.png`

**Disposition: REDESIGN (conceptual bridge) + TRUST FIX**

**What works**
- Tabs: Assessments / Study / Practice / Results — correct learning arc
- Study tab materials card + Read Summary / Practice this lesson
- Backup upload path exists

**Problems**
- Sidebar still highlights **Home** while you’re in Science — weak place identity
- Header repeats “0% complete / Keep practicing” twice
- Science subject color underused (page feels generic blue, not Science)
- Upload form sits heavy beside learning content — competes with “read then practice”

**Target**
- Subject-colored hero (Science green language)
- Clear pipeline: Learn (materials) → Understand (summary) → Practice → Assess
- Progress label honesty
- Demote backup upload (collapsed “Don’t see your file?”)

**Leave alone**
- Tab model; material → summary → practice links

---

### 12. Summary reader — `10-summary.png`

**Disposition: POLISH**

**What works**
- Jump-to + key idea cards
- Source pills
- Footer CTAs: Practice this lesson / Ask Teacher / Back — excellent loop

**Problems**
- “SCIENCE • AI SUMMARY” uses harsh red metadata (reads like error)
- Source pills also red — status-color collision
- Sidebar still on Home

**Change**
- Metadata/source use quiet or subject-colored chips, not error red
- Active nav should reflect Study/Subject context if possible
- Keep footer CTA trio

**Leave alone**
- Key-idea structure; jump nav; practice CTA

---

### 13. Teacher home — `14-teacher-home.png`

**Disposition: REDESIGN (Phase 4) — keep data, change feel**

**What works**
- Attention queue concept (“All clear”)
- Useful stat tiles (materials / drafts / pending / published)
- Same brand sidebar

**Problems**
- Sparse intro card = empty ops console
- Feels like admin, not “guide my students”
- Published assessments = 0 makes the product story incomplete

**Change (Phase 4)**
- Teacher command center: Needs attention → next actions (Upload / Generate / Publish / Message)
- Match student hero/card language
- Seed demo assessment so Monitor/HOTS aren’t empty stories

**Leave alone**
- Nav destinations; underlying metrics

---

### 14. Teacher HOTS — `16-teacher-hots.png`

**Disposition: POLISH now / shell REDESIGN in Phase 4**

**What works**
- Clear generate form; grounded-in-material copy; difficulty note is excellent pedagogy UX
- Empty state for “No HOTS sets yet” is honest

**Problems**
- Pure form stack; little preview personality
- Empty state below form feels disconnected

**Change**
- After generate, make review the star (item cards closer to student result review language)
- Keep generation controls

---

### 15. Teacher materials — `19-teacher-materials.png`

**Disposition: POLISH / Phase 4 shell unify**

**What works**
- Approved list + upload & summarize is clear
- Subject filing note at top

**Problems**
- Browser-native file control looks legacy next to Bloom buttons
- All-caps field labels feel admin-tool

**Change**
- Friendlier upload dropzone matching student backup card language
- Keep approve/summarize pipeline

---

### 16. Teacher monitor / announce / messages — `17`, `18`, `21`

**Disposition: POLISH + Phase 4 unify**

- **Monitor:** Preserve release controls — they are product-critical; improve scanability of attempts/releases.
- **Announce:** Keep post form; align announcement preview with student announcements visual language.
- **Messages:** Same polish as student thread; teacher inbox can emphasize unread students first.

---

### 17. Admin home — `22-admin-home.png`

**Disposition: DEFER (minimal polish only)**

**What works**
- Enough for pilot oversight (users + content counts)

**Problems**
- Pluralization bugs (“1 students”, “1 approved materials”)
- Sparse empty canvas
- Settings/Profile/gear confusion also present

**Change**
- Fix copy bugs only for now
- Do not invest in a full admin visual system yet

---

## Missing captures (do before declaring visual complete)

| Gap | Why it matters |
| --- | --- |
| Assessment lobby / take / assessment result | Core Bloom purpose; demo currently has 0 published |
| True practice take (in-progress answering) | Setup is strong; take experience still visually unknown |
| Mobile viewports | Phase 6 |
| Error states | Trust |
| Announcements selected/detail populated | Selection polish depends on this state |
| Unread-heavy messages | Badge/weight decisions |

---

## Recommended change matrix (what to do when)

### Phase 1 — Trust (before more pretty)

1. Relabel/redefine Home + Subject progress  
2. Seed published assessment + walkable take/result demo  
3. Decide Profile vs Settings vs Preferences (gear)  
4. Clarify notification bell meaning  
5. Replace inappropriate demo messages  
6. Honest result-review hero tone when unanswered/low score  
7. Gemini key / production seed-debug (from system audit)  

### Phase 2 — Design system pass

Extend existing `--bloom` / `--pro` / `--wic` tokens:

Colors · type · cards · buttons · inputs · badges · subject colors · empty states · page headers · nav · spacing · shadows · borders  

Apply staff pages to the **same** language. Do not invent a third palette.

### Phase 3 — Student redesign priority

| Order | Screen | Mode |
| --- | --- | --- |
| 1 | Home | REDESIGN composition |
| 2 | Subject hub | REDESIGN bridge |
| 3 | Profile | REDESIGN identity |
| 4 | Results history + review | POLISH → storytelling |
| 5 | Announcements | POLISH selection |
| 6 | Messages | POLISH thread/composer |
| 7 | Practice setup | KEEP |
| 8 | Summary | POLISH color semantics |

### Phase 4 — Teacher

Unify shell; keep Materials / HOTS / Monitor / Announce / Messages workflows; elevate “guide students” command center.

### Phase 5 — Learning loop

Results → next practice / re-read summary recommendations (“Understand mistakes → Improve → Continue”).

---

## Explicit non-goals (for now)

- Do not rewrite the learning loop backend  
- Do not redesign Practice Setup from scratch  
- Do not rebuild Messages as a new chat product  
- Do not invest heavily in Admin visuals  
- Do not add gamification overlays  
- Do not throw away `--bloom` / `--pro` / `--wic` tokens  

---

## Bottom line

Bloom’s student shell already has a recognizable face. The product gap is not “missing random features” — it is:

1. **Trust** (progress, assessments demo, settings meaning, feedback honesty)  
2. **One visual language** (student → teacher)  
3. **A few high-leverage student compositions** (Home, Subject Hub, Profile)  
4. **Results as the engine of improvement**, not just a score archive  

Screenshots to review locally: `docs/audit-screenshots/` (20 PNGs). Open them in order `01` → `22` alongside this map.
