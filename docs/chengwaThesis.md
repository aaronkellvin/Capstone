# chengwaThesis — Chapters I–III (aligned)

**Use this file for Chapters 1–3.** Do not mix it with `IT7FINAL-revised.md` (old draft) or `IT7-Chapter4-5.md` (Chapters 4–5).

**Study title:** AI-Powered Smart Study Assistant for HOTS-Based Assessment Generation and Learning Support  
**Prototype name:** Bloom  
**Researchers:** Esguerra, Patrick Carlos P. · Lamadrid, Isaiah Matthew C. · Quilitis, Marvic Mat M.  
**School:** Colegio de San Juan de Letran Calamba · BS Information Technology · May 2026

**What this file aligns**
- The working Bloom prototype (Flask, SQLite, Gemini, roles, messages, practice vs publish)
- Evaluation instruments: ISO/IEC 25010:2023, ISO/IEC 25019:2023, ISO/IEC 25040:2024, adapted SUS
- Handbook testing levels used in Chapter IV: unit, integration, system, UAT

Copy Chapters I–III from here into the official thesis Word file. Then paste Chapters IV–V from `docs/IT7-Chapter4-5.docx`.

---

# CHAPTER I
# INTRODUCTION

The cultivation of Higher-Order Thinking Skills (HOTS) has become a major priority in modern junior high education. Learners are expected to progress beyond memorization and recall, moving toward deeper processes such as analysis, evaluation, and creative problem-solving. Despite this emphasis, many classroom assessments still lean heavily on lower-level tasks due to lack of teacher training, time constraints, and the absence of structured support systems.

At Letran Calamba Junior High School, teachers must design assessments that align with curriculum standards while encouraging higher-level thinking. Creating HOTS-based questions manually is demanding and time-intensive, often resulting in inconsistent quality and a reliance on recall-type items. Artificial intelligence tools can assist with content generation, but most produce generic outputs that are not grounded in the school’s uploaded lessons and are not constrained to Bloom’s Taxonomy levels of Analyze, Evaluate, and Create.

This study therefore developed **Bloom**, an AI-powered smart study assistant for curriculum-aligned HOTS assessment generation and student learning support. Bloom uses large language model APIs (primarily Google Gemini, with optional OpenAI) and prompt engineering so that summaries and items are drawn from uploaded lesson text. Teachers review and publish assessments. Students use approved lessons for summaries, guided practice, published assessments, feedback, announcements, and messages. System quality and quality in use are evaluated with ISO/IEC 25010:2023 and ISO/IEC 25019:2023 under the ISO/IEC 25040:2024 evaluation process. Usability is also measured with an adapted System Usability Scale (SUS).

## Research Problem

### Central Question
How can an intelligent, curriculum-aligned system assist teachers and students at Colegio de San Juan de Letran Calamba in developing and applying Higher-Order Thinking Skills (HOTS) through validated assessments and student-centered learning support?

### Corollary Questions
1. What challenges do teachers face in creating curriculum-aligned HOTS-based assessments?
2. Why do existing AI content generation tools fail to ensure alignment with competencies, learning outcomes, and higher-order cognitive levels?
3. How do students experience limited access to interactive resources that strengthen higher-order thinking beyond classroom instruction?
4. In what ways can an AI-powered study assistant help teachers with meaningful learning support?

## Research Objectives

### General Objective
To design, develop, and evaluate a system that supports Higher-Order Thinking Skills (HOTS) among junior high school students at Colegio de San Juan de Letran Calamba through curriculum-aligned assessment generation, validation mechanisms, and student-centered learning support.

### Specific Objectives
1. Develop an AI-driven study assistant (**Bloom**) that produces HOTS-focused items aligned with the Junior High School curriculum of Letran Calamba, using prompt engineering and Bloom’s Taxonomy (Analyze, Evaluate, Create).
2. Implement validation mechanisms: prompt constraints, Bloom-level tagging, teacher approval of lesson materials, and teacher review before **published assessments** reach the class.
3. Develop a student module that provides structured summaries, guided HOTS practice, published assessments, immediate feedback, announcements, and messages with the subject teacher.
4. Evaluate Bloom among teachers and students using **ISO/IEC 25010:2023** (product quality), **ISO/IEC 25019:2023** (quality in use), **ISO/IEC 25040:2024** (evaluation process), and an **adapted SUS** questionnaire.

