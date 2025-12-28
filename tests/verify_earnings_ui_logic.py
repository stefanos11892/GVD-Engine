import asyncio
import os
import sys
import logging
import json
import base64

# Setup Path
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

from src.utils.pdf_renderer import PDFRenderer
from src.dashboard.callbacks.earnings_callbacks import generate_pdf_figure

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase5Verification")

def verify_ui_logic():
    print(">>> 1. INITIALIZING PDF RENDERER...")
    pdf_path = "complex_10k.pdf"
    if not os.path.exists(pdf_path):
        print("Error: complex_10k.pdf missing. Run demo script first.")
        return

    renderer = PDFRenderer(pdf_path)
    count = renderer.get_page_count()
    print(f"[PASS] PDF Loaded. Total Pages: {count}")
    
    print(">>> 2. TESTING PAGE RENDER (IMAGE)...")
    img_str, w, h = renderer.get_page_image(1) # Page 1
    if img_str.startswith("data:image/png;base64,"):
         print(f"[PASS] Page 1 Rendered to Base64 (Size: {w}x{h}).")
         # Check content length roughly
         if len(img_str) > 1000:
             print("[PASS] Image Content looks valid.")
    else:
         print("[FAIL] Image String format incorrect.")

    print(">>> 3. TESTING CANVAS CALLBACK LOGIC (JUMP)...")
    # Simulate Callback Inputs: current_page=1
    # We call generate_pdf_figure directly, passing the Mocked Renderer
    # (Here we use the real renderer instance)
    
    fig, indicator, page_store = generate_pdf_figure(1, renderer)
    
    # Assertions on Figure
    if fig is None:
        print("[FAIL] Callback returned None.")
        return
        
    layout = fig.layout
    # Check Background Image
    if len(layout.images) > 0:
        print("[PASS] Figure has Background Image.")
        if layout.images[0].source.startswith("data:image/png;base64,"):
             print("[PASS] Background Source is Base64.")
    else:
        print("[FAIL] Figure missing background image.")
        
    # Check Shapes (BBox)
    if len(layout.shapes) > 0:
        bbox = layout.shapes[0]
        print(f"[PASS] Figure has Bounding Box: {bbox}")
        if bbox['line']['color'] == "Red":
             print("[PASS] Bounding Box is RED (Adversarial Warning).")
    else:
        print("[FAIL] Figure missing BBox shape.")

if __name__ == "__main__":
    verify_ui_logic()
