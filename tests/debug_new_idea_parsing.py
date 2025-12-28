import re
import json

def test_parsing():
    print("--- Debugging New Idea Parsing logic ---")
    
    # Simulate problematic Originator Output (Markdown + Table)
    originator_text = """
Based on the live screen, I have identified **GOOG** as the top candidate.
This is a great company.

| Ticker | Market Cap | P/E Ratio | Thesis |
|---|---|---|---|
| GOOG | 3.8T | 25x | Great AI |

The company is highly profitable.
    """
    
    print("\n[1] Narrative Cleaning")
    # Current behavior: raw dump
    print(f"Current Narrative: {originator_text[:50]}... (Table Leaking)")
    
    # Proposed Fix: Strip Table using Regex
    # Regex to find | ... | lines
    clean_text = re.sub(r'\|.*\|', '', originator_text).strip()
    # Remove empty lines left behind
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()
    print(f"Cleaned Narrative:\n{clean_text}")

    # [2] Metrics Extraction from Table (Fallback)
    print("\n[2] Metrics Extraction from Table")
    # Try to extract Market Cap and P/E from the table text if Analyst fails
    match_row = re.search(r'\|\s*GOOG\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|', originator_text)
    if match_row:
        mcap = match_row.group(1).strip()
        pe = match_row.group(2).strip()
        print(f"Found in Table -> Cap: {mcap}, PE: {pe}")
    else:
        print("No table match found.")

    # [3] Score Scaling
    print("\n[3] Score Scaling")
    raw_score = 95 # 0-100 scale from Agent
    
    # Current Logic
    display_val_bad = int(raw_score * 10)
    print(f"Current Logic (Bad): {display_val_bad}/10")
    
    # Proposed Fix
    # Identify if score is > 10. If so, treat as 0-100.
    if raw_score > 10:
        display_val_good = int(raw_score / 10) # 95 -> 9
        progress_val = raw_score # 95%
    else:
        # 0-10 scale
        display_val_good = int(raw_score)
        progress_val = raw_score * 10
        
    print(f"Fixed Logic: {display_val_good}/10")

if __name__ == "__main__":
    test_parsing()
