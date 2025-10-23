"""
Smoke tests for finance_clean module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finance_clean.compute import compute_all


def test_smoke():
    """Basic smoke test to ensure module works."""
    print("Running smoke test...")
    
    try:
        # Test with Apple
        result = compute_all("AAPL")
        
        # Basic structure validation
        assert "ratios" in result, "Missing ratios"
        assert "altman" in result, "Missing altman"
        assert "beneish" in result, "Missing beneish"
        assert len(result["years"]) == 2, "Should have 2 years"
        assert result["ticker"] == "AAPL", "Wrong ticker"
        
        # Check ratios exist
        required_ratios = ["current_ratio", "quick_ratio", "debt_to_equity", "roe", "roa"]
        for ratio in required_ratios:
            assert ratio in result["ratios"], f"Missing ratio: {ratio}"
        
        # Check Altman components
        assert "z" in result["altman"], "Missing Altman Z-score"
        assert "zone" in result["altman"], "Missing Altman zone"
        
        # Check Beneish components
        assert "m_score" in result["beneish"], "Missing Beneish M-score"
        assert "zone" in result["beneish"], "Missing Beneish zone"
        
        print("✓ Smoke test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Smoke test failed: {e}")
        return False


def test_multiple_tickers():
    """Test with multiple tickers."""
    tickers = ["AAPL", "MSFT", "GOOGL"]
    
    print("Testing multiple tickers...")
    
    for ticker in tickers:
        try:
            result = compute_all(ticker)
            assert result["ticker"] == ticker
            print(f"✓ {ticker} processed successfully")
        except Exception as e:
            print(f"✗ {ticker} failed: {e}")
            return False
    
    print("✓ Multiple ticker test passed!")
    return True


if __name__ == "__main__":
    success = True
    success &= test_smoke()
    success &= test_multiple_tickers()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
