import functools
import traceback
import numpy as np

def valuation_guard(func):
    """
    Decorator to catch NaN, Infinity, or Exceptions in Valuation Logic.
    Returns a 'Safe Failure' dictionary to prevent UI crashes.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # Post-check validation: Catch NaN/Inf in critical outputs
            if "r_implied" in result:
                if np.isnan(result["r_implied"]) or np.isinf(result["r_implied"]):
                    raise ValueError(f"Implied WACC is invalid: {result['r_implied']}")
            if "proj_prices" in result:
                for price in result["proj_prices"]:
                    if np.isnan(price) or np.isinf(price):
                        raise ValueError(f"Projected price contains invalid value: {price}")
            
            return result
            
        except Exception as e:
            print(f"CRITICAL VALUATION ERROR: {str(e)}")
            traceback.print_exc()
            
            # Return Safe Default Structure
            return {
                "proj_years": [2024],
                "proj_prices": [100.0], # Default safe price
                "table_data": [],
                "implied_drift": 0.0,
                "r_implied": 0.10,
                "net_cash_per_share": 0.0,
                "error": str(e) # Pass error to be handled if needed
            }
    return wrapper
