"""Build the Bloom IT access-request memo on the Letran RQMPD consent letterhead."""

from __future__ import annotations

import shutil
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

TEMPLATE = Path(r"C:\Users\isaia\Downloads\INFORMED CONSENT.docx")
OUTPUTS = [
    Path(r"C:\Users\isaia\Downloads\IT-Access-Request-Grade7-Bloom.docx"),
    Path(r"D:\Capstone\Capstone\docs\IT-Access-Request-Grade7-Bloom.docx"),
    Path(r"D:\Capstone\Capstone\docs\IT-Access-Request-Grade7-Bloom-letterhead.docx"),
]

TITLE = (
    "AI-Powered Smart Study Assistant for HOTS-Based Assessment "
    "Generation and Learning Support (Bloom)"
)
RESEARCHERS = (
    "Esguerra, Patrick Carlos P.; Lamadrid, Isaiah Matthew C.; "
    "Quilitis, Marvic Mat M."
)


def clear_body(doc: Document) -> None:
    body = doc.element.body
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def set_run(run, size=11, bold=False, italic=False, font="Arial"):
    run.font.name = font
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0, 0, 0)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:eastAsia"), font)


def add_para(
    doc,
    text="",
    *,
    size=11,
    bold=False,
    italic=False,
    align=None,
    space_after=6,
    space_before=0,
    justify=False,
):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align is not None:
        p.alignment = align
    if text:
        run = p.add_run(text)
        set_run(run, size=size, bold=bold, italic=italic)
    return p


def add_mixed(doc, parts, *, align=None, justify=False, space_after=6, space_before=0):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(space_before)
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align is not None:
        p.alignment = align
    for text, size, bold, italic in parts:
        run = p.add_run(text)
        set_run(run, size=size, bold=bold, italic=italic)
    return p


def heading(doc, text):
    add_para(doc, text, size=11, bold=True, space_before=10, space_after=4)


def body(doc, text):
    add_para(doc, text, size=11, justify=True, space_after=8)


def fill_grid_cell(cell, text, *, bold=False, size=11):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_run(run, size=size, bold=bold)


def add_grid_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        fill_grid_cell(table.rows[0].cells[i], h, bold=True)
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            fill_grid_cell(table.rows[r_i + 1].cells[c_i], val, bold=(c_i == 0))
    add_para(doc, "", space_after=8)
    return table


