"""
Financial data validation utilities.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List


def check_accounting_equation(balance_df: pd.DataFrame, tol: float = 0.01) -> Dict[str, Any]:
    """
    Validate the accounting equation: Assets = Liabilities + Equity
    
    Args:
        balance_df: Balance sheet DataFrame
        tol: Tolerance for validation (default 0.01 = 1%)
        
    Returns:
        Dictionary with validation results for each year
    """
    results = {}
    
    for col in balance_df.columns:
        try:
            # Get the three key components
            ta = safe_get_field(balance_df, ['TotalAssets'], col)
            tl = safe_get_field(balance_df, ['TotalLiabilities'], col)
            te = safe_get_field(balance_df, ['TotalStockholderEquity'], col)
            
            # Calculate difference as percentage of total assets
            if ta > 0:
                diff = abs(ta - (tl + te)) / ta
                results[str(col)] = {
                    "ok": diff <= tol,
                    "delta": diff,
                    "assets": ta,
                    "liabilities": tl,
                    "equity": te,
                    "calculated_total": tl + te
                }
            else:
                results[str(col)] = {
                    "ok": False,
                    "delta": float('inf'),
                    "error": "Total Assets is zero or missing"
                }
                
        except Exception as e:
            results[str(col)] = {
                "ok": False,
                "delta": float('inf'),
                "error": str(e)
            }
    
    return results


def collect_missing(df_map: Dict[str, pd.DataFrame], needed: Dict[str, List[str]]) -> List[str]:
    """
    Collect missing fields from DataFrames.
    
    Args:
        df_map: Dictionary mapping section names to DataFrames
        needed: Dictionary mapping section names to required field lists
        
    Returns:
        List of missing fields in format "section:field"
    """
    missing = []
    
    for section, fields in needed.items():
        if section not in df_map:
            missing.extend([f"{section}:{field}" for field in fields])
            continue
            
        df = df_map[section]
        for field in fields:
            if field not in df.index:
                missing.append(f"{section}:{field}")
    
    return missing


def safe_get_field(df: pd.DataFrame, field_names: List[str], year_idx: Any = None, default: float = np.nan) -> float:
    """
    Safely get a field value from DataFrame, trying multiple field names.
    
    Args:
        df: Input DataFrame
        field_names: List of possible field names to try
        year_idx: Year index to extract value for (if None, returns first non-null value)
        default: Default value if field not found
        
    Returns:
        Field value or default
    """
    for field_name in field_names:
        if field_name in df.index:
            value = df.loc[field_name]
            if isinstance(value, pd.Series):
                if year_idx is not None and year_idx in value.index:
                    # Return value for specific year
                    val = value[year_idx]
                    if not pd.isna(val):
                        return float(val)
                else:
                    # Return first non-null value from the series
                    for val in value:
                        if not pd.isna(val):
                            return float(val)
                return default
            else:
                # Single value
                if not pd.isna(value):
                    return float(value)
    return default