## Scope and Delimitations

This study covers the design, development, and evaluation of Bloom for the Junior High School curriculum of Colegio de San Juan de Letran Calamba. The pilot is limited to **English, Mathematics, and Science** for **one Grade 7 section**. HOTS generation is limited to **Analyze, Evaluate, and Create**. The study does **not** train or fine-tune a custom machine learning model. It uses external LLM APIs (Gemini primary; OpenAI optional) and a local fallback when an API is unavailable.

The student module is supplementary practice and review. It does not replace formal classroom instruction or official school examinations.

Teacher control is split as follows, matching the implemented system:
- **Lesson materials** (teacher uploads and student backup uploads) must be **approved** before students study or practice from them.
- **Published assessments** must be reviewed, edited if needed, and published by the teacher. Release of scores, answers, and feedback is also teacher-controlled.
- **Student practice** generates HOTS items from an **already-approved lesson** for drill. Those practice items are not edited by the teacher one by one.

The study is a prototype evaluation among selected teachers and students. It does not include full institutional deployment or long-term measurement of academic achievement.

## Significance of the Study

**Teachers.** Bloom reduces the time needed to draft HOTS items from a specific lesson, while leaving professional judgment with the teacher.

**Students.** Bloom gives structured summaries, HOTS practice, and feedback beyond recitation, using only approved materials.

**The institution.** The prototype shows how a school-email, role-based system can support Grade 7 English, Mathematics, and Science without replacing existing assessment policy.

**Educational technology and future researchers.** The work documents a grounded-prompt plus teacher-review pattern, and an ISO 25010:2023 / 25019:2023 / 25040:2024 plus SUS evaluation pack that later studies can reuse.

## Definition of Terms

**Bloom (AI-Powered Smart Study Assistant).** The web-based prototype that generates HOTS-based assessments and provides learning support for junior high teachers and students at Letran Calamba.

**Assessment Design.** Planning and constructing tests or tasks that measure learning outcomes at targeted cognitive levels.

**Bloom’s Taxonomy.** A framework of cognitive levels from remember to create. This study uses **Analyze, Evaluate, and Create**.

**Curriculum-Aligned.** Content matched to the school’s subjects and to **uploaded lesson files**, not to generic internet knowledge.

**Decision-Support Tool.** A system that drafts content for teachers and does not replace their judgment.

**HOTS (Higher-Order Thinking Skills).** Cognitive skills beyond memorization: analyzing, evaluating, and creating.

**Prompt Engineering.** Writing instructions so the AI model stays on the lesson text and on the intended Bloom level.

**Published Assessment.** A teacher-reviewed set of HOTS items that the teacher publishes for the class. Distinct from **practice**.

**Practice.** Student-generated HOTS drill from an approved lesson. Items are not individually teacher-edited.

**Gemini API.** Google’s generative AI interface used as Bloom’s primary content-generation service.

**Validation / Filtering.** Prompt rules, Bloom tags, material approval, and teacher review/publish of assessments so ungrounded or recall-heavy class tests are reduced.

**ISO/IEC 25010:2023.** SQuaRE **product quality** model (nine characteristics) used on the teacher and student **evaluation forms**.

**ISO/IEC 25019:2023.** SQuaRE **quality-in-use** model (three characteristics: beneficialness, freedom from risk, acceptability) used on the same evaluation forms.

**ISO/IEC 25040:2024.** SQuaRE **quality evaluation framework** (define, design, plan, execute, conclude) used to structure UAT.

**Adapted SUS.** Ten-item System Usability Scale, worded for Bloom, used on the teacher and student **questionnaires** (not on the ISO evaluation forms).

---

# CHAPTER II
# REVIEW OF RELATED LITERATURE

This chapter reviews HOTS and Bloom’s Taxonomy, limits of generic AI for classroom items, student practice beyond the lecture, software quality evaluation under the current SQuaRE models, and the gap that Bloom addresses. Sources from the original manuscript (pages 11–21 of IT7FINAL) may be merged here if the adviser requires those exact citations; the models below replace ISO/IEC 25010:2011 as the evaluation base.