def build():
    if not TEMPLATE.exists():
        raise FileNotFoundError(f"Missing Letran template: {TEMPLATE}")

    doc = Document(str(TEMPLATE))
    clear_body(doc)

    add_para(
        doc,
        "REQUEST FOR ACCESS TO GRADE 7 SCHOOL EMAIL",
        size=11,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        space_after=0,
    )
    add_para(
        doc,
        "ACCOUNTS AND DIRECTORY DATA",
        size=11,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        space_after=4,
    )
    add_para(
        doc,
        "Bloom Capstone Pilot — Memorandum to MIS / Information Technology",
        size=11,
        bold=True,
        italic=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        space_after=10,
    )

    add_mixed(doc, [("Data Privacy Notice:", 8, True, False)], justify=True, space_after=4)
    add_para(
        doc,
        (
            "This request seeks only the minimum directory data needed to create Bloom "
            "login accounts for one (1) approved Grade 7 pilot section. Access, if granted, "
            "shall be limited to the student-researchers named below, their faculty adviser, "
            "and authorized Research, Quality Management, and Planning Department (RQMPD), "
            "Junior High School, and MIS/IT staff of Colegio de San Juan de Letran Calamba. "
            "Personal data in hard copy will be held securely; personal data in soft copy "
            "may be stored in a restricted folder and in the Bloom prototype database used "
            "for this pilot. The list will not be posted publicly, sold, or used for "
            "marketing. Grade 7 learners are minors; release is requested only after the "
            "Data Protection Officer and Junior High School Principal authorize processing, "
            "and after any required parent/guardian notice or consent."
        ),
        size=8,
        justify=True,
        space_after=8,
    )

    table = doc.add_table(rows=3, cols=2)
    table.style = "Table Grid"
    info_rows = [
        ("Researcher/Group No.:", "BSIT Capstone / IT7 (AY 2025–2026)"),
        ("Research Title:", TITLE),
        ("Researcher(s):", RESEARCHERS),
    ]
    for i, (label, value) in enumerate(info_rows):
        fill_grid_cell(table.rows[i].cells[0], label, bold=True)
        fill_grid_cell(table.rows[i].cells[1], value)
    table.columns[0].width = Cm(4.5)
    table.columns[1].width = Cm(12.0)
    add_para(doc, "", space_after=8)

    add_para(
        doc,
        "MEMORANDUM",
        size=11,
        bold=True,
        align=WD_ALIGN_PARAGRAPH.CENTER,
        space_before=4,
        space_after=8,
    )

    routing = [
        (
            "FOR:",
            "Head, Management Information Systems / Information Technology Department, "
            "Colegio de San Juan de Letran Calamba",
        ),
        (
            "THROUGH:",
            "Data Protection Officer; Principal, Junior High School; [Name], Research Adviser",
        ),
        (
            "FROM:",
            "Patrick Carlos P. Esguerra, Isaiah Matthew C. Lamadrid, and Marvic Mat M. "
            "Quilitis, BS Information Technology – Capstone Project Team",
        ),
        (
            "DATE:",
            "19 September 2026",
        ),
        (
            "SUBJECT:",
            "Request for Limited Access to Grade 7 School Email Accounts and Directory "
            "Data for the Bloom Capstone Pilot",
        ),
    ]
    for label, value in routing:
        add_mixed(
            doc,
            [(label + "  ", 11, True, False), (value, 11, False, False)],
            justify=True,
            space_after=4,
        )

    add_para(doc, "Respectfully submitted:", size=11, italic=True, space_before=8, space_after=8)

    heading(doc, "PURPOSE OF THIS REQUEST")
    body(
        doc,
        (
            "We respectfully request limited, time-bound, and purpose-specific access to "
            "directory information of one (1) Grade 7 pilot section of Letran Calamba "
            "Junior High School. This request is made solely to create student login "
            "accounts for Bloom, our approved capstone prototype: an AI-powered smart "
            "study assistant for HOTS-based assessment generation and learning support "
            "in English, Mathematics, and Science."
        ),
    )
    body(
        doc,
        (
            "Bloom authenticates users with school email addresses. Without an official "
            "list of the pilot section’s Letran emails and corresponding names, we cannot "
            "enroll the assigned class for evaluation. We are not requesting a dump of "
            "student records, personal contact lists, or any data beyond what is required "
            "to create school-email logins for the named pilot section."
        ),
    )

    heading(doc, "LEGAL AND INSTITUTIONAL BASIS")
    body(
        doc,
        (
            "This request is submitted under the institution’s authority and in accordance "
            "with Republic Act No. 10173 (Data Privacy Act of 2012) and its Implementing "
            "Rules and Regulations, particularly purpose limitation, data minimization, "
            "and protection of personal data of minors; Colegio de San Juan de Letran "
            "Calamba data-privacy and acceptable-use policies; and the approved scope of "
            "our capstone study, limited to a Grade 7 pilot section for Academic Year "
            "2025–2026."
        ),
    )
    body(
        doc,
        (
            "We understand that Grade 7 learners are minors, and that MIS/IT may release "
            "directory data only after the Data Protection Officer, Junior High School "
            "Principal, and (as required) parents/guardians have authorized the processing."
        ),
    )

    heading(doc, "DATA REQUESTED (MINIMUM NECESSARY)")
    body(
        doc,
        "Please release only the following fields for students enrolled in:",
    )
    add_para(doc, "Grade / Section:  Grade 7 · [Section name, e.g. Section A]", size=11, space_after=2)
    add_para(doc, "School year:  2025–2026", size=11, space_after=2)
    add_para(doc, "Estimated headcount:  [number] students", size=11, space_after=8)

    add_grid_table(
        doc,
        ["Field", "Needed?", "Reason"],
        [
            [
                "Official Letran school email",
                "Yes",
                "Unique login identifier in Bloom (you@letran-calamba.edu.ph)",
            ],
            [
                "Full name (as it appears in the school directory)",
                "Yes",
                "Display name on the student profile and teacher monitoring views",
            ],
            [
                "Section / advisory class",
                "Yes",
                "Confirm the learner belongs to the approved pilot section",
            ],
            [
                "Student number",
                "Optional",
                "Matching and de-duplication only, if MIS prefers it over name matching",
            ],
        ],
    )
    body(
        doc,
        (
            "Preferred format: a password-protected spreadsheet or CSV, delivered through "
            "an official school channel (not personal email), with columns: school_email, "
            "full_name, section[, student_number]."
        ),
    )

    heading(doc, "DATA WE ARE NOT REQUESTING")
    body(doc, "Please do not include any of the following:")
    for item in [
        "Existing school-account passwords, password hashes, or SSO credentials",
        "Personal (Gmail, Yahoo, etc.) email addresses",
        "Mobile numbers, home addresses, or family contact details",
        "Dates of birth, ages, photos, or government IDs",
        "Grades, report cards, disciplinary records, or guidance files",
        "Medical, financial, or other sensitive personal information",
        (
            "Parent/guardian personal data (consent, if required, should be handled by "
            "Junior High School using school processes, not by releasing parent contact "
            "lists to the student researchers)"
        ),
    ]:
        add_para(doc, "•  " + item, size=11, justify=True, space_after=4)
    add_para(doc, "", space_after=4)
    body(
        doc,
        (
            "Bloom will issue temporary system passwords that we generate. We do not need, "
            "and should not receive, students’ existing Letran account passwords."
        ),
    )

    heading(doc, "HOW THE DATA WILL BE USED")
    body(
        doc,
        (
            "The research adviser or a designated admin user will import the approved list "
            "into Bloom (school email, name, role = student, temporary password). Students "
            "will sign in with their Letran school email and the temporary Bloom password, "
            "then change the password on first use. Teachers of English, Mathematics, and "
            "Science for the same section will use Bloom to upload lessons, generate HOTS "
            "items, and monitor the pilot. Data will be used only to operate and evaluate "
            "the prototype for the capstone study. It will not be sold, posted publicly, "
            "used for marketing, or reused for another project."
        ),
    )
    body(
        doc,
        (
            "No student personal data will be sent to AI providers (Gemini/OpenAI) as part "
            "of prompts. Lesson content used for generation is teacher-uploaded instructional "
            "material, not student profiles."
        ),
    )

    heading(doc, "ACCESS, STORAGE, AND RETENTION")
    add_grid_table(
        doc,
        ["Control", "Commitment"],
        [
            [
                "Who may see the list",
                "The three named student researchers, the research adviser, and designated JHS/MIS personnel only",
            ],
            [
                "Storage",
                "Password-protected file; Bloom database on a device/server used for the capstone, not a public repository",
            ],
            [
                "Accounts",
                "Role-based access (student / teacher / admin); no shared student logins",
            ],
            [
                "Transmission",
                "Official school email or MIS-controlled share; no USB copies left unattended; no posting in group chats",
            ],
            [
                "Retention",
                "Directory file and imported accounts will be deleted or anonymized within thirty (30) days after the capstone defense / end of the approved pilot, whichever comes first, unless the school directs otherwise",
            ],
            [
                "Incidents",
                "Any suspected loss or unauthorized access will be reported immediately to the Data Protection Officer and MIS/IT",
            ],
        ],
    )
    body(
        doc,
        "We will not commit the student list, emails, or database dumps to GitHub or any public repository.",
    )

    heading(doc, "REQUESTED ACTION FROM MIS / IT")
    body(doc, "We respectfully request that MIS/IT:")
    add_para(
        doc,
        "1. Confirm whether the Grade 7 school emails for the named section can be released for this capstone purpose.",
        size=11,
        justify=True,
        space_after=4,
    )
    add_para(
        doc,
        "2. Coordinate with the Data Protection Officer and Junior High School Principal on any required parent/guardian notice or consent before release.",
        size=11,
        justify=True,
        space_after=4,
    )
    add_para(
        doc,
        "3. Provide the minimum fields listed above in a secure file, or create the Bloom accounts internally and give us only confirmation that the pilot accounts exist.",
        size=11,
        justify=True,
        space_after=4,
    )
    add_para(
        doc,
        "4. Advise us of any additional forms, NDAs, or acceptable-use acknowledgments we must sign before the file is released.",
        size=11,
        justify=True,
        space_after=8,
    )
    body(
        doc,
        (
            "If MIS/IT prefers not to release a file to student researchers, we request "
            "the alternative: that MIS/IT or a JHS administrator import the accounts into "
            "Bloom, or issue the list only to the research adviser."
        ),
    )

    heading(doc, "PILOT PERIOD")
    add_para(doc, "Proposed start:  [date]", size=11, space_after=2)
    add_para(doc, "Proposed end:  [date]", size=11, space_after=2)
    add_para(
        doc,
        "Venue / mode:  Letran Calamba Junior High School; Bloom prototype for evaluation only (not full institutional deployment)",
        size=11,
        space_after=8,
    )

    heading(doc, "WHO TO CONTACT")
    body(
        doc,
        (
            "For questions about this request or Bloom, contact the student-researchers "
            "or their faculty adviser at the College of Information and Communications "
            "Technology, Colegio de San Juan de Letran Calamba, Bucal, Calamba City, Laguna."
        ),
    )
    add_grid_table(
        doc,
        ["Role", "Name", "Email / contact"],
        [
            ["Student researcher", "Patrick Carlos P. Esguerra", "[school email]"],
            ["Student researcher", "Isaiah Matthew C. Lamadrid", "[school email]"],
            ["Student researcher", "Marvic Mat M. Quilitis", "[school email]"],
            ["Research adviser", "[Name, title]", "[school email]"],
        ],
    )
    body(
        doc,
        (
            "We are available to meet MIS/IT and the Data Protection Officer to walk through "
            "Bloom’s login and import process and to sign any required confidentiality undertaking."
        ),
    )

    add_para(doc, "Respectfully yours,", size=11, italic=True, space_before=8, space_after=10)
    for name in [
        "Patrick Carlos P. Esguerra",
        "Isaiah Matthew C. Lamadrid",
        "Marvic Mat M. Quilitis",
    ]:
        add_para(doc, "Print name of researcher:  " + name, size=11, space_after=2)
        add_para(doc, "Signature of researcher:  ______________________________", size=11, space_after=2)
        add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=10)

    heading(doc, "NOTED BY")
    add_para(doc, "Print name of research adviser:  ________________________________", size=11, space_after=2)
    add_para(doc, "Signature of research adviser:  _________________________________", size=11, space_after=2)
    add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=10)
    add_para(doc, "Print name of Program Chair / College Dean:  ____________________", size=11, space_after=2)
    add_para(doc, "Signature:  _____________________________________________________", size=11, space_after=2)
    add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=10)

    heading(doc, "RECOMMENDING APPROVAL")
    add_para(doc, "Print name of Principal, Junior High School:  ___________________", size=11, space_after=2)
    add_para(doc, "Signature:  _____________________________________________________", size=11, space_after=2)
    add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=10)
    add_para(doc, "Print name of Data Protection Officer:  _________________________", size=11, space_after=2)
    add_para(doc, "Signature:  _____________________________________________________", size=11, space_after=2)
    add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=10)

    heading(doc, "APPROVED / RELEASED BY")
    add_para(
        doc,
        "Print name of Head, MIS / Information Technology Department:  ______________",
        size=11,
        space_after=2,
    )
    add_para(doc, "Signature:  _____________________________________________________", size=11, space_after=2)
    add_para(doc, "Date: ______________  (MM/DD/YYYY)", size=11, space_after=8)

    tmp = Path(r"D:\Capstone\Capstone\docs\_IT-Access-Request-Grade7-Bloom.tmp.docx")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(tmp))
    for dest in OUTPUTS:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(tmp, dest)
            print("wrote", dest)
        except PermissionError:
            print("locked, skipped", dest)
    tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    build()
