import fitz  # PyMuPDF
import base64
import io
from typing import Tuple, Dict, Any

class PDFRenderer:
    def __init__(self, pdf_path: str):
        self.doc = fitz.open(pdf_path)

    def get_page_count(self) -> int:
        return len(self.doc)

    def get_page_image(self, page_num: int, zoom: float = 2.0) -> Tuple[str, float, float]:
        """
        Renders a specific page to a base64 encoded PNG image.
        Returns: (base64_string, width, height)
        Page numbers are 1-based in the API, but 0-based in fitz.
        """
        if page_num < 1 or page_num > len(self.doc):
             raise ValueError(f"Page {page_num} out of bounds")

        page = self.doc[page_num - 1] # 0-based index
        
        # High-DPI rendering
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to bytes
        img_data = pix.tobytes("png")
        
        # Encode to base64
        encoded = base64.b64encode(img_data).decode("utf-8")
        img_str = f"data:image/png;base64,{encoded}"
        
        return img_str, float(pix.width), float(pix.height), float(pix.width / page.rect.width)

    def get_page_metadata(self, page_num: int) -> Dict[str, float]:
        """
        Returns original PDF page dimensions for coordinate scaling.
        """
        page = self.doc[page_num - 1]
        rect = page.rect
        return {"width": rect.width, "height": rect.height}

    def close(self):
        self.doc.close()