## Higher-Order Thinking and Bloom’s Taxonomy

Higher-order thinking is commonly described as going beyond recall to analysis, evaluation, and creation (Anderson & Krathwohl, 2001; Bloom, 1956). Junior high assessments that stay on Remember and Understand do not give learners enough practice in those upper levels. Teachers are expected to write items that match competencies and cognitive level, but item writing is slow and uneven when done entirely by hand.

This study therefore treats **Analyze, Evaluate, and Create** as the operational definition of HOTS inside Bloom. Lower levels are not the generation target.

## AI-Generated Assessment and the Alignment Problem

Generative AI can draft questions quickly. Without constraints, it often (a) uses facts that were never in the lesson, (b) writes recall items labeled as “critical thinking,” or (c) ignores the teacher’s curriculum file. For a school system, that is a validity problem: the item no longer measures the taught lesson.

Related systems and studies on AI tutors and quiz generators show speed gains but weak grounding unless the prompt is bound to a source text and a taxonomy. Bloom’s design choice follows that lesson: **summarize and generate only from extracted lesson text**, keep difficulty from changing the Bloom level, and require a **teacher publish step** for class assessments.

## Student Access to HOTS Practice

Practice that only happens during recitation leaves little time for analysis and creation. A student module that offers a short summary, a configurable practice set, a published test, and a way to ask the teacher is consistent with supplementary e-learning: it extends the lesson without replacing the teacher. Messages and announcements in Bloom are part of that support, not extra “social” features disconnected from the study.

## Software Quality Evaluation: SQuaRE 2023–2024

Older IT theses often used **ISO/IEC 25010:2011**, which put product quality and quality in use in one document. That edition is superseded for this study.

- **ISO/IEC 25010:2023** is the **product quality** model: functional suitability, performance efficiency, compatibility, interaction capability (formerly usability as a product attribute), reliability, security, maintainability, flexibility (formerly portability), and **safety**.
- **ISO/IEC 25019:2023** is the **quality-in-use** model: beneficialness, freedom from risk, and acceptability.
- **ISO/IEC 25040:2024** is the **evaluation process** (define, design, plan, execute, conclude). It does not add extra Likert characteristics; it structures how UAT is run.

Usability as an *outcome of use* is covered in 25019 (beneficialness / usability). Ease of learning and operating the interface is also scored under 25010 interaction capability. To avoid mixing those two ideas in one instrument, this study uses:
- **Evaluation forms** = all 25010 and 25019 characteristics (system quality and use in context);
- **Questionnaires** = adapted SUS plus open questions (usability experience and HOTS/curriculum comments).

Brooke’s SUS remains a short, widely used usability index and is treated as a complement to SQuaRE, not a replacement for it (Brooke, 1996).

## Synthesis

The literature supports four needs: HOTS items at Analyze–Evaluate–Create, grounding in the actual lesson, a student practice loop, and a current quality model for evaluation. Generic chat tools do not meet the first two. ISO 25010:2011 is not the current model. Bloom is positioned in that gap: a school-role web prototype with grounded generation, teacher publish for assessments, approved-lesson practice for students, and UAT under 25010:2023, 25019:2023, and 25040:2024 plus adapted SUS.

---

# CHAPTER III
# METHODOLOGY

This chapter describes the design, development, and evaluation of Bloom at Letran Calamba Junior High School. Evaluation follows ISO/IEC 25040:2024. Product quality uses ISO/IEC 25010:2023. Quality in use uses ISO/IEC 25019:2023. Usability experience uses an adapted SUS.

## Research Design

The study uses a **developmental design** because the main output is a working software prototype. Development follows an iterative **Agile** cycle (requirements, design, development, testing, deployment, maintenance). Evaluation is **mixed-methods**:
- **Quantitative:** ISO Likert means (evaluation forms) and SUS scores (questionnaires);
- **Qualitative:** open questions on the questionnaires and observations during the pilot.

The study does **not** use a pre-test/post-test of academic achievement as a required instrument. Learning gain is outside the prototype’s claim.

## Population of the Study

