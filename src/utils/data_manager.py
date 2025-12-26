import pandas as pd
import os
import json
from src.utils.portfolio_manager import import_broker_statement, update_portfolio_prices

class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        # Robust path finding
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_dir = os.path.join(self.project_root, 'data')
        self.portfolio_path = os.path.join(self.data_dir, 'master_portfolio.csv')
        self.account_info_path = os.path.join(self.data_dir, 'account_info.json')
        
        self.df = None
        self.account_info = {"Free Funds": 10000.0, "Account Value": 0.0} # Defaults
        
        self.load_data()
        self.initialized = True

    def load_data(self):
        """Loads portfolio and account info."""
        # Load Portfolio
        if os.path.exists(self.portfolio_path):
            self.df = pd.read_csv(self.portfolio_path)
            
            # Standardization: Qty -> Shares
            if "Qty" in self.df.columns and "Shares" not in self.df.columns:
                self.df.rename(columns={"Qty": "Shares"}, inplace=True)
                
            cols_numeric = ['Shares', 'Opening Price', 'Current Price', 'Market Value', 'Allocation %']
            for col in cols_numeric:
                if col not in self.df.columns:
                     self.df[col] = 0.0 # Force existence
                else:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        else:
            self.df = pd.DataFrame(columns=["Ticker", "ISIN", "Currency", "Shares", "Opening Price", "Current Price", "Unrealised P/L", "Value (Source)", "FX Rate", "Unrealised P/L (Base)", "Market Value", "Allocation %"])

        # Load Account Info
        if os.path.exists(self.account_info_path):
            try:
                with open(self.account_info_path, 'r') as f:
                    self.account_info = json.load(f)
            except Exception as e:
                print(f"ERROR loading account info: {e}")

    # Alias for backward compatibility
    def load_portfolio(self):
        return self.load_data()

    def get_portfolio_df(self):
        if self.df is None:
            self.load_data()
        return self.df

    def get_total_value(self):
        # Prefer the value from the statement if available, otherwise calculate
        if self.account_info.get("Account Value", 0) > 0:
            return self.account_info["Account Value"]
        return self.get_holdings_value() + self.get_cash_balance()

    def get_holdings_value(self):
        if self.df is None or self.df.empty:
            return 0.0
        return self.df['Market Value'].sum()

    def get_cash_balance(self):
        return self.account_info.get("Free Funds", 0.0)

    def get_holdings_list(self):
        if self.df is None or self.df.empty:
            return []
        return self.df['Ticker'].tolist()

    def get_portfolio_context(self):
        total_value = self.get_total_value()
        cash = self.get_cash_balance()
        invested = self.get_holdings_value()
        
        holdings_summary = ""
        if self.df is not None and not self.df.empty:
            sorted_df = self.df.sort_values(by='Market Value', ascending=False)
            for _, row in sorted_df.iterrows():
                holdings_summary += f"- {row['Ticker']}: {row['Shares']} shares @ ${row['Current Price']:.2f} (Value: ${row['Market Value']:.2f})\n"
        else:
            holdings_summary = "No active holdings."

        context = f"""
PORTFOLIO SNAPSHOT
------------------
Total Value: ${total_value:,.2f}
Cash Balance: ${cash:,.2f}
Invested Value: ${invested:,.2f}

HOLDINGS:
{holdings_summary}
------------------
"""
        return context

    def ingest_statement(self, file_path, broker="trading212"):
        """
        Updates the portfolio from a PDF statement.
        Supports multiple brokers via 'broker' argument.
        """
        # Note: We no longer need read_pdf here as the parser handles file opening
        
        if broker == "trading212":
            from src.parsers.trading212 import Trading212Parser
            parser = Trading212Parser()
            # FIX: Pass file_path, not text
            data = parser.parse(file_path)
        else:
            return "Broker not supported."
            
        # Update Account Info
        if data['summary']:
            self.account_info.update(data['summary'])
            with open(self.account_info_path, 'w') as f:
                json.dump(self.account_info, f, indent=4)
        
        # Update Holdings
        new_holdings = data['holdings']
        if new_holdings:
            # Create new DataFrame from parsed holdings
            new_df = pd.DataFrame(new_holdings)
            
            # Calculate Allocation
            total_val = new_df['Market Value'].sum()
            if total_val > 0:
                new_df['Allocation %'] = (new_df['Market Value'] / total_val) * 100
            else:
                new_df['Allocation %'] = 0
                
            self.df = new_df
            self.df.to_csv(self.portfolio_path, index=False)
            
        # Update Transactions (New Feature)
        new_transactions = data.get('transactions', [])
        if new_transactions:
            trans_df = pd.DataFrame(new_transactions)
            trans_path = os.path.join(self.data_dir, 'transactions.csv')
            trans_df.to_csv(trans_path, index=False)
            
        return f"Imported {len(new_holdings)} holdings and {len(new_transactions)} transactions. Cash: ${self.get_cash_balance():,.2f}"

    def refresh_prices(self):
        # Re-implement using update_portfolio_prices logic but adapted for new schema if needed
        # For now, we rely on the statement prices or existing logic
        from src.utils.portfolio_manager import update_portfolio_prices
        return update_portfolio_prices()

# Global instance for easy import
data_manager = DataManager()
