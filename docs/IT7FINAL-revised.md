# AI-POWERED SMART STUDY ASSISTANT FOR HOTS-BASED ASSESSMENT GENERATION AND LEARNING SUPPORT
### System name in the prototype: **Bloom**

**Revised draft (aligned with the working Capstone prototype)**  
Esguerra, Patrick Carlos P. · Lamadrid, Isaiah Matthew C. · Quilitis, Marvic Mat M.  
Colegio de San Juan de Letran Calamba · BS Information Technology · May 2026

---

## Revision summary (what changed from IT7FINAL)

| Section | Update |
|---|---|
| System naming | Prototype branded as **Bloom** (AI-Powered Smart Study Assistant) |
| Materials / Software | Placeholders replaced with **Python, Flask, SQLite, Gemini API** |
| Architecture | Matches Flask + `ai.py` + SQLite `bloom.db` |
| Use cases | Teacher / Student / Admin roles and real features |
| ERD | Updated to implemented tables |
| AI integration | Google **Gemini** primary (`GEMINI_API_KEY`); OpenAI optional |
| Learning support | Lesson upload → extract text → AI summary → HOTS practice/assessment |

Open this file in Word (**File → Open**) or copy sections back into your thesis document.

---

# CHAPTER I  
# INTRODUCTION

The cultivation of Higher-Order Thinking Skills (HOTS) has become a major priority in modern junior high education. Learners are expected to progress beyond memorization and recall, moving toward deeper processes such as analysis, evaluation, and creative problem-solving. Despite this emphasis, many classroom assessments still lean heavily on lower-level tasks due to lack of teacher training, time constraints, and the absence of structured support systems.

At Letran Calamba Junior High School, teachers must design assessments that align with curriculum standards while encouraging higher-level thinking. However, creating HOTS-based questions manually is demanding and time-intensive, often resulting in inconsistent quality and a reliance on recall-type items. While artificial intelligence tools have emerged to assist in content generation, most produce generic outputs that fail to align with specific curricula or frameworks such as Bloom’s Taxonomy. This gap highlights the need for a system that integrates AI with established educational models to support both teachers and students.

Therefore, this study proposes the development of **Bloom**, an AI-powered smart study assistant designed to generate curriculum-aligned HOTS-based assessments and provide structured learning support. By combining large language model APIs (primarily Google Gemini) with Bloom’s Taxonomy–guided prompt engineering, the system aims to improve the consistency, relevance, and cognitive quality of assessment materials for junior high students at Letran Calamba.

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
To design, develop, and evaluate a system that enhances Higher-Order Thinking Skills (HOTS) among junior high school students at Colegio de San Juan de Letran Calamba through curriculum-aligned assessment generation, intelligent validation mechanisms, and student-centered learning support features.

### Specific Objectives
- Develop an AI-driven study assistant (**Bloom**) capable of producing HOTS-focused assessments aligned with the Junior High School curriculum of Letran Calamba, guided by prompt engineering and Bloom’s Taxonomy.
- Implement filtering and validation mechanisms (prompt constraints, teacher review/approval workflows, and Bloom-level tagging for Analyze, Evaluate, and Create) that ensure generated questions reflect higher-order cognitive processes.
- Develop a student-centered learning support module that provides structured summaries, guided practice questions, and immediate feedback to support HOTS development.
- Evaluate the usability and effectiveness of the proposed system among teachers and students at Letran Calamba Junior High School.

## Scope and Delimitations
This study focuses on the design and development of Bloom for the Junior High School curriculum of Colegio de San Juan de Letran Calamba, initially covering **English, Mathematics, and Science** for a Grade 7 pilot section. The system generates HOTS-based assessments using prompt engineering and Bloom’s Taxonomy classification focused on **analyzing, evaluating, and creating**. The study does **not** include training or fine-tuning of a custom machine learning model; instead, it integrates external LLM APIs.

The student module is a supplementary practice and review tool and does not replace formal classroom instruction or teacher-administered assessments. All generated assessment items require teacher review and validation before classroom use. The study is limited to prototype development and evaluation among selected teachers and students; it does not include full institutional deployment or long-term measurement of academic achievement.

## Significance of the Study
*(Unchanged in intent from the original draft — Teachers, Students, Institution, Educational Technology, Future Researchers.)*

## Definition of Terms

**Bloom (AI-Powered Smart Study Assistant).** The working name of the proposed web-based system that generates HOTS-based assessments and provides structured learning support for junior high school teachers and students.

**Assessment Design.** The process of intentionally planning and constructing tests, quizzes, or tasks that measure specific learning outcomes at targeted cognitive levels.

**Bloom's Taxonomy.** A framework that organizes learning objectives into six stages, ranging from basic recall to advanced creative synthesis. This study focuses on Analyze, Evaluate, and Create.

**Curriculum-Aligned.** Content structured to match learning competencies, topics, and standards in the school’s curriculum and uploaded lesson materials.