Participants are selected teachers and Grade 7 students of Letran Calamba Junior High School during Academic Year 2025–2026.

- **Teachers** — faculty in English, Mathematics, or Science who prepare assessments. They use the teacher module and complete the **Teacher Evaluation Form** (ISO 25010 and 25019) and the **Teacher Questionnaire** (profile, SUS, open questions).
- **Students** — learners in the Grade 7 pilot section. They use the student module and complete the **Student Evaluation Form** and the **Student Questionnaire**.

## Sampling Design

**Purposive sampling** is used. Participants must be the teachers and students assigned to the Grade 7 pilot subjects. They are the only users who can judge Bloom in its intended context of use (ISO 25040).

## Data Collection Method

1. **ISO evaluation forms** after the participant uses Bloom (product quality and quality in use; 12 Likert items).
2. **Questionnaires** after the same session (respondent profile, 10 adapted SUS items, 3 open questions). The ISO form and the questionnaire are separate so items are not repeated.
3. **Automated functional tests** (unit, integration, system) recorded from `tests/test_smoke.py`.
4. **Observation** during laboratory or classroom pilot sessions (notes only; not a second survey).

Structured interviews and a HOTS item-quality rubric are **not** required UAT instruments in this aligned design. If interviews were used only during early requirements, they stay in the requirements phase of the SDLC, not in Chapter IV UAT tables.

## Software Development Lifecycle (SDLC)

Bloom follows **Agile SDLC**.

| Phase | Application in this study |
|---|---|
| Requirements | Role needs (student, teacher, admin); HOTS drafting load; school-email login |
| Design | UI, SQLite schema, prompt templates, Bloom tags, approval/publish rules |
| Development | Flask modules; `extract.py`; `ai.py`; practice, assessment, messages, announcements |
| Testing | Unit, integration, system, then UAT (ISO + SUS) |
| Deployment | Local/prototype server for the Grade 7 pilot |
| Maintenance | API settings, model name updates, UI fixes from feedback |

## Context Flow Diagram

External entities:
1. **Teacher** — uploads and approves materials, generates and reviews HOTS items, publishes assessments, posts announcements, monitors results, replies to messages.
2. **Student** — reads approved summaries, takes practice and published assessments, views results, reads announcements, messages the teacher, manages profile.
3. **Admin** — manages users, section view, reports snapshot, and settings (for example upload limits).
4. **AI service (Gemini / optional OpenAI)** — returns summaries and HOTS questions from prompts grounded in extracted lesson text.

*(Figure 1. Context Flow Diagram of Bloom — redraw captions to match the list above.)*

## Data Flow Diagram

Level-1 processes:
1. **Input** — login, file upload (PDF, DOCX, PPTX, TXT), practice/assessment parameters, messages.
2. **Text extraction** — `extract.py` converts the lesson file to text.
3. **Prompt generation** — Bloom-guided prompts from lesson text and user parameters.
4. **AI generation** — Gemini or OpenAI, with local fallback if the API fails.
5. **Validation** — material pending/approved/rejected; teacher review and publish of assessments; CSRF and role checks.
6. **Output** — summaries, practice, published assessments, scores/feedback (when released), announcements, messages.

*(Figure 2. Data Flow Diagram of Bloom.)*

## Use Case Diagram

### Student
- Sign in / sign out
- View subject hub (English, Mathematics, Science)
- Read AI-generated summaries from **approved** materials
- Upload a backup file (stays pending until the teacher deploys it)
- Configure and take HOTS **practice** (difficulty, Bloom focus, count, types)
- Take **published** assessments
- View results and feedback
- Read announcements
- Message the subject teacher
- Update profile (photo, password)

### Teacher
- Sign in / sign out
- Upload lesson materials and approve or reject student backups
- Generate lesson summaries
- Generate HOTS questions (Analyze / Evaluate / Create / Mixed)
- Build, edit, publish, or close assessments
- Set release of scores, answers, and feedback
- Post subject announcements
- Monitor attempts and section performance
- Message students (within the conversation model)

### Admin
- Sign in / sign out
- Manage user accounts (including school-email enrollment for the pilot)
- View section snapshot
- View reports snapshot
- Manage settings (for example upload limit)

