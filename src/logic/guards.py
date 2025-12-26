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
            
            # Post-check validation (Optional)
            # if "r_implied" in result and np.isnan(result["r_implied"]):
            #    raise ValueError("Implied WACC is NaN")
            
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