**Decision-Support Tool.** A system that assists teachers by providing structured generated content without replacing professional judgment.

**HOTS (Higher-Order Thinking Skills).** Cognitive skills beyond memorization, including analyzing, evaluating, and creating.

**Prompt Engineering.** Writing clear instructions for an AI model so outputs better match educational goals.

**Gemini API.** Google’s generative AI application programming interface used by Bloom as the primary content-generation service.

**Rule-Based Filtering / Validation.** Mechanisms that constrain and screen outputs (prompt rules, Bloom tags, teacher approval of materials/questions) so recall-heavy or ungrounded items are reduced before classroom use.

---

# CHAPTER II  
# REVIEW OF RELATED LITERATURE

*(Literature review content from the original IT7FINAL draft is retained. No major citation changes were required for this revision. Keep your original Chapter II pages 11–21.)*

---

# CHAPTER III  
# METHODOLOGY

This chapter describes the research design, development approach, instruments, and evaluation procedures used in developing and assessing Bloom within Letran Calamba Junior High School.

## Research Design
The research adopts a **developmental design** because the primary output is a functional software prototype. An iterative Agile approach guides cycles of design, testing, feedback, and improvement. The study also uses a **mixed-methods** approach: quantitative data (usability, effectiveness, satisfaction) and qualitative data (teacher/student experiences and observations).

## Population of the Study
Participants are selected teachers and students from Letran Calamba Junior High School during Academic Year 2025–2026.

- **Teacher participants** — purposively selected faculty in core subjects who prepare classroom assessments; they evaluate the teacher module for usability, curriculum alignment, clarity, and HOTS item quality.
- **Student participants** — purposively selected junior high learners who use the learning support module and evaluate clarity, ease of use, engagement, feedback usefulness, and perceived HOTS support.

## Sampling Design
Purposive sampling is used because participants must be directly involved in assessment preparation and HOTS-related learning activities.

## Data Collection Method
1. **Structured interviews** with teachers (requirements analysis)
2. **Survey questionnaires** (adapted SUS after pilot testing)
3. **Pre-test and post-test** HOTS assessments (optional preliminary indicators)
4. **Observation and feedback** during pilot testing

## Software Development Lifecycle (SDLC)
Bloom follows the **Agile SDLC** (requirements → design → development → testing → deployment → maintenance).

### Agile phases (as applied)
- **Requirements Analysis** — teacher/student needs; HOTS assessment challenges; role-based requirements (student, teacher, admin)
- **System Design** — UI wireframes, SQLite schema, prompt templates, Bloom tagging workflow
- **Development** — Flask teacher/student/admin modules; material upload & extraction; Gemini/OpenAI integration; practice and assessment flows
- **Testing** — functional tests, usability tests, review of generated HOTS items
- **Deployment** — local/prototype deployment for school pilot use
- **Maintenance** — refinements from feedback (API provider settings, model updates, UI fixes)

## Context Flow Diagram
External entities interacting with Bloom:
1. **Teacher** — uploads/approves lesson materials, generates and reviews HOTS items, publishes assessments, posts announcements, monitors results
2. **Student** — studies approved summaries, takes guided practice, answers assessments, views results/feedback
3. **Admin** — manages settings and oversight functions
4. **AI Model (Gemini / optional OpenAI)** — returns summaries and HOTS questions from structured prompts grounded in uploaded lesson text

*(Keep your existing Figure 1 visual; update the caption to “Context Flow Diagram of Bloom”.)*

## Data Flow Diagram
Primary Level-1 processes:
1. **Input Processing** — login, uploads (PDF/TXT; DOCX/PPTX when dependencies allow), assessment parameters
2. **Text Extraction** — converts uploaded lesson files into extractable text
3. **Prompt Generation** — builds Bloom-guided prompts from lesson text and teacher/student parameters
4. **AI Content Generation** — calls Gemini (or OpenAI) API
5. **Validation / Teacher Review** — approval of materials; review/edit of generated questions before publish
6. **Output Delivery** — summaries, practice checks, assessments, scores/feedback

*(Keep Figure 2; update labels to match the above if needed.)*

## Use Case Diagram
### Student
- Sign in / sign out
- View subject hub (English, Mathematics, Science)
- Read AI-generated lesson summaries from approved materials
- Configure and take HOTS practice (Bloom focus, item count, question types)
- Take published assessments
- View results and feedback
- Read announcements

### Teacher
- Sign in / sign out
- Upload lesson materials and manage approval of student-submitted backups
- Generate lesson summaries via AI
- Generate HOTS questions (Analyze / Evaluate / Create / Mixed)
- Build, edit, publish, or close assessments
- Release scores/answers/feedback settings
- Post subject announcements
- Monitor attempts and section performance

### Admin
- Sign in / sign out
- Manage system settings (e.g., upload limits, configuration flags)