*(Figure 3. Use Case Diagram of Bloom — include Student, Teacher, and Admin.)*

## System Architecture

Bloom is a three-layer web application.

1. **Presentation** — Flask Jinja2 templates and CSS/JS (student shell, teacher/admin staff pages).
2. **Application** — Flask routes in `app.py`:
   - session authentication and role gates
   - CSRF protection (`csrf.py`)
   - upload and text extraction (`extract.py`)
   - summarization and HOTS generation (`ai.py`)
   - practice drafts, scoring, assessments, announcements, messages, monitoring
3. **Data** — SQLite (`instance/bloom.db`) via Flask-SQLAlchemy (`models.py`)
4. **External AI** — Gemini API (primary) and optional OpenAI API via environment variables

*(Figure 4. System Architecture of Bloom.)*

## Flowchart

**Teacher:** login → upload/approve materials → generate summary/HOTS → review/edit → publish assessment → set release flags → monitor results → (optional) announce / message.

**Student:** login → subject hub → read approved summary → practice setup/take **or** published assessment → submit → view results → (optional) announcements / messages / profile.

*(Figures 5–6. Teacher and student flowcharts of Bloom.)*

## Entity Relationship Diagram

Entities implemented in Bloom:

| Entity | Notes |
|---|---|
| **User** | email, name, role (`student` / `teacher` / `admin`), subject (teachers), password_hash, section, avatar_filename |
| **Material** | slug, title, subject, owner, source (`teacher` / `student`), status (`pending` / `approved` / `rejected`), extracted_text |
| **Summary** | intro and sections_json for one material |
| **Assessment** | draft / published / closed; attempt limit; release_scores, release_answers, release_feedback; difficulty |
| **Question** | bloom (Analyze / Evaluate / Create), qtype (mcq / essay / problem), prompt, options, answer, explanation, citation |
| **Attempt** | kind (`assessment` / `practice`), scores, review_json |
| **QuizDraft** | in-progress practice question set |
| **Announcement** | subject, title, body, teacher |
| **AnnouncementRead** | which user has read which announcement |
| **Conversation** | unique student–teacher pair |
| **ChatMessage** | body, sender, read_at |
| **Setting** | key/value (for example max upload size) |

Relationships (simplified):
- User 1—N Material, Assessment, Attempt, Announcement
- User (student) 1—N Conversation; User (teacher) 1—N Conversation
- Conversation 1—N ChatMessage
- Material 1—1 Summary
- Assessment 1—N Question, Attempt
- Announcement 1—N AnnouncementRead

*(Figure 7. Entity Relationship Diagram of Bloom — include Conversation, ChatMessage, and AnnouncementRead.)*

## Materials

### Software
- Python 3, Flask, Flask-SQLAlchemy, SQLite (`bloom.db`)
- Google Gemini API (primary); OpenAI API (optional)
- pypdf, python-docx, python-pptx for extraction
- Visual Studio Code / Cursor; Git / GitHub
- Automated tests: Python `unittest` (`tests/test_smoke.py`)
- Configuration: `.env` (`GEMINI_API_KEY`, optional `OPENAI_API_KEY`)

### Hardware
- Development PC; prototype server; school PCs, laptops, tablets, or phones with a modern browser

## Data

1. ISO evaluation-form ratings (teachers and students)
2. Questionnaire data (profile, SUS, open answers)
3. Automated test results
4. Prototype logs of summaries, questions, and attempts in SQLite (aggregates only in the paper)

Human data are reported in aggregates. Names on forms are optional.

## Ethics on the Use of Data

Participation is voluntary. Minors in Grade 7 require institutional permission and the school’s data-privacy process (school-email enrollment is limited to the named pilot section). Responses are used only for this capstone. No full student-record dump is requested. Informed consent / school clearance procedures of Letran Calamba apply.

## Research Instruments

| Instrument | Who | What it measures | Standard |
|---|---|---|---|
| Teacher Evaluation Form | Teachers | 9 product-quality + 3 quality-in-use items | ISO/IEC 25010:2023, 25019:2023, 25040:2024 |
| Student Evaluation Form | Students | Same 12 characteristics, student wording | Same |
| Teacher Questionnaire | Teachers | Profile, 10 SUS items, 3 open questions | Adapted SUS |
| Student Questionnaire | Students | Profile, 10 SUS items, 3 open questions | Adapted SUS |

