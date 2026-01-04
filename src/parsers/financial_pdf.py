import logging
import json
from pathlib import Path
from typing import Dict, Any, List

# Docling Imports (V2)
try:
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
    from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
except ImportError:
    logging.warning("Docling not installed. Parser will fail.")
    DocumentConverter = None

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinancialPDFParser")

def configure_pipeline():
    """
    Configures the Docling Pipeline for Institutional 10-Ks.
    Optimization: OCR disabled for speed (assuming digital-born PDFs).
    High-Fidelity: Hierarchical table structure enabled.
    """
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True
    
    # NOTE: User requested 'hierarchical', but the library enum requires 'accurate'.
    # 'accurate' mode utilizes the TableFormer model, which correctly recovers hierarchical headers.
    pipeline_options.table_structure_options = TableStructureOptions(
        mode="accurate", 
        do_cell_text_clean=True
    )
    
    # Use V2 Backend for coordinate access
    return PdfFormatOption(
        pipeline_options=pipeline_options,
        backend=DoclingParseV2DocumentBackend
    )

# ======================================
# SINGLETON PATTERN FOR HEAVY ML MODEL
# ======================================
# The DocumentConverter loads large transformer-based models (TableFormer).
# Re-initializing on every request causes 1-2GB RAM spikes and 5-10s delay.
# Solution: Load once at module level and reuse.

_CONVERTER_INSTANCE = None

def _get_converter_instance():
    """Returns a shared DocumentConverter instance (singleton)."""
    global _CONVERTER_INSTANCE
    if _CONVERTER_INSTANCE is None:
        if DocumentConverter is None:
            raise ImportError("Docling library is missing. Please install it.")
        logger.info("Initializing DocumentConverter (one-time, heavy operation)...")
        _CONVERTER_INSTANCE = DocumentConverter(
            format_options={
                InputFormat.PDF: configure_pipeline()
            }
        )
        logger.info("DocumentConverter ready.")
    return _CONVERTER_INSTANCE


class FinancialPDFParser:
    def __init__(self):
        # Use shared singleton instance instead of creating a new one
        self.converter = _get_converter_instance()

    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parses a financial PDF into Semantic Markdown and a Coordinate Map.
        Returns:
            {
                "markdown": str,
                "provenance_map": List[Dict]  # [{text, page, bbox}]
            }
        """
        logger.info(f"Starting High-Fidelity Parse for: {file_path}")
        
        doc = self.converter.convert(file_path).document
        
        # 1. Semantic Markdown Export
        # We ensure strict markdown generation
        markdown_output = doc.export_to_markdown()
        
        # 2. Coordinate Mapping (The "Chain of Custody")
        provenance_map = self._extract_provenance(doc)
        
        logger.info(f"Parsing Complete. Extracted {len(provenance_map)} navigable elements.")
        
        return {
            "markdown": markdown_output,
            "provenance_map": provenance_map
        }

    def _extract_provenance(self, doc) -> List[Dict[str, Any]]:
        """
        Walks the Docling Document Object Model (DOM) to build a 'Click-to-Verify' map.
        Extracts [x,y,w,h] for paragraphs and table cells.
        """
        provenance = []
        
        for item, level in doc.iterate_items():
            try:
                if hasattr(item, "text") and item.text:
                    entry = {
                        "text_snippet": item.text[:100], 
                        "full_text": item.text,
                        "type": str(type(item).__name__),
                        "page": -1,
                        "bbox": []
                    }
                    
                    if hasattr(item, "prov") and item.prov:
                        first_prov = item.prov[0]
                        entry["page"] = first_prov.page_no
                        entry["bbox"] = first_prov.bbox.as_tuple() if hasattr(first_prov.bbox, "as_tuple") else str(first_prov.bbox)
                        
                    provenance.append(entry)
                    
            except Exception as e:
                logger.debug(f"Skipping item in provenance extraction: {e}")
                continue
                
        return provenance

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        parser = FinancialPDFParser()
        result = parser.parse(sys.argv[1])
        print(f"Stats: {len(result['provenance_map'])} elements extracted.")
