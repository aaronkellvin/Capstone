import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

md_path = Path(r"c:\Users\isaia\Downloads\IT7-Final-Paper-revised.md")
out_paths = [
    Path(r"c:\Users\isaia\Downloads\IT7-Final-Paper-revised.docx"),
    Path(r"D:\Capstone\Capstone\docs\IT7-Final-Paper-revised.docx"),
]
text = md_path.read_text(encoding="utf-8")


def runs_from_inline(s: str) -> str:
    parts = re.split(r"(\*\*[^*]+\*\*)", s)
    xml = []
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            content = escape(part[2:-2])
            xml.append(
                f'<w:r><w:rPr><w:b/></w:rPr><w:t xml:space="preserve">{content}</w:t></w:r>'
            )
        else:
            xml.append(f'<w:r><w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return "".join(xml) if xml else "<w:r><w:t></w:t></w:r>"


paras = []
for raw in text.splitlines():
    line = raw.rstrip()
    if not line.strip():
        paras.append("<w:p/>")
        continue
    if line.startswith("# "):
        inner = runs_from_inline(line[2:].strip())
        paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>{inner}</w:p>')
    elif line.startswith("## "):
        inner = runs_from_inline(line[3:].strip())
        paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>{inner}</w:p>')
    elif line.startswith("### "):
        inner = runs_from_inline(line[4:].strip())
        paras.append(f'<w:p><w:pPr><w:pStyle w:val="Heading3"/></w:pPr>{inner}</w:p>')
    elif line.startswith("- "):
        inner = runs_from_inline("• " + line[2:].strip())
        paras.append(f"<w:p>{inner}</w:p>")
    elif line.startswith("---"):
        paras.append("<w:p/>")
    else:
        inner = runs_from_inline(line)
        paras.append(f"<w:p>{inner}</w:p>")

document_xml = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body>"
    + "".join(paras)
    + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
    '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>'
    "</w:sectPr></w:body></w:document>"
)

content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>"""

rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

styles = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Normal" w:default="1"><w:name w:val="Normal"/><w:qFormat/><w:rPr><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="200" w:after="100"/></w:pPr><w:rPr><w:b/><w:sz w:val="28"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:before="160" w:after="80"/></w:pPr><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
</w:styles>"""

for out_path in out_paths:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/styles.xml", styles)
        zf.writestr("word/_rels/document.xml.rels", doc_rels)
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes)")
