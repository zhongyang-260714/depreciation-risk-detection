import sys, io
pdf_path = r"C:/Users/Lenovo/Desktop/揭榜挂帅/XH-202626_科创企业特有风险的识别与管理.pdf"
text = None
ok = False
try:
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    parts = []
    for i, page in enumerate(doc):
        parts.append("\n===== PAGE %d =====\n" % (i+1) + page.get_text())
    text = "\n".join(parts)
    ok = True
    print("OK: PyMuPDF pages=", len(doc))
except Exception as e:
    print("PyMuPDF failed:", repr(e))
if not ok:
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            parts = []
            for i, page in enumerate(pdf.pages):
                parts.append("\n===== PAGE %d =====\n" % (i+1) + (page.extract_text() or ""))
            text = "\n".join(parts)
        ok = True
        print("OK: pdfplumber")
    except Exception as e:
        print("pdfplumber failed:", repr(e))
if not ok:
    try:
        import PyPDF2
        r = PyPDF2.PdfReader(pdf_path)
        parts = []
        for i, p in enumerate(r.pages):
            parts.append("\n===== PAGE %d =====\n" % (i+1) + (p.extract_text() or ""))
        text = "\n".join(parts)
        ok = True
        print("OK: PyPDF2 pages=", len(r.pages))
    except Exception as e:
        print("PyPDF2 failed:", repr(e))
if text is None:
    print("ALL_FAILED")
    sys.exit(2)
out = r"C:/Users/Lenovo/WorkBuddy/2026-07-27-11-41-06/_pdf_extracted.txt"
with io.open(out, "w", encoding="utf-8") as f:
    f.write(text)
print("WROTE", out, "chars=", len(text))
