# Bloom — Current System Audit

**Date:** 2026-09-18  
**Scope:** Complete current-state audit of the Bloom codebase and running local app  
**Mode:** Audit only — no code changes, no redesign, no new features  
**App under review:** Flask app served at `http://127.0.0.1:5001`  
**Screenshots:** `docs/audit-screenshots/` (live captures; see Section 14)

This report is evidence-based. Items marked **CONFIRMED**, **POSSIBLE**, or **NOT ENOUGH EVIDENCE** reflect how strongly the code and runtime capture support the claim. Demo account passwords are not listed here.

---

## 1. System Overview

### Current technology stack (verified)

| Layer | Technology | Evidence |
| --- | --- | --- |
| Backend | Python Flask ≥3.0 | `requirements.txt`, `app.py` |
| ORM / DB | Flask-SQLAlchemy ≥3.1, SQLite file DB | `models.py`, `SQLALCHEMY_DATABASE_URI` → `instance/bloom.db` |
| Templates | Jinja2 HTML templates | `templates/` |
| Frontend JS | Vanilla JS (no React/Vue/Next) | `static/js/*.js` |
| CSS | Two stylesheets: `style.css` + `bloom-pro.css` | `layouts/pro.html` loads both |
| Auth | Server session + Werkzeug password hashes | `app.py` login/profile; no Firebase/Auth0/Supabase |
| CSRF | Custom middleware (`csrf.py`), not Flask-WTF | `init_csrf(app)` |
| File extract | pypdf, python-docx, python-pptx | `extract.py`, `requirements.txt` |
| AI | HTTP calls to OpenAI and/or Gemini via `urllib`; local fallbacks | `ai.py` |
| Tests | Smoke tests | `tests/test_smoke.py` |

**Not present:** React, Next.js, Vue, Firebase, Supabase, Redis, Celery, Docker (not required by app code), PostgreSQL (SQLite in use), TypeScript frontend.

### Application architecture

Monolithic Flask application:

1. **`app.py` (~2838 lines)** — routes, session auth, role gates, business logic, seeding, scoring, messaging, announcements, teacher/admin staff pages.
2. **`models.py`** — SQLAlchemy models.
3. **`ai.py`** — summarization + HOTS question generation (provider HTTP + fallbacks).
4. **`extract.py`** — text extraction from uploaded lesson files.
5. **`csrf.py`** — CSRF token issue/check for mutating methods.
6. **`templates/`** — Jinja pages; student pages mostly extend `layouts/pro.html`; teacher/admin pages use standalone HTML + `partials/staff_topbar.html`.
7. **`static/`** — CSS/JS/assets.
8. **`instance/`** — SQLite DB + upload files (runtime).

Request flow (typical student): browser → Flask route → `require_user` / role check → SQLAlchemy query → Jinja render (pro shell) → optional vanilla JS for filters/polling/setup.

### Main directories / files

```
app.py, models.py, ai.py, extract.py, csrf.py, requirements.txt, .env.example
templates/          # pages + layouts + partials
static/css/         # style.css, bloom-pro.css
static/js/          # pro-shell, practice_*, messages_*, announcements, topbar
tests/
docs/audit-screenshots/
instance/           # bloom.db, uploads (local runtime; not audited as source)
```

### Backend structure

- Single `Flask(__name__)` app with many `@app.route` handlers.
- Helpers for subjects, Bloom progress, today queue, announcement serialization, chat access, scoring, file save.
- Schema bootstrap via `ensure_schema()` (lightweight ALTER-style compatibility) + `db.create_all()` / `seed()` on startup path.
- Roles enforced with `@require_role("teacher"|"admin")` or inline `require_user()` + role redirects.

### Frontend structure

- **Student shell:** `layouts/pro.html` → sidebar (`pro_sidebar.html`) + topbar (`pro_topbar.html`) + flash + page blocks.
- **Staff shell:** each teacher/admin template is a full HTML document including `staff_topbar.html` (which itself mounts `pro_sidebar.html`).
- **Shared student components:** `partials/work_item_card.html` (Practice library + Results), message/announcement page-specific JS.
- Fonts: Google Fonts Fredoka + Inter loaded in pro layout.

### Database structure (models)

| Model | Purpose |
| --- | --- |
| `User` | email, name, role (`student`\|`teacher`\|`admin`), subject (teachers), password_hash, section |
| `Material` | lesson upload; status pending/approved/rejected; extracted_text |
| `Summary` | AI/fallback summary JSON sections for a material |
| `Assessment` | draft/published/closed; release flags; difficulty; attempt limits |
| `Question` | HOTS items on an assessment |
| `Attempt` | practice or assessment submission + review_json |
| `Announcement` / `AnnouncementRead` | teacher posts + per-user read tracking |
| `Setting` | key/value (e.g. max_upload_mb) |
| `QuizDraft` | in-progress practice draft questions |
| `Conversation` / `ChatMessage` | student↔teacher chat; `read_at` on messages |

