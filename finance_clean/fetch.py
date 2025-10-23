"""
Financial data fetching module using yfinance.
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any


def get_financials(ticker: str) -> Dict[str, Any]:
    """
    Fetch annual financials from yfinance.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing income statement, balance sheet, cash flow, and info
    """
    t = yf.Ticker(ticker)
    
    try:
        income = t.income_stmt
        balance = t.balance_sheet
        cashflow = t.cashflow
        info = t.info
        
        # Validate that we have data
        if (income is None or (hasattr(income, 'empty') and income.empty)) or \
           (balance is None or (hasattr(balance, 'empty') and balance.empty)) or \
           (cashflow is None or (hasattr(cashflow, 'empty') and cashflow.empty)):
            raise ValueError(f"No financial data available for ticker: {ticker}")
            
        return {
            "income": income,
            "balance": balance,
            "cashflow": cashflow,
            "info": info
        }
    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


def pick_two_years(fin: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the two most recent fiscal years from financial data.
    
    Args:
        fin: Financial data dictionary from get_financials
        
    Returns:
        Dictionary with income, balance, cashflow for two years plus metadata
    """
    # Get the two most recent years (columns are sorted newest first)
    yrs = fin["balance"].columns[:2]
    
    if len(yrs) < 2:
        raise ValueError("Need at least 2 years of financial data")
    
    # Extract data for the two years
    df_income = fin["income"].loc[:, yrs]
    df_balance = fin["balance"].loc[:, yrs]
    df_cash = fin["cashflow"].loc[:, yrs]
    
    currency = fin["info"].get("currency", "N/A")
    
    return {
        "income": df_income,
        "balance": df_balance,
        "cashflow": df_cash,
        "years": yrs,
        "currency": currency
    }


def coerce_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert DataFrame values to numeric, coercing errors to NaN.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with numeric values
    """
    return df.apply(pd.to_numeric, errors="coerce")


def ensure_units(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure consistent units across the DataFrame.
    Currently a placeholder - assumes data is already in base units.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with normalized units
    """
    # TODO: Implement unit normalization logic
    return df
