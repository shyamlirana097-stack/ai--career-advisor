import sys
from pypdf import PdfReader
from datetime import date

pdf_path, out_path, source_url = sys.argv[1], sys.argv[2], sys.argv[3]
text = "\n".join(p.extract_text() or "" for p in PdfReader(pdf_path).pages)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"SOURCE: {source_url}\nSCRAPED: {date.today()}\n\n{text}")
print(f"✔ {out_path}")