Printable files: `docs/Bloom-Teacher-Evaluation-Form.md`, `docs/Bloom-Student-Evaluation-Form.md`, `docs/Bloom-Teacher-Questionnaire.md`, `docs/Bloom-Student-Questionnaire.md` (and the matching `.docx` files).

Likert scale for ISO items: 1 = strongly disagree … 5 = strongly agree.

Verbal interpretation of means:

| Mean | Interpretation |
|---|---|
| 4.21 – 5.00 | Strongly agree / Excellent |
| 3.41 – 4.20 | Agree / Very satisfactory |
| 2.61 – 3.40 | Neutral / Satisfactory |
| 1.81 – 2.60 | Disagree / Fair |
| 1.00 – 1.80 | Strongly disagree / Poor |

SUS scoring: for odd items use (rating − 1); for even items use (5 − rating); sum the ten values and multiply by 2.5 (range 0–100).

## Data Analysis

- **ISO forms:** mean per characteristic, overall product-quality mean (items 1–9), overall quality-in-use mean (items 10–12), interpreted with the table above. Results appear in Chapter IV Tables 4.4–4.5.
- **SUS:** mean score per group (teachers, students). Results appear in Table 4.6.
- **Open questions:** thematic grouping (HOTS load, grounding, what to improve). Quoted in Chapter IV UAT discussion only. Chapter V has **no new tables or figures**.
- **Automated tests:** pass/fail counts for unit, integration, and system testing (Tables 4.1–4.3).

No paired t-test of achievement scores is required.

## Testing Procedure (maps to Chapter IV)

| Level | Purpose | Evidence |
|---|---|---|
| Unit | Single rules (login, logout, CSRF, role/ownership) | Table 4.1 |
| Integration | Joined modules (assessment start/submit, deploy material, messages, monitor) | Table 4.2 |
| System | Whole student shell and automated suite | Table 4.3 (20/20 passed in development) |
| UAT | Teachers and students in the Grade 7 context | Tables 4.4–4.6 (filled after the pilot) |

UAT steps follow ISO/IEC 25040:2024: define the target and characteristics, design the two instruments, plan the session, execute after the participant uses Bloom, conclude with means and comments.

---

## References (minimum for the aligned evaluation and system)

Anderson, L. W., & Krathwohl, D. R. (Eds.). (2001). *A taxonomy for learning, teaching, and assessing*. Longman.

Bloom, B. S. (Ed.). (1956). *Taxonomy of educational objectives*. Longmans.

Brooke, J. (1996). SUS: A quick and dirty usability scale. In P. W. Jordan et al. (Eds.), *Usability evaluation in industry* (pp. 189–194). Taylor & Francis.

ISO/IEC. (2023). *ISO/IEC 25010:2023 Systems and software engineering — SQuaRE — Product quality model*.

ISO/IEC. (2023). *ISO/IEC 25019:2023 Systems and software engineering — SQuaRE — Quality-in-use model*.

ISO/IEC. (2024). *ISO/IEC 25040:2024 Systems and software engineering — SQuaRE — Quality evaluation framework*.

ISO/IEC. (2011). *ISO/IEC 25010:2011* (superseded for this study; cited only to explain the 2023 split).

**Keep your original Chapter II bibliographic entries** (local studies, DepEd issuances, related systems) and add the ISO 2023/2024 entries above. Do not cite 25010:2011 as the current product-quality model.

---

## How to assemble the thesis

1. Official Word file: paste **chengwaThesis** Chapters I–III.  
2. Paste **IT7-Chapter4-5** as Chapters IV–V.  
3. Insert figures: Ch III Figs. 1–7 (diagrams you already drew, captions updated); Ch IV Figs. 8–27 from `docs/audit-screenshots/`.  
4. Appendices: the four evaluation/questionnaire forms.  
5. After the Grade 7 UAT: fill Tables 4.4–4.6 and delete `[after UAT]` lines in Chapter V.

**Do not edit `IT7FINAL-revised.md` for this alignment.** That file is the old mixed draft.
