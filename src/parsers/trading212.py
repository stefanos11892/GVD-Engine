
import pdfplumber
import re

class Trading212Parser:
    """
    Parser for Trading212 Statements using pdfplumber (Visual Extraction).
    Implements multi-pass strategy (Default + Text-Based) to handle variable table formats.
    """

    def parse(self, file_path):
        """
        Parses the PDF and returns structured data.
        """
        data = {
            "summary": {},
            "holdings": [],
            "transactions": []
        }

        print(f"DEBUG: [Trading212Parser] Opening {file_path} with pdfplumber...")
        
        with pdfplumber.open(file_path) as pdf:
            # 1. Extract Summary from Page 1 (Try tables first, then text)
            first_page = pdf.pages[0]
            summary_tables = first_page.extract_tables()
            data["summary"] = self._extract_summary_from_tables(summary_tables)
            
            if not data["summary"].get("Account Value"):
                 data["summary"].update(self._extract_summary_text(first_page.extract_text()))

            # 2. Extract Data Tables across all pages using Multi-Pass Strategy
            # Pass 1: Standard Table Extraction (Lines) - Good for boxed tables
            # Pass 2: Text/Whitespace Extraction - Good for open tables or when lines are missing
            
            # We collect all candidate tables from all pages and all strategies
            candidate_tables = []
            
            for i, page in enumerate(pdf.pages):
                # Strategy 1: Default
                t1 = page.extract_tables()
                if t1:
                    # print(f"DEBUG: Page {i} - Default found {len(t1)} tables")
                    for t in t1: candidate_tables.append({"type": "DEFAULT", "data": t})
                
                # Strategy 2: Text-based (simulate columns by whitespace)
                t2 = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                if t2:
                    # print(f"DEBUG: Page {i} - Text found {len(t2)} tables")
                    for t in t2: candidate_tables.append({"type": "TEXT", "data": t})

            # Process candidates
            for entry in candidate_tables:
                table = entry['data']
                if not table: continue
                
                table_type = self._identify_table_type(table)
                
                if table_type == "HOLDINGS":
                    data["holdings"].extend(self._parse_holdings_table(table))
                        
                elif table_type == "TRANSACTIONS":
                    data["transactions"].extend(self._parse_transactions_table(table))

        # Post-process: Deduplicate Transactions based on content
        data["transactions"] = self._deduplicate_dicts(data["transactions"])
        data["holdings"] = self._deduplicate_dicts(data["holdings"])

        return data

    def _deduplicate_dicts(self, dict_list):
        """Helper to remove exact duplicate dictionary entries."""
        seen = set()
        new_l = []
        for d in dict_list:
            t = tuple(sorted(d.items()))
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        return new_l

    def _extract_summary_from_tables(self, tables):
        summary = {}
        for table in tables:
            for row in table:
                if not row: continue
                # Flatten nulls
                clean_row = [str(x) for x in row if x]
                if len(clean_row) < 2: continue
                
                key_candidate = clean_row[0].replace("\n", " ").strip().lower()
                val_candidate = clean_row[-1].replace(",", "").strip() # Last item likely value
                
                # Check known keys
                if "account value" in key_candidate:
                     summary["Account Value"] = self._clean_money(val_candidate)
                if "free funds" in key_candidate:
                     summary["Free Funds"] = self._clean_money(val_candidate)
                if "portfolio value" in key_candidate:
                     summary["Portfolio Value"] = self._clean_money(val_candidate)
        return summary

    def _extract_summary_text(self, text):
        summary = {}
        if not text: return summary
        patterns = {
            "Account Value": r"Account value\s*[A-Z$€£]*\s*([0-9,]+\.[0-9]{2})",
            "Free Funds": r"Free funds\s*[A-Z$€£]*\s*([0-9,]+\.[0-9]{2})",
            "Portfolio Value": r"Portfolio value\s*[A-Z$€£]*\s*([0-9,]+\.[0-9]{2})"
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                summary[key] = self._clean_money(match.group(1))
        return summary

    def _clean_money(self, val_str):
        try:
            return float(val_str.replace("£","").replace("$","").replace("€","").replace(",","").strip())
        except:
            return 0.0

    def _identify_table_type(self, table):
        # Flatten first 10 rows (increased from 5 to catch headers after metadata)
        sample_rows = table[:10]
        text_dump = " ".join([str(cell).lower() for row in sample_rows for cell in row if cell])
        
        # Transactions: Look for unique transaction headers or action keywords
        if ("execution" in text_dump and "time" in text_dump) or \
           ("buy" in text_dump or "sell" in text_dump):
               if "isin" in text_dump or "order id" in text_dump:
                   return "TRANSACTIONS"

        # Holdings: Look for Quantity, Value, and no "Buy/Sell"
        # "name" or "instrument" + "quantity" + "value"
        # OR explicitly "open positions" in the title/metadata
        if "open positions" in text_dump or (
            ("quantity" in text_dump and "value" in text_dump) and \
            ("instrument" in text_dump or "isin" in text_dump)
        ):
             # Ensure it's not the transaction table (transactions also have quantity/value)
             # Transactions usually have 'Time' or 'Execution Time'. Holdings don't.
             if "time" not in text_dump and "execution" not in text_dump:
                 # print(f"DEBUG: Identified as HOLDINGS. Content: {text_dump[:100]}...")
                 return "HOLDINGS"
                 
        return "UNKNOWN"

    def _parse_holdings_table(self, table):
        records = []
        for row in table:
            # Clean None and whitespace
            clean = [str(cell).strip() for cell in row if cell and str(cell).strip()]
            if len(clean) < 3: continue
            
            # Skip Headers and Titles
            # Titles might include "Customer ID", "Open positions summary", "Pending orders"
            # We skip lines that don't look like data (no numbers, or standard headers)
            row_str = " ".join(clean).lower()
            if "customer id" in row_str or "open positions" in row_str or "pending orders" in row_str:
                continue
            if "quantity" in clean or "value" in row_str or "isin" in row_str: 
                continue
            
            # STRATEGY: Anchor on ISIN
            # ISIN is a 12-char alphanumeric starting with 2 letters.
            isin_index = -1
            isin_pattern = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
            
            for i, cell in enumerate(clean):
                if isin_pattern.match(cell):
                    isin_index = i
                    break
            
            if isin_index != -1:
                try:
                    # Name is likely 0 to isin_index-1 joined
                    name = " ".join(clean[:isin_index])
                    isin = clean[isin_index]
                    
                    # Scanning for numbers after ISIN
                    numbers = []
                    for item in clean[isin_index+1:]:
                        try:
                            # clean currency symbols out
                            val = float(item.replace(",",""))
                            numbers.append(val)
                        except:
                            pass
                    
                    # We expect at least [Qty, Price, Value] or just [Qty, Value]
                    if len(numbers) >= 2:
                        # Last number is usually Market Value (Total)
                        # First number is usually Quantity
                        qty = numbers[0]
                        market_value = numbers[-1]
                        
                        records.append({
                            "Ticker": name, 
                            "ISIN": isin,
                            "Qty": qty,
                            "Market Value": market_value
                        })
                except Exception as e:
                    pass
                    
        return records

    def _parse_transactions_table(self, table):
        records = []
        # Regex for date: YYYY-MM-DD
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        # Regex for ISIN
        isin_pattern = re.compile(r"^[A-Z]{2}[A-Z0-9]{10}$")
        
        for row in table:
            clean = [str(cell).strip() for cell in row if cell and str(cell).strip()]
            if len(clean) < 4: continue
            
            # Skip Headers
            if "Execution Time" in clean or "Action" in clean: continue
            
            try:
                # ANCHOR 1: Date (Start of row)
                has_date = date_pattern.search(clean[0])
                if not has_date: continue 
                
                date_str = clean[0]
                
                # ANCHOR 2: Action
                action_map = {"buy": "Buy", "sell": "Sell", "dividend": "Dividend", "deposit": "Deposit", "withdrawal": "Withdrawal"}
                action = "Unknown"
                for cell in clean:
                    if cell.lower() in action_map:
                        action = action_map[cell.lower()]
                        break
                
                # ANCHOR 3: ISIN (To find Ticker)
                ticker = "N/A"
                isin_idx = -1
                for i, cell in enumerate(clean):
                    if isin_pattern.match(cell):
                        isin_idx = i
                        break
                
                if isin_idx > 0:
                    ticker = clean[isin_idx - 1] # Ticker is usually right before ISIN
                elif isin_idx == -1:
                    # Fallback: Ticker is usually column 2 (Index 1) if Time is present, or Col 1 if not.
                    # Check if col 1 looks like a time "HH:MM:SS"
                    if ":" in clean[1]:
                        ticker = clean[2]
                    else:
                        ticker = clean[1]
                
                # ANCHOR 4: Total (End of row)
                total_val = self._clean_money(clean[-1])

                records.append({
                    "Date": date_str,
                    "Action": action,
                    "Ticker": ticker,
                    "Total": total_val,
                    "Raw": str(clean)
                })

            except Exception as e:
                pass
                
        return records
