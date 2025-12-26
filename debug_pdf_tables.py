
import pdfplumber
import os

files = ["Monthly-Statement-2025-10.pdf", "Monthly-Statement-2025-11.pdf"]
for f in files:
    path = os.path.join("inputs", f)
    if not os.path.exists(path): continue
    print(f"\nScanning {f}...")
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            if tables:
                print(f"Page {i+1} Tables:")
                for t in tables:
                    if t:
                        clean_row = [str(c).replace('\n', ' ') for c in t[0] if c]
                        print(f"  Header: {clean_row}")
            
            # Check for page titles
            text = page.extract_text() or ""
            lines = text.split('\n')[:5]
            print(f"  Page {i+1} Top Lines: {[l.strip() for l in lines if l.strip()]}")
