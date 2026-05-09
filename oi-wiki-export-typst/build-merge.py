import subprocess, os, sys
import io

STRIP_PDF = "oi-wiki-strip.pdf"
MERGED_PDF = "oi-wiki-a4.pdf"
TEMPLATE = "oi-wiki-export.typ"
INCLUDES = "includes.typ"
INCLUDES_MOD = "includes-merged.typ"
TEMPLATE_MOD = "oi-wiki-export-merged.typ"

# Step 1: create modified includes (skip first 4 chapters)
with open(INCLUDES, encoding="utf-8") as f:
    lines = f.readlines()
with open(INCLUDES_MOD, "w", encoding="utf-8") as f:
    f.writelines(lines[4:])

# Step 2: create modified template that uses the filtered includes
with open(TEMPLATE, encoding="utf-8") as f:
    content = f.read()
content = content.replace('#include "includes.typ"', '#include "includes-merged.typ"')
with open(TEMPLATE_MOD, "w", encoding="utf-8") as f:
    f.write(content)

# Step 3: compile strip PDF
typst = r"c:/Users/Iridet/AppData/Local/Microsoft/WinGet/Packages/Typst.Typst_Microsoft.Winget.Source_8wekyb3d8bbwe/typst-x86_64-pc-windows-msvc/typst.exe"
r = subprocess.run([typst, "compile", TEMPLATE_MOD, STRIP_PDF],
    capture_output=True, text=True, errors="replace")
if r.returncode != 0:
    print("Typst compile error:")
    print(r.stderr)
    sys.exit(1)
print(f"Strip PDF created: {STRIP_PDF}")

# Step 4: merge 3-up into A4 using direct page references (no image rendering)
import fitz

src = fitz.open(STRIP_PDF)
n = len(src)
print(f"Strip pages: {n}")

a4_w, a4_h = 595, 842  # A4 in points
strip_w = a4_w / 3
strip_h = a4_h

dst = fitz.open()

for i in range(0, n, 3):
    page = dst.new_page(width=a4_w, height=a4_h)
    for j in range(3):
        idx = i + j
        if idx >= n:
            break
        r = fitz.Rect(j * strip_w, 0, (j+1) * strip_w, strip_h)
        page.show_pdf_page(r, src, idx)
    print(f"Merged page {i//3 + 1}/{(n + 2)//3}")

dst.save(MERGED_PDF)
dst.close()
src.close()
print(f"A4 PDF created: {MERGED_PDF} ({os.path.getsize(MERGED_PDF)/1024/1024:.0f}MB)")

# Cleanup temp files
os.remove(INCLUDES_MOD)
os.remove(TEMPLATE_MOD)
os.remove(STRIP_PDF)
