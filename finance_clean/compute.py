"""
Core financial metric computation module with explicit formulas.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import yfinance as yf
from .fetch import get_financials
from .normalize import select_two_years, safe_get_field, safe_div, avg
from .validate import check_accounting_equation, collect_missing


def calculate_alpha(ticker: str, beta: float = None) -> float:
    """
    Calculate alpha using CAPM model against SPY benchmark.
    
    Args:
        ticker: Stock ticker symbol
        beta: Beta value (if None, will fetch from yfinance)
        
    Returns:
        Annualized alpha or None if calculation fails
    """
    try:
        # Get stock and SPY data for 3 years
        stock = yf.Ticker(ticker)
        spy = yf.Ticker("SPY")
        
        # Get 3 years of monthly data
        stock_data = stock.history(period="3y", interval="1mo")
        spy_data = spy.history(period="3y", interval="1mo")
        
        if stock_data.empty or spy_data.empty:
            return None
            
        # Calculate monthly returns
        stock_returns = stock_data['Close'].pct_change().dropna()
        spy_returns = spy_data['Close'].pct_change().dropna()
        
        # Align dates
        common_dates = stock_returns.index.intersection(spy_returns.index)
        if len(common_dates) < 12:  # Need at least 1 year of data
            return None
            
        stock_returns = stock_returns.loc[common_dates]
        spy_returns = spy_returns.loc[common_dates]
        
        # Get beta if not provided
        if beta is None:
            beta = stock.info.get('beta', 1.0)
            if beta is None or pd.isna(beta):
                beta = 1.0
        
        # Calculate alpha using CAPM: alpha = R_stock - (Rf + beta * (R_market - Rf))
        # Assuming risk-free rate is 0 for simplicity
        alpha_monthly = stock_returns.mean() - beta * spy_returns.mean()
        
        # Annualize alpha
        alpha_annual = alpha_monthly * 12
        
        return float(alpha_annual) if not pd.isna(alpha_annual) else None
        
    except Exception:
        return None




def compute_all(ticker: str) -> Dict[str, Any]:
    """
    Compute all financial metrics for a given ticker using explicit formulas.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with all computed metrics in deterministic order
    """
    try:
        # Fetch raw financial data
        raw_data = get_financials(ticker)
        
        # Select two most recent years with common columns
        data = select_two_years(raw_data)
        
        income = data['income']
        balance = data['balance']
        cashflow = data['cashflow']
        info = data['info']
        years = data['years']
        currency = data['currency']
        
        # Get year indices
        y_t = years[0]  # Most recent year
        y_t1 = years[1]  # Prior year
        
        # Initialize notes list for missing fields
        notes = []
        
        # Extract financial data using explicit field mappings
        # Income Statement
        TotalRevenue_t = safe_get_field(income, ['TotalRevenue'], y_t)
        TotalRevenue_t1 = safe_get_field(income, ['TotalRevenue'], y_t1)
        GrossProfit_t = safe_get_field(income, ['GrossProfit'], y_t)
        GrossProfit_t1 = safe_get_field(income, ['GrossProfit'], y_t1)
        OperatingIncome_t = safe_get_field(income, ['OperatingIncome'], y_t)
        OperatingIncome_t1 = safe_get_field(income, ['OperatingIncome'], y_t1)
        NetIncome_t = safe_get_field(income, ['NetIncome'], y_t)
        NetIncome_t1 = safe_get_field(income, ['NetIncome'], y_t1)
        PretaxIncome_t = safe_get_field(income, ['PretaxIncome'], y_t)
        SellingGeneralAdministrative_t = safe_get_field(income, ['SellingGeneralAdministrative'], y_t)
        SellingGeneralAdministrative_t1 = safe_get_field(income, ['SellingGeneralAdministrative'], y_t1)
        IncomeTaxExpense_t = safe_get_field(income, ['IncomeTaxExpense'], y_t)
        InterestExpense_t = safe_get_field(income, ['InterestExpense'], y_t)
        
        # Balance Sheet
        TotalAssets_t = safe_get_field(balance, ['TotalAssets'], y_t)
        TotalAssets_t1 = safe_get_field(balance, ['TotalAssets'], y_t1)
        TotalLiabilities_t = safe_get_field(balance, ['TotalLiabilities'], y_t)
        TotalLiabilities_t1 = safe_get_field(balance, ['TotalLiabilities'], y_t1)
        TotalStockholderEquity_t = safe_get_field(balance, ['TotalStockholderEquity'], y_t)
        TotalStockholderEquity_t1 = safe_get_field(balance, ['TotalStockholderEquity'], y_t1)
        TotalCurrentAssets_t = safe_get_field(balance, ['TotalCurrentAssets'], y_t)
        TotalCurrentLiabilities_t = safe_get_field(balance, ['TotalCurrentLiabilities'], y_t)
        Inventory_t = safe_get_field(balance, ['Inventory'], y_t)
        NetPPE_t = safe_get_field(balance, ['NetPPE'], y_t)
        NetPPE_t1 = safe_get_field(balance, ['NetPPE'], y_t1)
        RetainedEarnings_t = safe_get_field(balance, ['RetainedEarnings'], y_t)
        NetReceivables_t = safe_get_field(balance, ['NetReceivables'], y_t)
        NetReceivables_t1 = safe_get_field(balance, ['NetReceivables'], y_t1)
        
        # Cash Flow
        TotalCashFromOperatingActivities_t = safe_get_field(cashflow, ['TotalCashFromOperatingActivities'], y_t)
        TotalCashFromOperatingActivities_t1 = safe_get_field(cashflow, ['TotalCashFromOperatingActivities'], y_t1)
        Depreciation_t = safe_get_field(cashflow, ['Depreciation'], y_t)
        Depreciation_t1 = safe_get_field(cashflow, ['Depreciation'], y_t1)
        CashDividendsPaid_t = safe_get_field(cashflow, ['CashDividendsPaid'], y_t)
        
        # Market data from info
        shares = info.get('sharesOutstanding', np.nan)
        price = info.get('currentPrice') or info.get('regularMarketPrice', np.nan)
        dividend_rate = info.get('dividendRate', np.nan)
        book_value = info.get('bookValue', np.nan)
        
        # Calculate averages for ROE/ROA
        avg_assets = avg(TotalAssets_t, TotalAssets_t1)
        avg_equity = avg(TotalStockholderEquity_t, TotalStockholderEquity_t1)
        
        # Core ratios (explicit formulas)
        current_ratio = safe_div(TotalCurrentAssets_t, TotalCurrentLiabilities_t)
        quick_ratio = safe_div(TotalCurrentAssets_t - Inventory_t, TotalCurrentLiabilities_t)
        debt_to_equity = safe_div(TotalLiabilities_t, TotalStockholderEquity_t)
        roe = safe_div(NetIncome_t, avg_equity)
        roa = safe_div(NetIncome_t, avg_assets)
        
        # DuPont Analysis
        npm = safe_div(NetIncome_t, TotalRevenue_t)
        asset_turnover = safe_div(TotalRevenue_t, avg_assets)
        equity_multiplier = safe_div(TotalAssets_t, TotalStockholderEquity_t)
        roe_dupont_3 = npm * asset_turnover * equity_multiplier
        
        # 5-step DuPont
        tax_burden = safe_div(NetIncome_t, PretaxIncome_t) if not pd.isna(PretaxIncome_t) and PretaxIncome_t != 0 else np.nan
        interest_burden = safe_div(PretaxIncome_t, OperatingIncome_t) if not pd.isna(OperatingIncome_t) and OperatingIncome_t != 0 else np.nan
        operating_margin = safe_div(OperatingIncome_t, TotalRevenue_t)
        roe_dupont_5 = tax_burden * interest_burden * operating_margin * asset_turnover * equity_multiplier
        
        # ROE Adjusted (always provided when inputs exist)
        roe_adjusted = roe_dupont_3
        
        # Price-based ratios
        eps_t = safe_div(NetIncome_t, shares) if not pd.isna(shares) and shares > 0 else np.nan
        eps_t1 = safe_div(NetIncome_t1, shares) if not pd.isna(shares) and shares > 0 else np.nan
        bps_t = safe_div(TotalStockholderEquity_t, shares) if not pd.isna(shares) and shares > 0 else book_value
        sps_t = safe_div(TotalRevenue_t, shares) if not pd.isna(shares) and shares > 0 else np.nan
        growth_eps = safe_div(eps_t - eps_t1, eps_t1) if not pd.isna(eps_t1) and eps_t1 > 0 else np.nan
        
        pe = safe_div(price, eps_t)
        pb = safe_div(price, bps_t)
        ps = safe_div(price, sps_t)
        peg = safe_div(pe, 100 * growth_eps) if not pd.isna(pe) and not pd.isna(growth_eps) and growth_eps > 0 else np.nan
        
        # Dividend metrics
        div_ps = dividend_rate if not pd.isna(dividend_rate) else safe_div(-CashDividendsPaid_t, shares) if not pd.isna(CashDividendsPaid_t) and not pd.isna(shares) and shares > 0 else np.nan
        dividend_yield = safe_div(div_ps, price)
        dividend_payout_ratio = safe_div(div_ps, eps_t) if not pd.isna(eps_t) and eps_t > 0 else np.nan
        dividend_coverage_ratio = safe_div(eps_t, div_ps) if not pd.isna(div_ps) and div_ps > 0 else np.nan
        
        # Piotroski F-Score (0-9, two-year signals)
        ROA_t = safe_div(NetIncome_t, TotalAssets_t)
        ROA_t1 = safe_div(NetIncome_t1, TotalAssets_t1)
        CFO_t = TotalCashFromOperatingActivities_t
        
        # Get prior year values for Piotroski F6
        TotalCurrentAssets_t1 = safe_get_field(balance, ['TotalCurrentAssets'], y_t1)
        TotalCurrentLiabilities_t1 = safe_get_field(balance, ['TotalCurrentLiabilities'], y_t1)
        
        # Calculate Piotroski signals
        piotroski_signals = {
            'F1': 1 if ROA_t > 0 else 0,
            'F2': 1 if CFO_t > 0 else 0,
            'F3': 1 if ROA_t > ROA_t1 else 0,
            'F4': 1 if CFO_t > NetIncome_t else 0,
            'F5': 1 if safe_div(TotalLiabilities_t, TotalAssets_t) < safe_div(TotalLiabilities_t1, TotalAssets_t1) else 0,
            'F6': 1 if safe_div(TotalCurrentAssets_t, TotalCurrentLiabilities_t) > safe_div(TotalCurrentAssets_t1, TotalCurrentLiabilities_t1) else 0,
            'F7': 1 if shares <= shares else 0,  # Simplified: assume no share dilution
            'F8': 1 if safe_div(GrossProfit_t, TotalRevenue_t) > safe_div(GrossProfit_t1, TotalRevenue_t1) else 0,
            'F9': 1 if safe_div(TotalRevenue_t, TotalAssets_t) > safe_div(TotalRevenue_t1, TotalAssets_t1) else 0
        }
        
        piotroski_score = sum(piotroski_signals.values())
        piotroski_fscore_display = f"{piotroski_score:.2f}/9"
        
        # Beneish components
        COGS_t = TotalRevenue_t - GrossProfit_t if not pd.isna(TotalRevenue_t) and not pd.isna(GrossProfit_t) else np.nan
        COGS_t1 = TotalRevenue_t1 - GrossProfit_t1 if not pd.isna(TotalRevenue_t1) and not pd.isna(GrossProfit_t1) else np.nan
        
        DSRI = safe_div(safe_div(NetReceivables_t, TotalRevenue_t), safe_div(NetReceivables_t1, TotalRevenue_t1))
        GMI = safe_div(safe_div(GrossProfit_t1, TotalRevenue_t1), safe_div(GrossProfit_t, TotalRevenue_t))
        AQI = safe_div(1 - safe_div(TotalCurrentAssets_t + NetPPE_t, TotalAssets_t), 1 - safe_div(safe_get_field(balance, ['TotalCurrentAssets'], y_t1) + NetPPE_t1, TotalAssets_t1))
        SGI = safe_div(TotalRevenue_t, TotalRevenue_t1)
        DEPI = safe_div(safe_div(Depreciation_t1, Depreciation_t1 + NetPPE_t1), safe_div(Depreciation_t, Depreciation_t + NetPPE_t))
        SGAI = safe_div(safe_div(SellingGeneralAdministrative_t, TotalRevenue_t), safe_div(SellingGeneralAdministrative_t1, TotalRevenue_t1))
        LVGI = safe_div(safe_div(TotalLiabilities_t, TotalAssets_t), safe_div(TotalLiabilities_t1, TotalAssets_t1))
        TATA = safe_div(OperatingIncome_t - TotalCashFromOperatingActivities_t, TotalAssets_t)
        
        # Beneish M-Score calculation
        beneish_components = {
            'DSRI': DSRI,
            'GMI': GMI,
            'AQI': AQI,
            'SGI': SGI,
            'DEPI': DEPI,
            'SGAI': SGAI,
            'LVGI': LVGI,
            'TATA': TATA
        }
        
        # Check if all components are available for M-Score
        missing_components = [k for k, v in beneish_components.items() if pd.isna(v)]
        if missing_components:
            beneish_m_score = None
            beneish_reason = f"insufficient_fields: {', '.join(missing_components)}"
        else:
            beneish_m_score = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI + 0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI
            beneish_reason = None
        
        # Altman Z-Score calculation
        # Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
        # A = Working Capital / Total Assets
        # B = Retained Earnings / Total Assets  
        # C = EBIT / Total Assets
        # D = Market Value of Equity / Total Liabilities
        # E = Sales / Total Assets
        
        working_capital = TotalCurrentAssets_t - TotalCurrentLiabilities_t
        retained_earnings = safe_get_field(balance, ['RetainedEarnings'], y_t)
        ebit = OperatingIncome_t  # EBIT = Operating Income
        
        altman_a = safe_div(working_capital, TotalAssets_t)
        altman_b = safe_div(retained_earnings, TotalAssets_t)
        altman_c = safe_div(ebit, TotalAssets_t)
        altman_d = safe_div(TotalStockholderEquity_t, TotalLiabilities_t)  # Using book value as proxy for market value
        altman_e = safe_div(TotalRevenue_t, TotalAssets_t)
        
        # Check if all components are available
        altman_components = [altman_a, altman_b, altman_c, altman_d, altman_e]
        if any(pd.isna(comp) for comp in altman_components):
            altman_z_score = None
            altman_reason = "insufficient_fields: missing working capital, retained earnings, EBIT, equity, or revenue data"
        else:
            altman_z_score = 1.2*altman_a + 1.4*altman_b + 3.3*altman_c + 0.6*altman_d + 1.0*altman_e
            altman_reason = None
        
        # Calculate alpha using CAPM
        beta = info.get('beta', 1.0)
        if beta is None or pd.isna(beta):
            beta = 1.0
        alpha = calculate_alpha(ticker, beta)
        
        # Validation
        validation = check_accounting_equation(balance)
        
        # Collect missing fields
        needed_fields = {
            'income': ['TotalRevenue', 'GrossProfit', 'OperatingIncome', 'NetIncome', 'SellingGeneralAdministrative', 'IncomeTaxExpense', 'InterestExpense'],
            'balance': ['TotalAssets', 'TotalLiabilities', 'TotalStockholderEquity', 'TotalCurrentAssets', 'TotalCurrentLiabilities', 'Inventory', 'NetPPE', 'RetainedEarnings', 'NetReceivables'],
            'cashflow': ['TotalCashFromOperatingActivities', 'Depreciation', 'CashDividendsPaid']
        }
        
        missing_fields = collect_missing({'income': income, 'balance': balance, 'cashflow': cashflow}, needed_fields)
        if missing_fields:
            notes.extend([f"Missing field: {field}" for field in missing_fields])
        
        # Return deterministic structure with consistent key ordering
        return {
            "ticker": ticker,
            "currency": currency,
            "years": [str(y) for y in years],
            "validation": validation,
            "ratios": {
                "current": round(current_ratio, 4) if not pd.isna(current_ratio) else None,
                "quick": round(quick_ratio, 4) if not pd.isna(quick_ratio) else None,
                "debt_to_equity": round(debt_to_equity, 4) if not pd.isna(debt_to_equity) else None,
                "roe": round(roe, 4) if not pd.isna(roe) else None,
                "roa": round(roa, 4) if not pd.isna(roa) else None,
                "roe_adjusted": round(roe_adjusted, 4) if not pd.isna(roe_adjusted) else None
            },
            "dupont": {
                "roe_3step": {
                    "npm": round(npm, 4) if not pd.isna(npm) else None,
                    "asset_turnover": round(asset_turnover, 4) if not pd.isna(asset_turnover) else None,
                    "equity_multiplier": round(equity_multiplier, 4) if not pd.isna(equity_multiplier) else None,
                    "roe": round(roe_dupont_3, 4) if not pd.isna(roe_dupont_3) else None
                },
                "roe_5step": {
                    "tax_burden": round(tax_burden, 4) if not pd.isna(tax_burden) else None,
                    "interest_burden": round(interest_burden, 4) if not pd.isna(interest_burden) else None,
                    "operating_margin": round(operating_margin, 4) if not pd.isna(operating_margin) else None,
                    "asset_turnover": round(asset_turnover, 4) if not pd.isna(asset_turnover) else None,
                    "equity_multiplier": round(equity_multiplier, 4) if not pd.isna(equity_multiplier) else None,
                    "roe": round(roe_dupont_5, 4) if not pd.isna(roe_dupont_5) else None
                }
            },
            "piotroski": {
                "score": round(piotroski_score, 2),
                "fscore_display": piotroski_fscore_display,
                "signals": piotroski_signals
            },
            "beneish": {
                "m": round(beneish_m_score, 4) if beneish_m_score is not None else None,
                "reason": beneish_reason,
                "components": {k: round(v, 4) if not pd.isna(v) else None for k, v in beneish_components.items()}
            },
            "altman": {
                "z": round(altman_z_score, 4) if altman_z_score is not None else None,
                "z_prime": None,  # Not implemented yet
                "reason": altman_reason,
                "components": {
                    "a": round(altman_a, 4) if not pd.isna(altman_a) else None,
                    "b": round(altman_b, 4) if not pd.isna(altman_b) else None,
                    "c": round(altman_c, 4) if not pd.isna(altman_c) else None,
                    "d": round(altman_d, 4) if not pd.isna(altman_d) else None,
                    "e": round(altman_e, 4) if not pd.isna(altman_e) else None
                }
            },
            "price_based": {
                "pe": round(pe, 4) if not pd.isna(pe) else None,
                "pb": round(pb, 4) if not pd.isna(pb) else None,
                "ps": round(ps, 4) if not pd.isna(ps) else None,
                "peg": round(peg, 4) if not pd.isna(peg) else None
            },
            "dividends": {
                "dividend_yield": round(dividend_yield, 4) if not pd.isna(dividend_yield) else None,
                "dividend_payout_ratio": round(dividend_payout_ratio, 4) if not pd.isna(dividend_payout_ratio) else None,
                "dividend_coverage_ratio": round(dividend_coverage_ratio, 4) if not pd.isna(dividend_coverage_ratio) else None
            },
            "alpha": round(alpha, 4) if alpha is not None and not pd.isna(alpha) else None,
            "notes": notes
        }
        
    except Exception as e:
        return {
            "ticker": ticker,
            "error": str(e),
            "currency": "Unknown",
            "years": [],
            "validation": {},
            "ratios": {},
            "dupont": {},
            "piotroski": {"score": None, "fscore_display": "N/A", "signals": {}},
            "beneish": {"m": None, "reason": f"computation_error: {str(e)}", "components": {}},
            "altman": {"z": None, "z_prime": None, "reason": f"computation_error: {str(e)}", "components": {}},
            "price_based": {},
            "dividends": {},
            "alpha": None,
            "notes": [f"Error: {str(e)}"]
        }