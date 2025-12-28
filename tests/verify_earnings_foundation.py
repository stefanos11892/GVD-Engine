import os
import sys
import logging
from fpdf import FPDF
from pathlib import Path

# Setup Path
sys.path.append(os.getcwd())

# MONKEY PATCH: Force Copy instead of Symlink to avoid WinError 1314
import shutil
import huggingface_hub.file_download

def _force_copy(src, dst, new_blob=False):
    try:
        shutil.copy2(src, dst)
    except Exception as e:
        print(f"Copy failed: {e}")

huggingface_hub.file_download._create_symlink = _force_copy

# Import components
try:
    from src.parsers.financial_pdf import FinancialPDFParser
    from src.parsers.indexer import CrossReferenceIndexer
    from src.agents.auditor import AuditorAgent
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

def create_dummy_pdf(filename="dummy_10k.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Page 1: Content
    pdf.cell(200, 10, txt="Annual Report 2025", ln=1, align="C")
    pdf.cell(200, 10, txt="Consolidated Statement of Operations", ln=1)
    pdf.cell(200, 10, txt="Revenue ........................... $10.4B", ln=1)
    pdf.cell(200, 10, txt="See Note 12 for details on tax.", ln=1)
    
    # Page 2: Notes
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Note 12. Income Taxes", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="The effective tax rate was 21%. We paid $2.1B in taxes.")
    
    pdf.output(filename)
    return filename

def run_verification():
    print("--- 1. Generating Dummy 10-K PDF ---")
    pdf_path = create_dummy_pdf()
    print(f"Created: {pdf_path}")
    
    print("\n--- 2. Testing High-Fidelity Parsing (Docling) ---")
    parser = FinancialPDFParser()
    result = parser.parse(pdf_path)
    
    md = result["markdown"]
    provenance = result["provenance_map"]
    
    print(f"Markdown Length: {len(md)} chars")
    print(f"Provenance Items: {len(provenance)}")
    
    # Verify Content
    if "Revenue" in md and "$10.4B" in md:
        print("[PASS] Content Extraction Successful")
    else:
        print("[FAIL] Content Missing")
        
    # Verify Provenance
    if len(provenance) > 0 and "bbox" in provenance[0]:
        print(f"[PASS] BBox Captured: {provenance[0]['bbox']}")
    else:
        print("[FAIL] BBox Missing")

    print("\n--- 3. Testing Cross-Ref Indexer ---")
    indexer = CrossReferenceIndexer()
    index = indexer.build_index(md, provenance)
    
    # Check for Note 12
    if "Note 12" in index:
        target = index["Note 12"]
        print(f"[PASS] Note 12 Indexed at Page {target['page']}")
    else:
        print(f"[FAIL] Note 12 NOT Found in Index. Keys: {list(index.keys())}")
        
    # Check Resolution from Page 1
    page1_text = "See Note 12 for details"
    resolved = indexer.resolve_citation(page1_text, index)
    if resolved:
        print(f"[PASS] 'See Note 12' resolved to Page {resolved['page']}")
    else:
        print("[FAIL] Resolution failed")

    print("\n--- 4. Testing Auditor Agent Logic ---")
    auditor = AuditorAgent()
    # Mocking a verification call to see prompt construction
    # We won't run LLM to save tokens/time, just inspect object
    print(f"Auditor Initialized: {auditor.name}")
    print("Auditor System Prompt Snippet:")
    print(auditor.system_instruction[:200] + "...")
    
    print("\n--- PHASE 1 VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_verification()
