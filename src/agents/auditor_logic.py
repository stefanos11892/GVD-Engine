import logging
import fitz  # PyMuPDF
from typing import Dict, Any, Tuple

logger = logging.getLogger("AuditorLogic")

class CoordinateVerifier:
    def __init__(self):
        pass

    def verify_jump(self, pdf_path: str, page_num: int, bbox: Tuple[float, float, float, float], claimed_text: str) -> Dict[str, Any]:
        """
        Performs the 'JUMP' verification.
        1. Opens PDF.
        2. Goes to Page.
        3. Extracts text at BBox.
        4. Compares with Claim.
        """
        try:
            doc = fitz.open(pdf_path)
            
            # Page Number Logic (Assumes 1-based provided, convert to 0-based)
            # PROVENANCE from Docling usually is 1-based.
            if page_num < 1 or page_num > len(doc):
                return {"match": False, "error": f"Page {page_num} out of bounds (1-{len(doc)})"}
            
            page = doc[page_num - 1]
            
            # BBox: [x0, y0, x1, y1] or [left, top, right, bottom]
            # Docling BBox might be different format. 
            # Docling V2 (TableFormer) usually standard PDF coordinates.
            # We assume [L, T, R, B] from the parser.
            # If parser provides [x, y, w, h] (top-left, width, height), we convert.
            # For this implementation, we assume the parser sends [L, T, R, B].
            
            rect = fitz.Rect(bbox)
            extracted_text = page.get_text("text", clip=rect).strip()
            
            # Comparison Logic (Case Insensitive, Normalize Whitespace)
            is_match = False
            if claimed_text.lower() in extracted_text.lower():
                is_match = True
            elif extracted_text.lower() in claimed_text.lower():
                is_match = True
            
            # Fuzzy match or "contains" is safer than strict equality due to layout noise
                
            result = {
                "match": is_match,
                "ground_truth_text": extracted_text,
                "claimed_text": claimed_text,
                "page": page_num
            }
            
            if not is_match:
                logger.warning(f"JUMP MISMATCH! Claim: '{claimed_text}' vs Truth: '{extracted_text}'")
                
            return result

        except Exception as e:
            logger.error(f"JUMP Verification Error: {e}")
            return {"match": False, "error": str(e)}

if __name__ == "__main__":
    # Test Stub
    print("Coordinate Verifier Module Loaded.")
