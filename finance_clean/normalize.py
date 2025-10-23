"""
Data normalization and preprocessing utilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple


def normalize_field_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize field names to standard accounting terms.
    
    Args:
        df: Input DataFrame with financial data
        
    Returns:
        DataFrame with normalized field names
    """
    # Common field name mappings
    field_mappings = {
        # Income Statement
        'Total Revenue': 'TotalRevenue',
        'Revenue': 'TotalRevenue',
        'Operating Revenue': 'TotalRevenue',
        'Net Sales': 'TotalRevenue',
        'Sales': 'TotalRevenue',
        
        'Cost Of Revenue': 'CostOfRevenue',
        'Cost of Goods Sold': 'CostOfRevenue',
        'COGS': 'CostOfRevenue',
        
        'Gross Profit': 'GrossProfit',
        'Gross Income': 'GrossProfit',
        
        'Operating Income': 'OperatingIncome',
        'EBIT': 'OperatingIncome',
        'Earnings Before Interest And Taxes': 'OperatingIncome',
        
        'Net Income': 'NetIncome',
        'Net Earnings': 'NetIncome',
        'Net Income Common Stockholders': 'NetIncome',
        
        'Pretax Income': 'PretaxIncome',
        'Income Before Tax': 'PretaxIncome',
        'Earnings Before Tax': 'PretaxIncome',
        
        'Selling General Administrative': 'SellingGeneralAdministrative',
        'Selling General And Administration': 'SellingGeneralAdministrative',
        'SG&A': 'SellingGeneralAdministrative',
        'Selling, General & Administrative': 'SellingGeneralAdministrative',
        
        'Income Tax Expense': 'IncomeTaxExpense',
        'Tax Provision': 'IncomeTaxExpense',
        'Income Tax': 'IncomeTaxExpense',
        
        'Interest Expense': 'InterestExpense',
        'Interest Paid': 'InterestExpense',
        
        # Balance Sheet
        'Total Assets': 'TotalAssets',
        'Total Current Assets': 'TotalCurrentAssets',
        'Current Assets': 'TotalCurrentAssets',
        
        'Total Liabilities': 'TotalLiabilities',
        'Total Liab': 'TotalLiabilities',
        'Total Liabilities Net Minority Interest': 'TotalLiabilities',
        'Total Liabilities And Stockholders Equity': 'TotalLiabilities',
        
        'Total Current Liabilities': 'TotalCurrentLiabilities',
        'Current Liabilities': 'TotalCurrentLiabilities',
        
        'Total Stockholder Equity': 'TotalStockholderEquity',
        'Total Equity': 'TotalStockholderEquity',
        'Stockholders Equity': 'TotalStockholderEquity',
        
        'Inventory': 'Inventory',
        'Net PPE': 'NetPPE',
        'Property Plant Equipment': 'NetPPE',
        'Net Property Plant Equipment': 'NetPPE',
        
        'Retained Earnings': 'RetainedEarnings',
        'Net Receivables': 'NetReceivables',
        'Accounts Receivable': 'NetReceivables',
        
        # Cash Flow
        'Total Cash From Operating Activities': 'TotalCashFromOperatingActivities',
        'Operating Cash Flow': 'TotalCashFromOperatingActivities',
        'Cash From Operations': 'TotalCashFromOperatingActivities',
        
        'Depreciation': 'Depreciation',
        'Depreciation And Amortization': 'Depreciation',
        
        'Cash Dividends Paid': 'CashDividendsPaid',
        'Dividends Paid': 'CashDividendsPaid',
    }
    
    # Create a copy to avoid modifying original
    df_normalized = df.copy()
    
    # Apply mappings
    new_index = []
    new_data = []
    seen_normalized = set()
    
    for i, field_name in enumerate(df_normalized.index):
        normalized_name = field_mappings.get(field_name, field_name)
        
        # Only keep first occurrence of each normalized name
        if normalized_name not in seen_normalized:
            new_index.append(normalized_name)
            seen_normalized.add(normalized_name)
            new_data.append(df_normalized.iloc[i])
    
    # Create new DataFrame with unique normalized names
    df_normalized = pd.DataFrame(new_data, index=new_index, columns=df_normalized.columns)
    
    return df_normalized


def select_two_years(financial_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Select two most recent fiscal years that exist in all three statements.
    
    Args:
        financial_data: Dict with 'income', 'balance', 'cashflow', 'info' DataFrames
        
    Returns:
        Dict with normalized DataFrames, years, and currency info
    """
    income = financial_data['income']
    balance = financial_data['balance'] 
    cashflow = financial_data['cashflow']
    info = financial_data['info']
    
    # Get common columns (years) across all three statements
    income_cols = set(income.columns)
    balance_cols = set(balance.columns)
    cashflow_cols = set(cashflow.columns)
    
    common_years = income_cols.intersection(balance_cols).intersection(cashflow_cols)
    
    if len(common_years) < 2:
        raise ValueError(f"Insufficient common years: {len(common_years)} found")
    
    # Sort years and take the two most recent
    sorted_years = sorted(common_years, reverse=True)[:2]
    
    # Normalize and coerce to numeric
    income_norm = normalize_field_names(income)
    balance_norm = normalize_field_names(balance)
    cashflow_norm = normalize_field_names(cashflow)
    
    # Coerce to numeric, errors='coerce' converts non-numeric to NaN
    income_norm = income_norm.apply(pd.to_numeric, errors='coerce')
    balance_norm = balance_norm.apply(pd.to_numeric, errors='coerce')
    cashflow_norm = cashflow_norm.apply(pd.to_numeric, errors='coerce')
    
    # Extract currency from info
    currency = info.get('currency', 'USD')
    
    return {
        'income': income_norm,
        'balance': balance_norm,
        'cashflow': cashflow_norm,
        'info': info,  # Keep info as-is
        'years': sorted_years,
        'currency': currency
    }


def safe_get_field(df: pd.DataFrame, field_names: list, year_idx: Any = None, default: float = np.nan) -> float:
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


def safe_div(numerator: float, denominator: float, default: float = np.nan) -> float:
    """
    Safe division that handles NaN and zero division.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails
        
    Returns:
        Division result or default
    """
    try:
        if pd.isna(numerator) or pd.isna(denominator):
            return default
        if abs(denominator) < 1e-12:
            return default
        result = float(numerator / denominator)
        # Check for infinity values
        if np.isinf(result):
            return default
        return result
    except (ValueError, TypeError, ZeroDivisionError):
        return default


def sanitize_for_json(value: Any) -> Any:
    """
    Sanitize values for JSON serialization by converting inf/nan to null.
    
    Args:
        value: Any value to sanitize
        
    Returns:
        JSON-safe value
    """
    if isinstance(value, (int, float)):
        if np.isnan(value) or np.isinf(value):
            return None
        return value
    elif isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    else:
        return value


def avg(x: float, y: float) -> float:
    """
    Calculate average of two values, return NaN if either is not finite.
    
    Args:
        x: First value
        y: Second value
        
    Returns:
        Average or NaN if either input is NaN
    """
    try:
        if pd.isna(x) or pd.isna(y):
            return np.nan
        x, y = float(x), float(y)
        if not np.isfinite(x) or not np.isfinite(y):
            return np.nan
        return (x + y) / 2.0
    except (ValueError, TypeError):
        return np.nan