Pilot subject set is hardcoded: English, Mathematics, Science (`SUBJECTS` in `app.py`).

### AI integration

- `summarize_material`, `generate_hots_questions` in `ai.py`.
- Provider selected via `AI_PROVIDER` / available keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`).
- Without keys: grounded **fallback** generators (app still works).
- Gemini requests append API key as query parameter (`generateContent?key=...`) — see Security.

### Authentication

- Form login at `/login` (email + password).
- Session stores user payload; permanent session with expiry injected for client timeout UI.
- Passwords: Werkzeug `generate_password_hash` / `check_password_hash`.
- Profile can change password (min 8 chars, confirm match).
- Logout: GET shows confirm page; POST clears session (prefetch-safe).
- Demo/pilot seed users exist when seeding is allowed (dev). Login UI can show pilot shortcuts when configured — **do not treat as production credentials**.

### User roles

| Role | Home redirect / primary surface |
| --- | --- |
| `student` | `/home` — pro student shell |
| `teacher` | `/teacher` — staff pages scoped to teacher’s subject |
| `admin` | `/admin` — staff pages for users/section/reports/settings |

### File handling / uploads

- Uploads stored under `instance/uploads` via `secure_filename`.
- Teacher materials upload → extract → summarize → approve path.
- Student “backup upload” on subject hub (pending teacher approval before practice unlock).
- Supported via extractors: PDF, DOCX, PPTX, TXT (per `extract.py` / deps).
- Admin settings surface documents upload limit notes (20 MB default setting seed).

### Important dependencies

From `requirements.txt` only:

- Flask ≥3.0.0  
- Flask-SQLAlchemy ≥3.1.0  
- pypdf ≥5.0.0  
- python-docx ≥1.1.0  
- python-pptx ≥1.0.0  

Stdlib also used heavily (`urllib`, `json`, `secrets`, etc.). AI providers are external HTTP APIs, not Python packages.

---

## 2. Complete Feature Inventory

Only features with real routes/templates/models are listed.

| Feature | User Role | Current Status | Main Route/Page | Backend Support | Database Support | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Login / session auth | All | Working | `/login` | Yes | `User` | Pilot shortcuts optional in dev |
| Logout (confirm) | All | Working | `/logout` | Yes | Session | GET confirm, POST clear |
| Student home / Today | Student | Working | `/home` | Yes | Attempts, Assessments, Materials, Announcements | Progress metric is score-average based |
| Subject hub | Student | Working | `/subjects/<slug>` | Yes | Materials, Assessments | Tabs for materials/practice/assessments |
| Student backup upload | Student | Working | POST subject hub | Yes | `Material` pending | Unlocks after teacher approve |
| Summary reader | Student | Working | `/subjects/.../summaries/...` | Yes | `Summary` | From approved materials |
| Practice library | Student | Working | `/practice` | Yes | Materials + Attempts | WorkItemCard list |
| Practice setup (difficulty/focus/count/types) | Student | Working | `/subjects/.../practice/...` | Yes | — | Count clamped 1–15 |
| Practice generate + take | Student | Working | `.../take` | Yes | `QuizDraft` | AI or fallback questions |
| Practice submit + result | Student | Working | `.../submit`, `/results/<id>` | Yes | `Attempt` | Scoring + review |
| Results history | Student | Working | `/results` | Yes | `Attempt` | Filters assessments/practice |
| Attempt review / feedback | Student (own), Teacher (subject), Admin | Working | `/results/<attempt_id>` | Yes | `Attempt`, release flags | Release gates for assessments |
| Assessment lobby | Student | Implemented | `/assessments/<slug>` | Yes | `Assessment` | Not populated in current demo DB (0 published) |
| Assessment take + submit | Student | Implemented | `/assessments/.../take`, `/submit` | Yes | `Attempt` | Session `assessment_started` on GET take |
| Announcements inbox | Student (also staff via context) | Working | `/announcements` | Yes | `Announcement`, `AnnouncementRead` | Search/filter/mark read |
| Messages inbox | Student, Teacher | Working | `/messages` | Yes | `Conversation`, `ChatMessage` | Subject-colored rows; filters |
| Message thread + send + poll | Student, Teacher | Working | `/messages/with/<id>` | Yes | Chat models | Student initiates; teacher replies |
| Profile / password change | Student (and users hitting `/profile`) | Working | `/profile` | Yes | `User` | Account + password form |
| Topbar prefs / settings panel | Authenticated | Partial UI | Topbar gear | Client prefs | Local/client | Not full account settings |
| Notification bell | Authenticated | UI present | Topbar | Announcement counts injected in places | Announcements | Behavior is panel/UI — not a separate notification entity |
| Teacher home dashboard | Teacher | Working | `/teacher` | Yes | Materials, Assessments | Attention queue + stats |
| Teacher materials upload/approve | Teacher | Working | `/teacher/materials` | Yes | `Material`, `Summary` | Subject-scoped |
| Teacher HOTS generate/review/publish | Teacher | Working | `/teacher/hots` | Yes | `Assessment`, `Question` | AI generation + draft/publish |
| Teacher monitor / release controls | Teacher | Working | `/teacher/monitor` | Yes | Assessment release flags, attempts | Release scores/answers/feedback |
| Teacher announce | Teacher | Working | `/teacher/announce` | Yes | `Announcement` | Subject-scoped posts |
| Admin home | Admin | Working | `/admin` | Yes | Counts | Thin dashboard |
| Admin user CSV import | Admin | Working | `/admin/users` | Yes | `User` | Temp passwords from CSV |
| Admin section view | Admin | Read-only info | `/admin/section` | Yes | User counts | No real section CRUD |
| Admin reports | Admin | Snapshot only | `/admin/reports` | Yes | Attempts/Assessments | Simple % participation |
| Admin settings | Admin | Read-only notes | `/admin/settings` | POST rejected as read-only | `Setting` exists | Env-driven AI/upload |

**Not implemented as first-class features (verified absent or stubbed):** multi-section school admin, parent accounts, real-time websocket chat, gradebook export, push notifications service, React SPA, cloud storage SDK.

---

## 3. User Flows

Legend: **Works** = code path exists and is coherent; **Questionable** = works but has side effects / weak UX; **Broken/Unavailable in demo** = cannot exercise with current data.

### A. Student login → dashboard

`/login` → POST credentials → session → `/home`  
**Works.** Flash may prompt password change. Screenshot: `01-login.png`, `02-home.png`.

### B. Student → subject → practice

Home subject card / Practice hub → `/subjects/<slug>` → approved material → practice setup → generate → take  
**Works** for Science Ecosystems in demo. Screenshots: `08-subject-hub.png`, `09-practice-setup.png`, `15-practice-take.png`, `03-practice.png`.

### C. Student → assessment → submit → result

Subject assessments / Today card → lobby → take (GET sets `assessment_started`) → submit → attempt review (release-gated)  
**Implemented in code.** **Unavailable in current demo DB** (0 published assessments at capture time). Flow itself is coherent; GET take mutates session — **Questionable**.

### D. Student → learning material → summary

Subject hub → summary link → `/subjects/.../summaries/...`  
**Works.** Screenshot: `10-summary.png`.

### E. Student → result → feedback

Results list → Review → `/results/<attempt_id>` shows review items / explanations for practice; assessments respect release flags  
**Works** for practice. Screenshot: `04-results.png`, `13-result-review.png`.

### F. Student → message teacher

Messages → teacher row → thread → POST body  
**Works.** Student can create conversation. Screenshot: `06-messages.png`, `12-messages-thread.png`.

### G. Teacher → receive/reply to message

Teacher `/messages` → open started thread → reply  
**Works** if student started conversation; teacher cannot initiate empty thread (by design). Screenshot: `21-teacher-messages.png`.

### H. Teacher → create/generate assessment → release

`/teacher/hots` generate → draft → publish; `/teacher/monitor` release toggles  
**Works** in code; teacher home showed 0 draft / 0 published in live capture — feature idle until used. Screenshots: `16-teacher-hots.png`, `17-teacher-monitor.png`.

### I. Teacher → review student submission

Monitor / results access via `can_view_attempt` (teacher subject match)  
**Works** for same-subject attempts. Depth of teacher-specific review UI is thinner than student result page (staff surfaces are form/panel oriented).

### J. Teacher → publish announcement

`/teacher/announce` POST → `Announcement`  
**Works.** Screenshot: `18-teacher-announce.png`.

### K. Student → receive/read announcement

`/announcements` list → select → mark read (POST)  
**Works.** Unread/read model exists. Screenshot: `05-announcements.png` (list populated; detail empty until select).

### L. Profile / settings

`/profile` password change; topbar gear opens prefs panel (theme/density-style client prefs via `topbar.js` / prefs boot)  
**Works for password.** “Settings” is **not** a full account-settings page — **Questionable labeling**.

### M. Other important flows discovered

1. **Student backup upload → teacher approve → practice unlock** — implemented.  
2. **Practice draft resume** via `QuizDraft` — implemented.  
3. **Admin CSV user import** — implemented.  
4. **Index `/`** — landing/redirect behavior for guests vs authed (simple entry).  

---

## 4. UI / Page Inventory

| Page | Role | Purpose | Template | Shared Layout | Visual Notes |
| --- | --- | --- | --- | --- | --- |
| Login | Guest | Sign in | `login.html` | Standalone | Light auth card; optional pilot shortcuts |
| Logout confirm | Auth | Confirm sign-out | `logout.html` | Standalone | Prefetch-safe |
| Student Home | Student | Today + subjects | `student_home.html` | `layouts/pro.html` | Strong pro shell; metric cards |
| Subject hub | Student | Materials / practice / assessments | `subject_hub.html` | pro | Subject-colored accents |
| Practice hub | Student | Practice library | `practice_hub.html` | pro | WorkItemCard |
| Practice setup | Student | Difficulty/focus/build | `practice_setup.html` | pro | Numbered steps; blue selection |
| Practice take | Student | Answer questions | `practice_take.html` | pro | Quiz UI |
| Practice/Assessment result | Student | Review | `practice_result.html` | pro | Feedback focus |
| Results history | Student | Past work | `results.html` | pro | WorkItemCard + filters |
| Assessment lobby | Student | Start assessment | `assessment_lobby.html` | pro | Not screenshot-captured (no published) |
| Assessment take | Student | Timed/attempt quiz | `assessment_take.html` | pro | Same |
| Summary | Student | Read summary | `summary_reader.html` | pro | Sectioned reading |
| Announcements | Student | Inbox + detail | `announcements.html` | pro | Split pane |
| Messages inbox | Student/Teacher | Conversations | `messages_inbox.html` | pro | Filters + subject borders |
| Messages thread | Student/Teacher | Chat | `messages_thread.html` | pro | Bubble thread + composer |
| Profile | Student | Account + password | `profile.html` | pro | Form-heavy |
| Teacher home | Teacher | Ops dashboard | `teacher_home.html` | staff_topbar + pro sidebar | Staff visual language |
| Teacher materials | Teacher | Upload/manage | via `staff_page` / materials route templates | staff | Form panels |
| Teacher HOTS | Teacher | Generate/publish | `teacher_hots.html` | staff | Generation UI |
| Teacher monitor | Teacher | Attempts + release | `teacher_monitor.html` | staff | Controls |
| Teacher announce | Teacher | Post news | staff announce route → staff template | staff | Form |
| Admin pages | Admin | Users/section/reports/settings | `staff_page.html` | staff | Thin content |
| Error | All | 500/error | `error.html` | Standalone | Generic |

### Multiple UI shells / design systems

**Confirmed dual shell:**

1. **Student Pro shell** — `layouts/pro.html` + `bloom-pro.css` + `style.css`.  
2. **Staff shell** — full-page templates + `staff_topbar.html` overlaying the same sidebar CSS tokens, but not extending `pro.html` the same way (duplicate HTML chrome, slightly different topbar utility set).

**Also present:**

- Legacy/parallel CSS in `style.css` (~74KB) alongside `bloom-pro.css` (~85KB).  
- Legacy-ish `partials/topbar.html` and `placeholder.html` (not primary student path).  
- Shared newer pattern: `work_item_card` + `--wic-*` tokens for Practice/Results.  
- Page-specific JS/CSS behaviors for announcements, messages, practice setup (not one component library).

---

## 5. Visual Design Audit

### Visual hierarchy

- Student pages generally lead with a **page hero** (kicker + title + subtitle), then a primary list/card region. Eye first hits hero, then list — good for orientation.
- Home “Today” CTA is appropriately emphasized (`Start now`). Secondary stat cards compete mildly with Today but remain secondary.
- Teacher home intro card is sparse; stats row carries more weight than narrative — more **ops dashboard** than teaching studio.

### Readability

- Body text contrast on light surfaces is generally acceptable (`--bloom-text` / `--pro-muted`).
- Muted secondary text is used heavily; usually readable, occasionally quiet on gray canvas.
- Sidebar active states are clear (blue pill on navy).
- Progress meters exist; fill depends on computed progress (Home subject bars can look empty when percent is 0).

### Color

- Palette tokens exist: Bloom blue primary, purple support, semantic success/warning/error, subject greens/ambers/purples.
- Student recent pages (Practice setup, Messages, Announcements, Results) show intentional subject-color semantics.
- Staff pages reuse blue/navy but with less subject storytelling.
- Excessive color is mostly avoided on redesigned student pages; Home subject cards use color purposefully.

### Layout

- Consistent card radius/shadow language on student pro pages.
- Some pages feel **card-dense** (Home stats + subject cards).
- Announcements split view leaves a large empty detail pane until selection — correct empty state, but looks sparse.
- Teacher home has noticeable empty vertical space in the intro card.

### Component consistency

| Component | Consistency |
| --- | --- |
| Sidebar nav | Strong across student; staff uses same sidebar partial |
| Primary buttons | Mostly Bloom blue — good |
| WorkItemCard | Shared Practice/Results — good architectural win |
| Selection cards (practice setup) | Coherent |
| Staff form panels | Different density/voice from student cards |
| Topbar icons | Student has bell/messages/avatar/gear; teacher topbar lighter |

### Student experience verdict

Feels closer to a **modern student learning app** on Home / Practice setup / Messages / Announcements than a pure admin tool. Teacher/admin surfaces still feel like **lightweight admin dashboards**. Overall product identity is improving on the student pro shell but not unified end-to-end.

---

## 6. Specific Bloom UI Review

### HOME (`02-home.png`)

- Engaging enough: greeting + Today CTA + subjects.
- Metrics: Progress / Today / Courses / Unread — useful at a glance.
- **Progress % is not curriculum completion** — it averages attempt scores (`bloom_progress`). Label “Progress … Across your subjects” can over-promise.
- Hero/Today is useful when items exist.
- My Subjects feels integrated via subject color and next-step lines.
- Some empty-bar whitespace when subjects are “Not started”.

### PRACTICE (`03-practice.png`, `09-practice-setup.png`, `15-practice-take.png`)

- Setup feels intentional and engaging (difficulty → focus → build → generate).
- Subject vs selection color separation is clear (Science green tags; blue selection/CTA).
- Primary action obvious: **Generate practice check**.
- Library progress clarity depends on WorkItemCard meter data quality.

### RESULTS (`04-results.png`, `13-result-review.png`)

- History is scannable; not spreadsheet-like.
- Review page carries feedback; status chips matter for correct/incorrect.
- With few results, page feels light (expected). Filter pills (All/Assessments/Practice) present.

### ANNOUNCEMENTS (`05-announcements.png`)

- Coherent blue header treatment + subject accent on list rows.
- Unread filter exists; unread visual weight depends on data/CSS state classes.
- Selection empty state is clear but large.
- Overall polished relative to older staff pages.

### MESSAGES (`06-messages.png`, `12-messages-thread.png`)

- Feels like a modern messaging list (search, filters, subject borders, previews).
- Conversation hierarchy clear (list → thread).
- Unread badges exist in nav/topbar when counts > 0.
- Empty conversation preview copy is handled (“No messages yet…”).
- Demo preview text includes inappropriate language in one thread — **content quality issue in demo data**, not UI chrome.
- Teacher cannot start cold threads — product rule, but can feel incomplete.

### PROFILE (`07-profile.png`)

- Organized as account + password more than a personalized learner profile.
- Visually consistent with pro shell, but not emotionally “profile”-rich (limited personalization beyond initials/name/section).

---

## 7. Functionality Audit

| Finding | Classification | Evidence |
| --- | --- | --- |
| Assessment lobby/take not exercisable in current DB (0 published) | CONFIRMED (data gap) | Teacher home published count 0; screenshot capture found no `/assessments/` links |
| `bloom_progress` = average of attempt score percents, not lesson completion | CONFIRMED | `bloom_progress()` in `app.py` |
| Admin settings POST does not save; flashes read-only | CONFIRMED | `admin_settings` |
| Admin section/reports are informational snapshots, not full admin tools | CONFIRMED | `admin_section`, `admin_reports` |
| Assessment take GET sets `session["assessment_started"]` | CONFIRMED | `assessment_take` |
| Opening message thread marks messages read (GET side effect) | CONFIRMED | `messages_thread` calls `mark_conversation_read` |
| Messages updates GET is read-only (marking separated) | CONFIRMED | comment + `messages_updates` |
| CSRF enforced on POST/PUT/PATCH/DELETE | CONFIRMED | `csrf.py` |
| Practice count clamped 1–15 | CONFIRMED | `clamp_practice_count` |
| AI fallback when no API keys | CONFIRMED | `ai.py` |
| Fake/static home metrics beyond computed fields | POSSIBLE | Courses=3 is pilot constant; Progress semantics misleading |
| Notification bell implies a notification center | POSSIBLE | Topbar UI; no dedicated Notification model |
| Settings gear ≠ Profile settings page | CONFIRMED (UX mismatch) | gear → prefs panel; password on `/profile` |
| Duplicate screenshot/filename noise in docs folder earlier | N/A (audit artifact) | cleaned during audit capture |
| Practice autosave reliability under all browsers | NOT ENOUGH EVIDENCE | `practice_take.js` exists; not exhaustively runtime-tested here |
| Race conditions in chat polling | NOT ENOUGH EVIDENCE | poll endpoint exists; not load-tested |

Broken buttons/links: no systematic dead-link crawl was completed beyond primary student/teacher routes used for screenshots. Primary student nav destinations resolved.

---

## 8. Security / Reliability

| Topic | Status | Notes |
| --- | --- | --- |
| Authentication | Generally sound | Hashed passwords, session auth |
| Authorization | Role gates present | Teacher subject scoping; chat partner checks; attempt view checks |
| IDOR on attempts | Mitigated | `can_view_attempt` |
| IDOR on chat | Mitigated | `allowed_chat_partner`, `can_access_conversation` |
| CSRF | Present | Custom token; mutating methods blocked if missing |
| Session | Permanent session + client expiry hint | Production requires strong `SECRET_KEY` |
| Secret keys | Dev fallback exists | Production raises if missing/weak |
| Debug | FLASK_DEBUG defaults on in non-production | Expected for local |
| File uploads | `secure_filename` + size setting | Edge cases (malware, zip bombs) not deeply hardened — typical for pilot |
| Gemini API key in query string | CONFIRMED risk | `ai.py` URL `?key=` |
| API keys in browser | Not observed in templates | Server-side env |
| GET mutating state | CONFIRMED | assessment_started; mark conversation read on thread GET |
| Error leakage | Generic 500 template | Better than stack traces in prod if debug off |
| Demo credentials | Seeded in dev | Must not ship enabled in production (`BLOOM_SEED_DEMO`, `BLOOM_SHOW_PILOTS`) |
| DB reliability | SQLite single-file | Fine for pilot; concurrency limits |
| Migrations | `ensure_schema` + create_all | Not Alembic; workable but fragile for evolved prod |
| Input validation | Partial | Message length 2000; password min 8; file type via extractors |

**P0-oriented security notes for reviewers:** Gemini key-in-query; ensure production seed/pilots off; treat GET side-effects carefully for prefetch/logging; upload scanning is minimal.

---

## 9. Accessibility + Responsiveness

| Area | Observation |
| --- | --- |
| Skip link | Present in pro layout |
| Focus | CSS `--focus` / `--bloom-focus` tokens exist |
| Labels | Many forms labeled; staff dynamic forms vary |
| Keyboard | Not fully audited end-to-end; custom cards/filters may need extra key handling |
| Contrast | Generally OK on pro light theme; muted text is the risk zone |
| Touch targets | Primary CTAs large; icon-only topbar controls are smaller |
| Screen readers | Semantic landmarks partially present (`main`); some icon buttons need verified accessible names |
| Responsive | Pro sidebar collapses via JS/backdrop; staff pages less verified on small screens |
| Mobile nav | Sidebar drawer pattern exists; not screenshot-tested on phone viewport in this audit |
| Overflow | No major horizontal overflow seen at 1280×800 captures |

---

## 10. Code Quality

| Issue | Evidence |
| --- | --- |
| Very large `app.py` (~2838 lines) | Routes + domain logic colocated |
| Dual CSS systems | `style.css` + `bloom-pro.css` both loaded |
| Dual layout approaches | `layouts/pro.html` vs staff full pages |
| Shared WorkItemCard is a positive consolidation | `partials/work_item_card.html` |
| Hardcoded pilot subjects / section strings | `SUBJECTS`, default section |
| Inconsistent feature depth admin vs student | Admin mostly read-only panels |
| Dead/legacy templates | `placeholder.html`, alternate `topbar.html` still in tree |
| AI + extract reasonably separated | `ai.py`, `extract.py` |
| CSRF module clean | `csrf.py` |

**Rewrite not recommended.** Architecture is a coherent Flask monolith suitable for the Grade 7 pilot. Priority should be modularization and UI shell unification, not a greenfield rewrite.

---

## 11. Current Problems — Prioritized

### P0 — Critical / security / data integrity

**Issue:** Gemini API key passed as URL query parameter  
**Where:** `ai.py` Gemini request builder  
**Evidence:** `generateContent?key={key}`  
**Why it matters:** Keys in URLs leak via logs, proxies, referrers  
**Affected users:** Operators / all users if key revoked/quota abused  
**Suggested direction:** Use header-based auth if provider supports; never log full URL  
**Estimated effort:** Low–Medium  

**Issue:** Production misconfiguration risk (debug, seed pilots, weak SECRET_KEY)  
**Where:** `.env.example`, `app.py` startup  
**Evidence:** Dev fallbacks and seed gates exist; safe if env correct, dangerous if not  
**Why it matters:** Account takeover / demo password exposure in real deployments  
**Affected users:** All  
**Suggested direction:** Deployment checklist; fail closed (already partly present)  
**Estimated effort:** Low  

### P1 — Major functionality or UX

**Issue:** Home “Progress %” semantics misleading  
**Where:** `bloom_progress`, Home subject cards  
**Evidence:** Averages attempt scores; 0% with “keep practicing” copy  
**Why it matters:** Students/teachers misread mastery vs completion  
**Affected users:** Students, teachers interpreting dashboards  
**Suggested direction:** Relabel metric or compute true completion against approved materials/assessments  
**Estimated effort:** Medium  

**Issue:** Assessment end-to-end hard to validate in current demo data; release-gated review complexity  
**Where:** Assessment publish + student take + monitor release  
**Evidence:** 0 published in live DB; code path exists  
**Why it matters:** Core product promise (HOTS assessments) may look “missing”  
**Affected users:** Students, teachers, reviewers  
**Suggested direction:** Seed one published assessment for demos; UX polish on release states  
**Estimated effort:** Low (seed) / Medium (UX)  

**Issue:** Dual UI shells (student pro vs staff) fragment consistency  
**Where:** templates + CSS  
**Evidence:** inventory + screenshots  
**Why it matters:** Teachers see a different product quality bar  
**Affected users:** Teachers, admins  
**Suggested direction:** Migrate staff pages onto `layouts/pro.html` patterns  
**Estimated effort:** High  

**Issue:** GET requests with state changes (assessment started; mark messages read)  
**Where:** `assessment_take`, `messages_thread`  
**Evidence:** code  
**Why it matters:** Prefetch/back/refresh oddities; harder reasoning about state  
**Affected users:** Students/teachers  
**Suggested direction:** Explicit POST “Start” / mark-read actions  
**Estimated effort:** Medium  

### P2 — Significant polish / usability

**Issue:** Profile feels like settings, not learner identity  
**Where:** `profile.html`  
**Evidence:** screenshot + template purpose  
**Suggested direction:** Add learning snapshot; keep password secondary  
**Effort:** Medium  

**Issue:** Announcements detail empty until click — large blank pane  
**Where:** announcements UI  
**Evidence:** `05-announcements.png`  
**Suggested direction:** Auto-select newest unread  
**Effort:** Low  

**Issue:** Notification bell affordance vs actual notifications model  
**Where:** topbar  
**Evidence:** no Notification model; announcement counts elsewhere  
**Suggested direction:** Wire bell to announcements unread or remove badge ambiguity  
**Effort:** Low–Medium  

**Issue:** Demo chat content quality  
**Where:** seeded/demo messages  
**Evidence:** inbox preview text inappropriate  
**Suggested direction:** Replace demo fixtures with school-appropriate samples  
**Effort:** Low  

**Issue:** Admin tools thin / read-only settings  
**Where:** `/admin/*`  
**Evidence:** code  
**Suggested direction:** Either build real controls or label “Pilot snapshots” more loudly in UI  
**Effort:** Medium  

### P3 — Minor

- Legacy `placeholder.html` / unused topbar partial cleanup  
- Reduce CSS duplication between `style.css` and `bloom-pro.css`  
- Mobile viewport screenshot pass  
- Empty-state illustrations consistency  

---

## 12. What Should Not Be Changed

Verified working pieces worth preserving:

1. **Session authentication + Werkzeug password hashing + CSRF middleware** — solid baseline.  
2. **Student pro shell navigation** (Home / Practice / Results / Announcements / Messages / Profile) — coherent IA.  
3. **Practice setup flow** (difficulty, HOTS focus, 1–15 count, types, generate CTA) — clear and intentional.  
4. **WorkItemCard shared component** for Practice library + Results — correct consolidation direction.  
5. **Subject color semantics** (English purple, Math amber, Science green) — meaningful, not decorative noise.  
6. **Messaging model** with student-initiated conversations, `read_at`, polling updates endpoint, partner checks.  
7. **Announcement read tracking** (`AnnouncementRead` unique constraint).  
8. **Teacher HOTS generate → draft/publish + Monitor release flags** (`release_scores` / `release_answers` / `release_feedback`) — important academic control.  
9. **Attempt review release gating** for assessments.  
10. **AI module with fallbacks** so classrooms work without keys.  
11. **File extract pipeline** for teacher materials + summaries.  
12. **Logout GET confirm / POST clear** prefetch-safe pattern.  
13. **QuizDraft** for practice continuity.  

---

## 13. Design System Audit

### What exists

`bloom-pro.css` defines a real token layer:

- `--bloom-*` brand/semantic colors  
- `--pro-*` shell tokens (sidebar, canvas, shadows, text)  
- Focus ring tokens  
- Subject-oriented accents used across student pages  
- Work item tokens (`--wic-*`) for shared cards  

Typography: Inter + Fredoka via Google Fonts in pro layout.

### What is fragmented

- **Two CSS files** both active → overlap and override risk.  
- **Staff pages** don’t fully share student page header/hero patterns.  
- Buttons/cards/inputs are CSS-class based, not a documented component library.  
- Icons are mostly inline SVG in partials — inconsistent sizing possible.  
- Status colors exist, but status chips vary by page.  
- Spacing feels token-ish but not a strict spacing scale documented in one place.

### Verdict

Bloom has an **emerging design system** (pro tokens + recent page redesigns), not a finished single source of truth. Student-facing redesigned pages are the most coherent. Staff + legacy CSS are the fragmentation zones.

**Do not invent a new design system in code yet** — document and extend the existing `--bloom` / `--pro` / `--wic` tokens.

---

## 14. Screenshot Capture

Live captures from the running app (Chromium via Playwright), stored in:

`docs/audit-screenshots/`

| File | Page / state |
| --- | --- |
| `01-login.png` | Login |
| `02-home.png` | Student Home (populated Today + subjects) |
| `03-practice.png` | Practice library |
| `04-results.png` | Results history (1 practice result) |
| `05-announcements.png` | Announcements list + empty detail |
| `06-messages.png` | Messages inbox (3 conversations) |
| `07-profile.png` | Profile |
| `08-subject-hub.png` | Science subject hub |
| `09-practice-setup.png` | Practice setup (Medium / Mixed / 3) |
| `10-summary.png` | Summary reader |
| `12-messages-thread.png` | Active conversation |
| `13-result-review.png` | Practice result review |
| `14-teacher-home.png` | Teacher home |
| `15-practice-take.png` | Practice take (when draft route available / related capture) |
| `16-teacher-hots.png` | Teacher HOTS |
| `17-teacher-monitor.png` | Teacher monitor |
| `18-teacher-announce.png` | Teacher announce |
| `19-teacher-materials.png` | Teacher materials |
| `21-teacher-messages.png` | Teacher messages |
| `22-admin-home.png` | Admin home |

### Gaps (explicit)

- **Assessment lobby / assessment take / assessment result** — not captured; current DB had **no published assessments**.  
- Dedicated **empty-state** screenshots for Practice/Results/Messages not separately filed (some empty regions appear inside populated pages, e.g. announcements detail).  
- **Error state** pages not captured.  
- **Mobile** viewports not captured.  

Accounts used: existing local demo/pilot users already present in the project seed — credentials intentionally omitted from this report.

---

## 15. Final Summary

### A. Current system architecture

Flask + Jinja + SQLite monolith with session auth, custom CSRF, server-side AI HTTP integration, and a student “pro” UI shell plus separate staff pages.

### B. Current feature completeness

**Strong:** student learning loop (subjects → summaries → practice setup/take → results), announcements, messaging, teacher materials/HOTS/monitor/announce, basic admin user import.  
**Thin:** admin section/settings/reports, notification center, rich profile.  
**Data-dependent gap:** published assessments empty in the audited local DB.

### C. Major functional problems

Misleading progress metric; assessment demo gap; GET side-effects; admin read-only “settings”; notification affordance ambiguity.

### D. Major visual problems

Dual shells (student vs staff); dual CSS; some sparse empty panes; teacher intro card emptiness; profile not visually “learner identity.”

### E. Major UX problems

Progress labeling; settings gear vs profile password; announcements requiring manual select; teacher messaging initiation rules may confuse; assessment release states need clear student messaging (code exists, demo sparse).

### F. Major technical/security problems

Gemini API key in query string; production env discipline for seeds/debug/SECRET_KEY; SQLite/`ensure_schema` vs real migrations for scale; large single `app.py`.

### G. Design-system problems

Emerging tokens (`--bloom`, `--pro`, `--wic`) but fragmented application across staff/legacy CSS; no single component catalog.

### H. Strong parts worth preserving

Auth/CSRF baseline; student IA; practice setup; WorkItemCard; subject color language; chat + announcement read models; teacher release controls; AI fallbacks; extract/summary pipeline.

### I. Recommended improvement order

1. **Secure & harden** — Gemini key handling; production config checklist; review GET mutations.  
2. **Make core academic loop demo-complete** — publish sample assessment; clarify release/result UX.  
3. **Fix trust metrics** — redefine/relabel Home progress.  
4. **Unify shells** — bring teacher/admin onto pro layout patterns without rewriting domain logic.  
5. **Polish student moments** — announcements auto-select, profile richness, notification clarity, demo content cleanup.  
6. **Code health** — split `app.py`, consolidate CSS tokens, remove dead templates.  

---

*End of audit. No application code was modified to produce this report (screenshot folder cleanup only under `docs/audit-screenshots/`).*
