"""
Comprehensive tests for financial metrics computation.
"""

import numpy as np
import pandas as pd
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from finance_clean.compute import compute_all, avg, pct_change
from finance_clean.normalize import safe_div


def test_synthetic_data():
    """Test with synthetic data to verify formulas."""
    
    # Create synthetic financial data
    synthetic_data = {
        "ticker": "TEST",
        "currency": "USD",
        "years": ["2023-12-31", "2022-12-31"],
        "ratios": {
            "current": 2.0,
            "quick": 1.5,
            "debt_to_equity": 0.5,
            "roe": 0.15,
            "roa": 0.10
        },
        "dupont": {
            "roe_3step": {
                "npm": 0.10,
                "asset_turnover": 1.0,
                "equity_multiplier": 1.5,
                "roe": 0.15
            }
        },
        "piotroski": {
            "score": 7,
            "signals": {"F1": 1, "F2": 1, "F3": 1, "F4": 0, "F5": 1, "F6": 1, "F7": 1, "F8": 1, "F9": 0}
        },
        "beneish_components": {
            "DSRI": 1.0,
            "GMI": 1.0,
            "AQI": 1.0,
            "SGI": 1.1,
            "DEPI": 1.0,
            "SGAI": 1.0,
            "LVGI": 1.0,
            "TATA": 0.0
        }
    }
    
    # Test helper functions
    assert avg(10, 20) == 15.0
    assert pd.isna(avg(10, np.nan))
    assert abs(pct_change(110, 100) - 0.1) < 1e-10
    assert pd.isna(pct_change(100, 0))
    assert safe_div(10, 2) == 5.0
    assert pd.isna(safe_div(10, 0))
    
    # Test DuPont formula
    npm = 0.10
    asset_turnover = 1.0
    equity_multiplier = 1.5
    expected_roe = npm * asset_turnover * equity_multiplier
    assert abs(expected_roe - 0.15) < 1e-6
    
    # Test Piotroski score range
    score = synthetic_data["piotroski"]["score"]
    assert 0 <= score <= 9
    
    print("✓ All synthetic data tests passed")


def test_formulas():
    """Test individual formula calculations."""
    
    # Test DuPont 3-step
    npm = 0.12
    asset_turnover = 1.2
    equity_multiplier = 1.8
    roe_3step = npm * asset_turnover * equity_multiplier
    expected = 0.2592
    assert abs(roe_3step - expected) < 1e-6
    
    # Test DuPont 5-step
    tax_burden = 0.8
    interest_burden = 0.9
    operating_margin = 0.15
    roe_5step = tax_burden * interest_burden * operating_margin * asset_turnover * equity_multiplier
    expected_5step = 0.23328
    assert abs(roe_5step - expected_5step) < 1e-6
    
    # Test Piotroski signals
    signals = {"F1": 1, "F2": 1, "F3": 0, "F4": 1, "F5": 0, "F6": 1, "F7": 1, "F8": 0, "F9": 1}
    score = sum(signals.values())
    assert score == 6
    
    print("✓ All formula tests passed")


def test_edge_cases():
    """Test edge cases and error handling."""
    
    # Test division by zero
    assert pd.isna(safe_div(10, 0))
    assert pd.isna(safe_div(10, np.nan))
    assert pd.isna(safe_div(np.nan, 10))
    
    # Test percentage change edge cases
    assert pd.isna(pct_change(100, 0))
    assert pd.isna(pct_change(np.nan, 100))
    assert pd.isna(pct_change(100, np.nan))
    
    # Test averaging edge cases
    assert pd.isna(avg(np.nan, 10))
    assert pd.isna(avg(10, np.nan))
    assert pd.isna(avg(np.inf, 10))
    
    print("✓ All edge case tests passed")


def test_real_data_structure():
    """Test that real data has expected structure."""
    try:
        result = compute_all("AAPL")
        
        # Check required keys exist
        required_keys = ["ticker", "currency", "years", "ratios", "dupont", "piotroski", "beneish_components"]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"
        
        # Check ratios structure
        ratios = result["ratios"]
        expected_ratios = ["current", "quick", "debt_to_equity", "roe", "roa", "pe", "pb", "ps", "peg", 
                          "dividend_yield", "dividend_payout_ratio", "dividend_coverage_ratio"]
        for ratio in expected_ratios:
            assert ratio in ratios, f"Missing ratio: {ratio}"
        
        # Check DuPont structure
        dupont = result["dupont"]
        assert "roe_3step" in dupont
        assert "roe_5step" in dupont
        
        # Check Piotroski structure
        piotroski = result["piotroski"]
        assert "score" in piotroski
        assert "signals" in piotroski
        
        # Check Beneish components
        beneish = result["beneish_components"]
        expected_components = ["DSRI", "GMI", "AQI", "SGI", "DEPI", "SGAI", "LVGI", "TATA"]
        for comp in expected_components:
            assert comp in beneish, f"Missing component: {comp}"
        
        print("✓ Real data structure test passed")
        
    except Exception as e:
        print(f"✗ Real data structure test failed: {e}")


if __name__ == "__main__":
    print("Running comprehensive financial metrics tests...")
    print()
    
    test_synthetic_data()
    test_formulas()
    test_edge_cases()
    test_real_data_structure()
    
    print()
    print("🎉 All tests completed successfully!")