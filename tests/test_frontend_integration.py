
import sys
import os
import pandas as pd
import json

sys.path.append(os.getcwd())

from src.utils.data_manager import DataManager

def test_integration():
    print("--- Testing Data Manager Integration (PDF -> DataManager -> CSV) ---")
    
    # 1. Setup
    dm = DataManager()
    file_path = os.path.join("inputs", "Monthly-Statement-2025-11.pdf")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    # 2. Execute Ingest
    print(f"Ingesting {file_path}...")
    result = dm.ingest_statement(file_path)
    print(f"Result: {result}")
    
    # 3. Verify Holdings (master_portfolio.csv)
    print("\n[VERIFYING HOLDINGS]")
    if os.path.exists(dm.portfolio_path):
        df = pd.read_csv(dm.portfolio_path)
        print(f"Loaded 'master_portfolio.csv'. Rows: {len(df)}")
        if not df.empty:
            print(f"Sample Ticker: {df.iloc[0]['Ticker']}")
            if len(df) > 80:
                 print("[SUCCESS]: Correctly loaded ~90 holdings.")
            else:
                 print(f"[WARNING]: Holdings count seems low ({len(df)}). This might be correct for this file.")
        else:
            print("[FAILED]: CSV is empty.")
    else:
        print("[FAILED]: 'master_portfolio.csv' not found.")

    # 4. Verify Transactions (transactions.csv)
    print("\n[VERIFYING TRANSACTIONS]")
    trans_path = os.path.join(dm.data_dir, 'transactions.csv')
    if os.path.exists(trans_path):
        df_trans = pd.read_csv(trans_path)
        print(f"Loaded 'transactions.csv'. Rows: {len(df_trans)}")
        if not df_trans.empty:
            print(f"Sample Transaction: {df_trans.iloc[0]['Action']} {df_trans.iloc[0]['Ticker']}")
            if len(df_trans) >= 20:
                 print("[SUCCESS]: Correctly loaded ~21 transactions.")
            else:
                 print("[WARNING]: Transaction count seems low.")
        else:
            print("[FAILED]: Transactions CSV is empty.")
    else:
        print("[FAILED]: 'transactions.csv' not created.")
        
    # 5. Verify Account Info
    print("\n[VERIFYING ACCOUNT INFO]")
    if dm.account_info.get("Account Value", 0) > 0:
        print(f"[SUCCESS]: Account Value updated to {dm.account_info['Account Value']}")
    else:
        print("[FAILED]: Account Value is 0.")

if __name__ == "__main__":
    test_integration()
