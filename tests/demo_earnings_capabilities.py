import os
import sys
import logging
from fpdf import FPDF

# Configure Path
sys.path.append(os.getcwd())

# MONKEY PATCH for HuggingFace (Symlink Fix)
import shutil
import huggingface_hub.file_download
def _force_copy(src, dst, new_blob=False):
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Copy failed: {e}")
huggingface_hub.file_download._create_symlink = _force_copy

try:
    from src.parsers.financial_pdf import FinancialPDFParser
    from src.parsers.indexer import CrossReferenceIndexer
except ImportError as e:
    print(f"Import Error: {str(e)}")
    sys.exit(1)

# Logging
logging.basicConfig(level=logging.ERROR) # Quiet the logs for clean output

def create_complex_10k(filename="complex_10k.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PAGE 1: BALANCE SHEET ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "CONSOLIDATED BALANCE SHEETS", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, "(In millions, except share amounts)", ln=True, align="C")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(100, 10, "Assets")
    pdf.cell(40, 10, "2024", align="R")
    pdf.cell(40, 10, "2023", align="R")
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", "", 10)
    data = [
        ("Current assets:", "", ""),
        ("  Cash and cash equivalents", "28,840", "29,965"),
        ("  Marketable securities", "31,590", "28,120"),
        ("  Accounts receivable, net", "44,230", "42,000"),
        ("  Inventories", "6,580", "6,331"),
        ("Total current assets", "111,240", "106,416"),
        ("", "", ""),
        ("Non-current assets:", "", ""),
        ("  Property, plant and equipment, net", "43,789", "39,245"),
        ("  Goodwill (See Note 3)", "12,400", "12,400"),
        ("Total Assets", "352,755", "335,038"),
    ]
    
    for label, v1, v2 in data:
        pdf.cell(100, 8, label)
        pdf.cell(40, 8, v1, align="R")
        pdf.cell(40, 8, v2, align="R")
        pdf.ln()

    pdf.ln(10)
    pdf.multi_cell(0, 8, "See Note 1 for Basis of Presentation.\nSee Note 2 for Significant Accounting Policies.\nSee Note 8 for details on Long-Term Debt.")

    # --- PAGE 2: NOTES ---
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "NOTES TO CONSOLIDATED FINANCIAL STATEMENTS", ln=True)
    pdf.ln(5)
    
    # Note 1
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Note 1. Basis of Presentation", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "The accompanying consolidated financial statements have been prepared in accordance with U.S. GAAP.")
    pdf.ln(5)

    # Note 2
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Note 2. Significant Accounting Policies", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "We recognize revenue when control of the promised goods or services is transferred to our customers.")
    pdf.ln(5)
    
    # Note 3 (Goodwill)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Note 3. Goodwill", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "We test goodwill for impairment annually. No impairment was recorded in 2024 or 2023.")
    pdf.ln(5)

    # Note 8 (Debt) - Intentionally skipping numbers to test robust indexing
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Note 8. Debt", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, "The Company has issued $5.0 billion in unsecured senior notes.")
    
    pdf.output(filename)
    return filename

def run_demo():
    print(">>> 0. GENERATING COMPLEX 10-K SAMPLE...")
    filename = create_complex_10k()
    print(f"    File created: {filename} (Matches 'Institutional Grade' complexity)")
    
    print("\n>>> 1. EXECUTING FINANCIAL PARSER (Docling V2)...")
    parser = FinancialPDFParser()
    result = parser.parse(filename)
    markdown = result["markdown"]
    provenance = result["provenance_map"]
    
    print("\n>>> 2. BUILDING CROSS-REFERENCE INDEX...")
    indexer = CrossReferenceIndexer()
    index_map = indexer.build_index(markdown, provenance)
    
    print("\n" + "="*60)
    print("OUTPUT REVIEW FOR USER")
    print("="*60)
    
    # --- OUTPUT 1: MARKDOWN SNIPPET ---
    print("\n[1] MARKDOWN SNIPPET (Financial Table)")
    print("-" * 40)
    # Find the table part in the markdown
    lines = markdown.split('\n')
    table_start = 0
    for i, line in enumerate(lines):
        if "| Assets" in line or "| 2024" in line:
            table_start = i
            break
            
    # Print 20 lines from table start
    for line in lines[table_start:table_start+20]:
        print(line)
    print("-" * 40)
    
    # --- OUTPUT 2: PROVENANCE SNIPPET ---
    print("\n[2] JSON PROVENANCE SNIPPET (First 5 Entries)")
    print("-" * 40)
    import json
    # Filter for non-empty items to show interesting data
    valid_prov = [p for p in provenance if p['text_snippet'].strip()][:5]
    print(json.dumps(valid_prov, indent=2))
    print("-" * 40)
    
    # --- OUTPUT 3: CROSS-REF LOG ---
    print("\n[3] CROSS-REF INDEXER RESULTS")
    print("-" * 40)
    print(f"Total Targets Indexed: {len(index_map)}")
    
    # Verify Citations from Page 1
    citations_to_check = ["See Note 1", "See Note 2", "See Note 8"]
    print("Resolving Citations found on Page 1:")
    for cit in citations_to_check:
        target = indexer.resolve_citation(cit, index_map)
        if target:
            print(f"  [PASS] '{cit}' -> Maps to {target['page']} (BBox: {target['bbox']})")
        else:
            print(f"  [FAIL] '{cit}' -> Resolution Failed")
    print("-" * 40)

if __name__ == "__main__":
    run_demo()
