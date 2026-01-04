"""
Configuration Settings for GVD Engine.
Centralizes all 'magic numbers' and default assumptions.
"""

# --- Valuation Parameters ---
TERMINAL_GROWTH_RATE = 0.03  # 3% Perpetuity Growth
DEFAULT_DISCOUNT_RATE = 0.10 # Initial WACC guess
GORDON_GUARD_BUFFER = 0.015  # 1.5% spread between r and g

# --- P/E Constraints ---
MIN_TARGET_PE = 5.0
MAX_TARGET_PE = 150.0

# --- Monte Carlo Settings ---
TRADING_DAYS = 252
MC_SIMULATIONS = 10000
MC_DRIFT_CAP_MULTIPLIER = 50.0 # Max 50x drift

# --- Data Defaults (Fallback) ---
DEFAULT_PRICE = 100.0
DEFAULT_REVENUE = 1_000_000_000.0
DEFAULT_EPS = 1.0
DEFAULT_SHARES = 1_000_000  # Fallback: Assume 1M shares to prevent division errors
