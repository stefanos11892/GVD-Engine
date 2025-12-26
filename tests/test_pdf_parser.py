
import sys
import os
import json
import pdfplumber
sys.path.append(os.getcwd())

from src.parsers.trading212 import Trading212Parser

def test_parser(filename):
    print(f"\n--- Testing Parser on {filename} ---")
    file_path = os.path.join("inputs", filename)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    parser = Trading212Parser()
    try:
        # Debugging: Print headers of first few tables to understand structure
        with pdfplumber.open(file_path) as pdf:
            full_text = ""
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                full_text += f"\n--- Page {i+1} ---\n{text}"
            
            print(f"Contains 'Open positions'? {'Open positions' in full_text}")
            print(f"Contains 'Account value'? {'Account value' in full_text}")
            print(f"Contains 'executed trades'? {'executed trades' in full_text}")
            
            # Print first 1000 chars to see layout
            print(f"Snippet:\n{full_text[:1000]}")
                    
        data = parser.parse(file_path)
        
        print("\n[SUMMARY]")
        print(json.dumps(data["summary"], indent=2))
        
        print(f"\n[HOLDINGS] Found {len(data['holdings'])} positions.")
        if data["holdings"]:
            print("First 3:")
            for h in data["holdings"][:3]:
                print(h)
                
        print(f"\n[TRANSACTIONS] Found {len(data['transactions'])} transactions.")
        if data["transactions"]:
            print("First 3:")
            for t in data["transactions"][:3]:
                print(t)
                
        if len(data["holdings"]) > 0:
            print("\n[SUCCESS]: Parser extracted holdings.")
        else:
            print("\n[WARNING]: No holdings found. Check table logic.")
            
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parser("Monthly-Statement-2025-10.pdf")
    test_parser("Monthly-Statement-2025-11.pdf")