*(Update Figure 3 caption to Bloom and add Admin actor if your drawing currently shows only Teacher/Student.)*

## System Architecture
Bloom uses a three-layer web architecture:

1. **Presentation Layer** — Flask Jinja2 templates and static CSS/JS for student, teacher, and admin interfaces (login, subject hubs, practice, assessments, monitoring).
2. **Application Layer** — Flask routes and services:
   - authentication/session handling
   - material upload and text extraction (`extract.py`)
   - AI summarization and HOTS generation (`ai.py`)
   - practice drafts, scoring, announcements, monitoring logic
3. **Data Layer** — SQLite database file `instance/bloom.db` via Flask-SQLAlchemy
4. **External AI Services** — Google Gemini API (primary) and optional OpenAI API, configured through environment variables (`.env`)

*(Update Figure 4 accordingly.)*

## Flowchart
- **Teacher Module:** login → upload/approve materials → generate summary/HOTS items → review/edit → publish assessment → monitor results  
- **Student Module:** login → select subject/material → read summary → practice setup → answer items → submit → view feedback/results  

*(Retain Figures 5–6; align step labels with the implemented screens.)*

## Entity Relationship Diagram
Implemented logical entities in Bloom:

| Entity | Key fields / notes |
|---|---|
| **User** | id, email, name, role (`student`/`teacher`/`admin`), subject, password_hash, section |
| **Material** | id, slug, title, subject_slug, owner_id, source, status (`pending`/`approved`/`rejected`), filename, extracted_text |
| **Summary** | id, material_id, intro, sections_json |
| **Assessment** | id, slug, title, subject_slug, material_id, created_by, status, deadline, attempt_limit, release flags |
| **Question** | id, assessment_id, bloom, qtype (`mcq`/`essay`/`problem`), prompt, options_json, answer, explanation, rubric, citation |
| **Attempt** | id, user_id, assessment_id, kind (`assessment`/`practice`), scores, review_json, encouragement |
| **Announcement** | id, subject, title, body, teacher_id |
| **QuizDraft** | temporary practice question sets before submission |
| **Setting** | key/value system configuration |

Relationships (simplified):
- User 1—N Material, Assessment, Attempt, Announcement  
- Material 1—1 Summary  
- Assessment 1—N Question, Attempt  

*(Replace Figure 7 entities with the table above.)*

## Materials

### Software
The following tools and technologies are used in developing Bloom:

- **Programming language:** Python 3
- **Web framework:** Flask
- **ORM / database toolkit:** Flask-SQLAlchemy
- **Database:** SQLite (`bloom.db`)
- **AI API:** Google Gemini API (primary); OpenAI API (optional fallback)
- **Document text extraction:** pypdf (PDF); python-docx / python-pptx when available for DOCX/PPTX
- **Development environment:** Visual Studio Code / Cursor
- **Version control:** Git / GitHub
- **Database inspection:** DB Browser for SQLite
- **Prototyping / wireframes:** HTML wireframes / Figma (as applicable)
- **Configuration:** `.env` file for `GEMINI_API_KEY`, optional `OPENAI_API_KEY`, and model settings

### Hardware
- **Development machine:** desktop/laptop suitable for web development (recommended 16GB RAM)
- **Deployment:** local prototype server or cloud host capable of handling concurrent browser sessions and outbound AI API calls
- **User devices:** any modern web browser on school PCs, tablets, or smartphones

## Data
Primary data sources:
1. Teacher interview responses (requirements)
2. Usability/quality evaluation data from pilot testing
3. System logs of generated summaries/questions and learner attempts stored in SQLite during prototype use

Human participant data are anonymized in reporting; only aggregates are published.

## Ethics on the Use of Data
*(Retain original ethics safeguards: informed consent, voluntary participation, confidentiality, data security, beneficence, institutional permission.)*

## Research Instruments
*(Retain: Structured Interview Guide; HOTS Question Quality Rubric; Pre/Post HOTS instruments; adapted SUS.)*

## Data Analysis
*(Retain descriptive statistics, optional paired t-test as preliminary only, and thematic analysis for qualitative responses.)*

---

# REFERENCES
*(Keep the original reference list from IT7FINAL. Add the following implementation note in methodology citations if needed, not as a bibliographic replacement.)*

**Implementation note for the prototype:** Bloom integrates Google Gemini through the Generative Language API and stores application data in SQLite. Exact model names (e.g., `gemini-2.0-flash`) may be updated as providers revise available endpoints.

---

## How to use this file in your thesis
1. Open `IT7FINAL-revised.md` in Word, Google Docs, or VS Code.
2. Copy the **updated Chapter I naming**, **Definition of Terms**, and especially **Chapter III Materials / Architecture / Use Case / ERD** into your official thesis document.
3. Redraw Figures 1–7 captions/labels to say **Bloom** and match the finalized stack.
4. Keep your original Chapter II literature pages unless your adviser asks for changes.
