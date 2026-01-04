"""
DataManager - Refactored with SQLite Backend
=============================================
Thread-safe data persistence using SQLite instead of CSV/JSON.
Maintains backward-compatible API for existing callers.
"""
import pandas as pd
import os
import logging
from typing import Dict, Any, List, Optional

# Import SQLite database layer
from src.utils import db

logger = logging.getLogger("DataManager")


class DataManager:
    """Singleton DataManager with SQLite persistence."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        
        # Robust path finding (kept for legacy CSV migration)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(current_dir))
        self.data_dir = os.path.join(self.project_root, 'data')
        self.portfolio_path = os.path.join(self.data_dir, 'master_portfolio.csv')  # Legacy
        self.account_info_path = os.path.join(self.data_dir, 'account_info.json')  # Legacy
        
        # In-memory cache for DataFrame (for backward compatibility)
        self._df_cache = None
        self._account_cache = None
        
        # Migrate existing CSV/JSON data to SQLite if needed
        self._migrate_legacy_data()
        
        self.load_data()
        self.initialized = True

    def _migrate_legacy_data(self):
        """One-time migration of CSV/JSON data to SQLite."""
        import json
        
        # Migrate CSV portfolio if exists and DB is empty
        if os.path.exists(self.portfolio_path):
            holdings = db.get_all_holdings()
            if not holdings:  # Only migrate if DB is empty
                try:
                    df = pd.read_csv(self.portfolio_path)
                    for _, row in df.iterrows():
                        db.upsert_holding(row.to_dict())
                    logger.info(f"Migrated {len(df)} holdings from CSV to SQLite")
                except Exception as e:
                    logger.error(f"CSV migration failed: {e}")
        
        # Migrate JSON account info if exists
        if os.path.exists(self.account_info_path):
            account_info = db.get_all_account_info()
            if not account_info:  # Only migrate if DB is empty
                try:
                    with open(self.account_info_path, 'r') as f:
                        data = json.load(f)
                    for key, value in data.items():
                        db.set_account_value(key, value)
                    logger.info(f"Migrated account info to SQLite")
                except Exception as e:
                    logger.error(f"JSON migration failed: {e}")

    def load_data(self):
        """Loads portfolio and account info from SQLite."""
        # Load Holdings from SQLite
        holdings = db.get_all_holdings()
        if holdings:
            # Convert to DataFrame for backward compatibility
            self._df_cache = pd.DataFrame(holdings)
            # Rename DB columns to legacy column names
            column_map = {
                'ticker': 'Ticker',
                'isin': 'ISIN',
                'currency': 'Currency',
                'shares': 'Shares',
                'opening_price': 'Opening Price',
                'current_price': 'Current Price',
                'unrealised_pl': 'Unrealised P/L',
                'value_source': 'Value (Source)',
                'fx_rate': 'FX Rate',
                'unrealised_pl_base': 'Unrealised P/L (Base)',
                'market_value': 'Market Value',
                'allocation_pct': 'Allocation %'
            }
            self._df_cache.rename(columns=column_map, inplace=True)
        else:
            self._df_cache = pd.DataFrame(columns=[
                "Ticker", "ISIN", "Currency", "Shares", "Opening Price", 
                "Current Price", "Unrealised P/L", "Value (Source)", 
                "FX Rate", "Unrealised P/L (Base)", "Market Value", "Allocation %"
            ])
        
        # Load Account Info from SQLite
        self._account_cache = db.get_all_account_info()
        if not self._account_cache:
            self._account_cache = {"Free Funds": 10000.0, "Account Value": 0.0}

    # Backward compatibility alias
    def load_portfolio(self):
        return self.load_data()

    @property
    def df(self):
        """Property for backward compatibility with self.df access."""
        if self._df_cache is None:
            self.load_data()
        return self._df_cache
    
    @df.setter
    def df(self, value):
        """Setter to intercept DataFrame assignments and persist to SQLite."""
        self._df_cache = value
        # Persist to SQLite
        if value is not None and not value.empty:
            db.clear_holdings()
            for _, row in value.iterrows():
                db.upsert_holding(row.to_dict())

    @property
    def account_info(self):
        """Property for backward compatibility with self.account_info access."""
        if self._account_cache is None:
            self.load_data()
        return self._account_cache
    
    @account_info.setter
    def account_info(self, value):
        """Setter to intercept account_info assignments and persist to SQLite."""
        self._account_cache = value
        # Persist to SQLite
        if value:
            for key, val in value.items():
                db.set_account_value(key, val)

    def get_portfolio_df(self):
        if self._df_cache is None:
            self.load_data()
        return self._df_cache

    def get_total_value(self):
        if self.account_info.get("Account Value", 0) > 0:
            return self.account_info["Account Value"]
        return self.get_holdings_value() + self.get_cash_balance()

    def get_holdings_value(self):
        if self._df_cache is None or self._df_cache.empty:
            return 0.0
        return self._df_cache['Market Value'].sum()

    def get_cash_balance(self):
        return self.account_info.get("Free Funds", 0.0)

    def get_holdings_list(self):
        if self._df_cache is None or self._df_cache.empty:
            return []
        return self._df_cache['Ticker'].tolist()

    def get_portfolio_context(self):
        total_value = self.get_total_value()
        cash = self.get_cash_balance()
        invested = self.get_holdings_value()
        
        holdings_summary = ""
        if self._df_cache is not None and not self._df_cache.empty:
            sorted_df = self._df_cache.sort_values(by='Market Value', ascending=False)
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
        Now persists directly to SQLite.
        """
        if broker == "trading212":
            from src.parsers.trading212 import Trading212Parser
            parser = Trading212Parser()
            data = parser.parse(file_path)
        else:
            return "Broker not supported."
            
        # Update Account Info in SQLite
        if data['summary']:
            for key, value in data['summary'].items():
                db.set_account_value(key, value)
            self._account_cache = db.get_all_account_info()
        
        # Update Holdings in SQLite
        new_holdings = data['holdings']
        if new_holdings:
            db.clear_holdings()  # Full refresh
            
            # Calculate Allocation
            total_val = sum(h.get('Market Value', 0) for h in new_holdings)
            
            for holding in new_holdings:
                if total_val > 0:
                    holding['Allocation %'] = (holding.get('Market Value', 0) / total_val) * 100
                else:
                    holding['Allocation %'] = 0
                db.upsert_holding(holding)
            
            # Refresh cache
            self.load_data()
            
        # Update Transactions in SQLite
        new_transactions = data.get('transactions', [])
        for trans in new_transactions:
            db.insert_transaction(trans)
            
        return f"Imported {len(new_holdings)} holdings and {len(new_transactions)} transactions. Cash: ${self.get_cash_balance():,.2f}"

    def refresh_prices(self):
        from src.utils.portfolio_manager import update_portfolio_prices
        return update_portfolio_prices()


# Global instance for easy import
data_manager = DataManager()
