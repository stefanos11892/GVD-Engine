import re
import logging
import asyncio
from typing import Dict, Any, List, Tuple, Set
from src.parsers.financial_pdf import FinancialPDFParser

logger = logging.getLogger("DeltaEngine")

class DeltaParser:
    def __init__(self):
        self.parser = FinancialPDFParser()

    async def parse_dual_docs(self, current_pdf: str, prior_pdf: str) -> Dict[str, Any]:
        """
        Parses two PDFs to prepare for Delta Analysis.
        In a real scenario, this would run in parallel executors.
        For now, we run sequentially but structuring for async.
        """
        logger.info(f"Parsing Current: {current_pdf}")
        current_data = self.parser.parse(current_pdf)
        
        logger.info(f"Parsing Prior: {prior_pdf}")
        prior_data = self.parser.parse(prior_pdf)
        
        return {
            "current": current_data,
            "prior": prior_data
        }

class VaguenessChecker:
    def __init__(self):
        # Patterns looking for vague qualifiers replacing numbers
        self.vague_terms = [
            "significant", "material", "substantial", "meaningful", 
            "various", "certain", "approximately"
        ]
        # Regex to find sentences with vague terms
        self.vague_pattern = re.compile(r'\b(' + '|'.join(self.vague_terms) + r')\b', re.IGNORECASE)
        # Regex to find monetary values (e.g. $50 million, $10.5B, $100)
        self.money_pattern = re.compile(r'\$(\d+(?:\.\d+)?[MBK]?)', re.IGNORECASE)

    def check_retreats(self, current_text: str, prior_text: str) -> List[Dict[str, str]]:
        """
        Detects 'Numerical Retreats' where specific numbers in Prior are replaced 
        by vague qualifiers in Current.
        """
        retreats = []
        
        # Split into sentences (simple split for MVP)
        prior_sentences = [s.strip() for s in prior_text.split('.') if s.strip()]
        current_sentences = [s.strip() for s in current_text.split('.') if s.strip()]
        
        # Heuristic: Find sentences in Prior with Money
        money_sentences = [s for s in prior_sentences if self.money_pattern.search(s)]
        
        for p_sent in money_sentences:
            # Extract key topics (Capitalized words) to fuzzy match in Current
            # e.g. "We expect to save $50 million." -> Topic: "save" (heuristic)
            # Better: use simple n-gram match
            
            # extract the number
            money_match = self.money_pattern.search(p_sent)
            money_val = money_match.group(0) if money_match else "MONEY"
            
            # Try to find a matching sentence in Current that LACKS money but HAS vague terms
            for c_sent in current_sentences:
                # Similarity check: Share at least 3 significant words (longer than 4 chars)
                p_words = set(w.lower() for w in p_sent.split() if len(w) > 4)
                c_words = set(w.lower() for w in c_sent.split() if len(w) > 4)
                common = p_words.intersection(c_words)
                
                if len(common) >= 2: # Found a context match
                    if self.vague_pattern.search(c_sent) and not self.money_pattern.search(c_sent):
                        retreats.append({
                            "type": "Numerical Retreat",
                            "prior": p_sent,
                            "current": c_sent,
                            "retreat_from": money_val,
                            "retreat_to": self.vague_pattern.search(c_sent).group(0)
                        })
        
        return retreats

class EntropyAnalyzer:
    def __init__(self):
        pass

    def calculate_density(self, text: str) -> float:
        """
        Calculates Information Density:
        (Numbers + Capitalized Entities) / Total Words
        """
        words = text.split()
        if not words:
            return 0.0
            
        total_words = len(words)
        
        # Count Numbers (digits included)
        numbers = sum(1 for w in words if any(c.isdigit() for c in w))
        
        # Count Entities (Capitalized but not start of sentence - approximation)
        # We'll just count Capitalized words for raw density heuristic
        # Ignoring first word of sentence is hard without sentence splitting
        # MVP: Count all capitalized words excluding standard stopwords
        capitalized = sum(1 for w in words if w[0].isupper() and w.lower() not in ["the", "a", "an", "we", "it", "this"])
        
        density = (numbers + capitalized) / total_words
        return round(density, 4)

    def analyze_obfuscation(self, current_text: str, prior_text: str) -> Dict[str, Any]:
        d_curr = self.calculate_density(current_text)
        d_prior = self.calculate_density(prior_text)
        
        # If density drops by > 20%, flag it
        is_obfuscated = False
        if d_prior > 0:
            change = (d_curr - d_prior) / d_prior
            if change < -0.20:
                is_obfuscated = True
        else:
            change = 0
            
        return {
            "current_density": d_curr,
            "prior_density": d_prior,
            "change_pct": round(change * 100, 2),
            "is_obfuscated": is_obfuscated
        }

class SilentOmissionDetector:
    def __init__(self):
        pass

    def extract_headers(self, markdown: str) -> Set[str]:
        # Identify headers and List Items (Risk Factors often appear as lists)
        items = set()
        for line in markdown.split('\n'):
            line = line.strip()
            if not line: continue
            
            # Markdown Header
            if line.startswith('#'):
                clean = line.lstrip('#').strip()
                items.add(clean)
            
            # ALL CAPS TITLE
            elif line.isupper() and len(line) < 100:
                items.add(line)
                
            # List Items (1. Risk, - Risk)
            # Regex for "1. ", "2. ", "- "
            elif re.match(r'^(\d+\.|-|\*)\s+', line):
                # Clean the marker
                clean = re.sub(r'^(\d+\.|-|\*)\s+', '', line).strip()
                if len(clean) > 5: # Ignore trivial
                     items.add(clean)
                     
        return items

    def detect_omissions(self, current_md: str, prior_md: str) -> List[str]:
        curr_headers = self.extract_headers(current_md)
        prior_headers = self.extract_headers(prior_md)
        
        # Find headers in Prior that are completely missing in Current
        # Using exact matching for now. Fuzzy matching would be Phase 4.
        missing = []
        for h in prior_headers:
            if h not in curr_headers:
                # Filter out numbers/dates to reduce noise
                if len(h) > 5 and not h.replace(' ','').isdigit():
                    missing.append(h)
                    
        return missing

# Facade for easy use
class DeltaEngine:
    def __init__(self):
        self.parser = DeltaParser()
        self.vagueness = VaguenessChecker()
        self.entropy = EntropyAnalyzer()
        self.omission = SilentOmissionDetector()

    async def compare_documents(self, current_pdf: str, prior_pdf: str) -> Dict[str, Any]:
        # 1. Parse
        data = await self.parser.parse_dual_docs(current_pdf, prior_pdf)
        curr_md = data["current"]["markdown"]
        prior_md = data["prior"]["markdown"]
        
        # 2. Analyze
        retreats = self.vagueness.check_retreats(curr_md, prior_md)
        obfuscation = self.entropy.analyze_obfuscation(curr_md, prior_md)
        omissions = self.omission.detect_omissions(curr_md, prior_md)
        
        return {
            "numerical_retreats": retreats,
            "entropy_analysis": obfuscation,
            "silent_omissions": omissions
        }
