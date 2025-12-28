import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("CrossRefIndexer")

class CrossReferenceIndexer:
    def __init__(self):
        # Snippets: "See Note 12", "Refer to Note 4", "Note 7"
        self.citation_pattern = re.compile(r"(?:See|Refer to)?\s*Note\s+(\d+)", re.IGNORECASE)
        # Headers: "Note 12. Income Taxes", "Note 12 - Revenue"
        self.target_pattern = re.compile(r"^#*\s*Note\s+(\d+)[.\-]", re.IGNORECASE | re.MULTILINE)

    def build_index(self, markdown_text: str, provenance_map: List[Dict]) -> Dict[str, Any]:
        """
        Scans the document for 'Targets' (e.g. 'Note 12. Income Taxes') and builds a map.
        Returns:
            {
                "Note 12": {
                    "text_snippet": "Note 12. Income Taxes...",
                    "page": 88,
                    "bbox": [x,y,w,h]
                }
            }
        """
        index = {}
        
        # 1. Find Targets in Markdown (Quick Scan)
        # We prefer using the provenance map to get exact coordinates
        
        for item in provenance_map:
            text = item.get("full_text", "")
            match = self.target_pattern.search(text)
            if match:
                note_num = match.group(1)
                key = f"Note {note_num}"
                
                # Check duplicate (Usually the first bold header is the definition)
                if key not in index:
                    index[key] = {
                        "text_snippet": text[:100],
                        "page": item.get("page", -1),
                        "bbox": item.get("bbox", [])
                    }
                    logger.debug(f"Indexed Target: {key} at Page {item.get('page')}")
        
        logger.info(f"Cross-Ref Index built with {len(index)} targets.")
        return index

    def resolve_citation(self, citation_text: str, index: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Takes a snippet like "See Note 12" and returns the target bbox.
        """
        match = self.citation_pattern.search(citation_text)
        if match:
            note_num = match.group(1)
            key = f"Note {note_num}"
            return index.get(key)
        return None
