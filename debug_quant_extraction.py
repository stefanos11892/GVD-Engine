import asyncio
import logging
import os
import sys

# Add project root
sys.path.append(os.getcwd())

from src.parsers.financial_pdf import FinancialPDFParser
from src.agents.quant import QuantAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DebugQuant")

async def run_debug():
    pdf_path = "temp/uploads/898f42e4_f64ea-2024-02-20-10-24-11_9e550.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return

    logger.info(f"--- 1. Testing Parser on {pdf_path} ---")
    parser = FinancialPDFParser()
    try:
        result = parser.parse(pdf_path)
        markdown = result.get("markdown", "")
        logger.info(f"Markdown Length: {len(markdown)} chars")
        logger.info(f"Snippet: {markdown[:500]}...")
        
        if len(markdown) < 100:
            logger.error("Parsing Failed: Content too short.")
            return

        with open("debug_markdown.md", "w", encoding="utf-8") as f:
            f.write(markdown)
        logger.info("Saved markdown to debug_markdown.md")
            
    except Exception as e:
        logger.error(f"Parser Crashed: {e}")
        return

    logger.info("--- 2. Testing Quant Agent ---")
    quant = QuantAgent()
    try:
        extraction = quant.extract_metrics(markdown)
        logger.info("Quant Extraction Result:")
        import json
        print(json.dumps(extraction, indent=2))
    except Exception as e:
        logger.error(f"Quant Agent Crashed: {e}")

if __name__ == "__main__":
    asyncio.run(run_debug())
