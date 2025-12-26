import pandas as pd
import os
from src.tools.pdf_reader import read_pdf
from src.tools.market_data import get_current_price

PORTFOLIO_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'master_portfolio.csv')

import re

import re

def parse_trading212_pdf(text):
    """
    Parses the text extracted from a Trading212 PDF statement.
    Prioritizes the 'Open positions' table for accurate holdings.
    """
    holdings = []
    
    print("DEBUG: Starting PDF Parse...")
    
    # Regex Explanation:
    # ^([A-Z0-9]{1,10})      : Ticker (Group 1) - Allow 1-10 chars (e.g. BRK.B)
    # \s+([A-Z0-9]{12})      : ISIN (Group 2) - Strict 12 chars
    # \s+([A-Z]{3})          : Currency (Group 3) - 3 chars
    # \s+([\d\.,]+)          : Quantity (Group 4) - Allow commas
    # \s+([\d\.,]+)          : Opening Price (Group 5)
    # \s+([\d\.,]+)          : Current Price (Group 6)
    
    # Note: We handle commas by removing them before float conversion
    pattern = re.compile(r"([A-Z0-9\.]{1,10})\s+([A-Z0-9]{12})\s+([A-Z]{3})\s+([\d\.,]+)\s+([\d\.,]+)\s+([\d\.,]+)")
    
    lines = text.split('\n')
    in_open_positions = False
    
    for line in lines:
        line = line.strip()
        
        # Detect start of table
        if "Open positions" in line:
            in_open_positions = True
            print("DEBUG: Found 'Open positions' section.")
            continue
            
        # Detect end of table (usually "Total" or empty lines after data)
        if in_open_positions and "Total" in line:
            in_open_positions = False
            print("DEBUG: End of 'Open positions' section.")
            continue
            
        # Optional: Only parse if inside the section (or just try to match everything if section detection is flaky)
        # For now, let's try to match everything that looks like a holding, as section headers might vary.
        
        match = pattern.search(line)
        if match:
            try:
                ticker = match.group(1)
                # isin = match.group(2)
                # currency = match.group(3)
                quantity_str = match.group(4).replace(',', '')
                avg_price_str = match.group(5).replace(',', '')
                current_price_str = match.group(6).replace(',', '')
                
                quantity = float(quantity_str)
                avg_price = float(avg_price_str)
                current_price = float(current_price_str)
                
                print(f"DEBUG: Parsed Holding -> {ticker}: {quantity} shares @ {current_price}")
                
                holdings.append({
                    "Ticker": ticker, 
                    "Shares": quantity,
                    "Avg Price": avg_price,
                    "Current Price": current_price
                })
            except ValueError as e:
                print(f"DEBUG: Parse Error for line '{line}': {e}")
        else:
            # print(f"DEBUG: No match for line: {line}") # Too noisy
            pass
            
    return holdings

def import_broker_statement(file_path):
    """
    Reads a PDF statement and updates the master_portfolio.csv
    """
    text = read_pdf(file_path)
    if "Error" in text:
        return text
        
    holdings = parse_trading212_pdf(text)
    
    if not holdings:
        return "No holdings found in PDF. Check format."
        
    # Load existing portfolio or create new
    if os.path.exists(PORTFOLIO_PATH):
        df = pd.read_csv(PORTFOLIO_PATH)
        # Ensure Opening Price column exists if reading old file
        if "Opening Price" not in df.columns and "Avg Price" in df.columns:
            df.rename(columns={"Avg Price": "Opening Price"}, inplace=True)
    else:
        df = pd.DataFrame(columns=["Ticker", "Company Name", "Shares", "Opening Price", "Current Price", "Market Value", "Allocation %", "Sector", "Tier"])
        
    # Update shares
    print(f"Found {len(holdings)} holdings in PDF.")
    
    for h in holdings:
        ticker = h["Ticker"]
        shares = h["Shares"]
        opening_price = h.get("Avg Price", 0) # Extracted as avg_price but corresponds to Opening Price
        current_price = h.get("Current Price", 0)
        
        # Check if ticker exists
        # Check if ticker exists
        if ticker in df['Ticker'].values:
            print(f"DEBUG: Updating existing ticker {ticker}")
            df.loc[df['Ticker'] == ticker, 'Shares'] = shares
            df.loc[df['Ticker'] == ticker, 'Opening Price'] = opening_price
            df.loc[df['Ticker'] == ticker, 'Current Price'] = current_price
            df.loc[df['Ticker'] == ticker, 'Market Value'] = shares * current_price
        else:
            print(f"DEBUG: Adding new ticker {ticker}")
            # Add new row
            new_row = {
                "Ticker": ticker, 
                "Shares": shares,
                "Company Name": ticker, # Placeholder
                "Opening Price": opening_price,
                "Current Price": current_price,
                "Market Value": shares * current_price,
                "Allocation %": 0,
                "Sector": "Unknown",
                "Tier": "Tier 2" # Default
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
    # Recalculate Market Value and Allocation
    df['Market Value'] = df['Shares'] * df['Current Price']
    total_value = df['Market Value'].sum()
    if total_value > 0:
        df['Allocation %'] = (df['Market Value'] / total_value) * 100
        
    df.to_csv(PORTFOLIO_PATH, index=False)
    
    # Trigger price update (optional, but good to refresh if PDF is old)
    # update_portfolio_prices() 
    
    return f"Successfully imported {len(holdings)} holdings from Open Positions table."

def update_portfolio_prices():
    """
    Updates the 'Current Price' and 'Market Value' columns in master_portfolio.csv
    """
    if not os.path.exists(PORTFOLIO_PATH):
        return "Portfolio file not found."
        
    df = pd.read_csv(PORTFOLIO_PATH)
    
    print("Updating portfolio prices...")
    for index, row in df.iterrows():
        ticker = row['Ticker']
        price = get_current_price(ticker)
        if price:
            df.at[index, 'Current Price'] = price
            df.at[index, 'Market Value'] = price * row['Shares']
            print(f"Updated {ticker}: ${price}")
        else:
            print(f"Could not fetch price for {ticker}")
            
    # Recalculate Allocation %
    total_value = df['Market Value'].sum()
    if total_value > 0:
        df['Allocation %'] = (df['Market Value'] / total_value) * 100
        
    df.to_csv(PORTFOLIO_PATH, index=False)
    return "Portfolio updated successfully."
