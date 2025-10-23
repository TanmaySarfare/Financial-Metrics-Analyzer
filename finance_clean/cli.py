"""
Command-line interface for finance_clean module.
"""

import json
import argparse
import sys
import pandas as pd
import numpy as np
from .compute import compute_all


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Financial Metrics Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m finance_clean.cli --ticker AAPL
  python -m finance_clean.cli --ticker MSFT --format table
  python -m finance_clean.cli --ticker GOOGL --verbose
  python -m finance_clean.cli --ticker AAPL --strict
        """
    )
    
    parser.add_argument(
        "--ticker", 
        required=True,
        help="Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include detailed validation and data quality information"
    )
    
    parser.add_argument(
        "--dump",
        action="store_true",
        help="Dump full JSON output with sorted keys"
    )
    
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Raise error on validation failure or missing core fields"
    )
    
    args = parser.parse_args()
    
    try:
        # Compute financial metrics
        result = compute_all(args.ticker)
        
        # Check for errors
        if "error" in result:
            if args.strict:
                raise ValueError(f"Computation failed: {result['error']}")
            else:
                print(f"Warning: {result['error']}", file=sys.stderr)
        
        # Check validation in strict mode
        if args.strict:
            validation = result.get("validation", {})
            for year, val in validation.items():
                if not val.get("ok", False):
                    raise ValueError(f"Accounting equation validation failed for {year}: delta={val.get('delta', 'N/A')}")
        
        if args.dump:
            # Full JSON dump with sorted keys
            output = result
        elif not args.verbose:
            # Simplified output
            output = {
                "ticker": result["ticker"],
                "currency": result["currency"],
                "years": result["years"],
                "ratios": result["ratios"],
                "dupont": result.get("dupont", {}),
                "piotroski": result.get("piotroski", {}),
                "beneish": result.get("beneish", {}),
                "price_based": result.get("price_based", {}),
                "dividends": result.get("dividends", {})
            }
        else:
            # Full output
            output = result
        
        if args.format == "json":
            # Sort keys for deterministic output
            if args.dump:
                print(json.dumps(output, indent=2, default=str, sort_keys=True))
            else:
                print(json.dumps(output, indent=2, default=str))
        else:
            # Table format
            print_table_output(output)
            
    except Exception as e:
        print(f"Error processing {args.ticker}: {str(e)}", file=sys.stderr)
        sys.exit(1)


def print_table_output(data):
    """Print output in a formatted table."""
    print(f"\n{'='*60}")
    print(f"FINANCIAL ANALYSIS: {data['ticker']}")
    print(f"{'='*60}")
    
    print(f"\nCurrency: {data['currency']}")
    if 'years' in data and len(data['years']) >= 2:
        print(f"Years: {data['years'][0]} - {data['years'][1]}")
    
    if 'ratios' in data:
        print(f"\n{'FINANCIAL RATIOS':<30}")
        print(f"{'-'*30}")
        for ratio, value in data['ratios'].items():
            if isinstance(value, (int, float)) and not pd.isna(value):
                if 'roe' in ratio or 'roa' in ratio:
                    print(f"{ratio.replace('_', ' ').title():<25}: {value:.2%}")
                else:
                    print(f"{ratio.replace('_', ' ').title():<25}: {value:.4f}")
            else:
                print(f"{ratio.replace('_', ' ').title():<25}: N/A")
    
    if 'dupont' in data:
        print(f"\n{'DUPONT ANALYSIS':<30}")
        print(f"{'-'*30}")
        if 'roe_3step' in data['dupont']:
            roe3 = data['dupont']['roe_3step']
            print(f"3-Step ROE: {roe3.get('roe', 0):.2%}")
            print(f"  Net Profit Margin: {roe3.get('npm', 0):.2%}")
            print(f"  Asset Turnover: {roe3.get('asset_turnover', 0):.4f}")
            print(f"  Equity Multiplier: {roe3.get('equity_multiplier', 0):.4f}")
        if 'roe_5step' in data['dupont']:
            roe5 = data['dupont']['roe_5step']
            print(f"5-Step ROE: {roe5.get('roe', 0):.2%}")
    
    if 'piotroski' in data:
        print(f"\n{'PIOTROSKI F-SCORE':<30}")
        print(f"{'-'*30}")
        piotroski = data['piotroski']
        if 'fscore_display' in piotroski:
            print(f"F-Score: {piotroski['fscore_display']}")
        else:
            score = piotroski.get('score', np.nan)
            if not pd.isna(score):
                print(f"F-Score: {score:.2f}/9")
            else:
                print("F-Score: N/A")
        
        signals = piotroski.get('signals', {})
        for signal, value in signals.items():
            print(f"  {signal}: {'✓' if value == 1 else '✗'}")
    
    if 'beneish' in data:
        print(f"\n{'BENEISH M-SCORE':<30}")
        print(f"{'-'*30}")
        beneish = data['beneish']
        if beneish.get('m') is not None:
            print(f"M-Score: {beneish['m']:.4f}")
        else:
            print(f"M-Score: N/A ({beneish.get('reason', 'Unknown reason')})")
        
        components = beneish.get('components', {})
        for comp, value in components.items():
            if value is not None:
                print(f"  {comp}: {value:.4f}")
            else:
                print(f"  {comp}: N/A")
    
    if 'price_based' in data:
        print(f"\n{'PRICE-BASED RATIOS':<30}")
        print(f"{'-'*30}")
        for ratio, value in data['price_based'].items():
            if value is not None:
                print(f"{ratio.upper():<25}: {value:.4f}")
            else:
                print(f"{ratio.upper():<25}: N/A")
    
    if 'dividends' in data:
        print(f"\n{'DIVIDEND METRICS':<30}")
        print(f"{'-'*30}")
        for metric, value in data['dividends'].items():
            if value is not None:
                if 'yield' in metric or 'payout' in metric:
                    print(f"{metric.replace('_', ' ').title():<25}: {value:.2%}")
                else:
                    print(f"{metric.replace('_', ' ').title():<25}: {value:.4f}")
            else:
                print(f"{metric.replace('_', ' ').title():<25}: N/A")
    
    if 'validation' in data:
        print(f"\n{'ACCOUNTING VALIDATION':<30}")
        print(f"{'-'*30}")
        for year, validation in data['validation'].items():
            status = "✓ PASS" if validation.get('ok', False) else "✗ FAIL"
            delta = validation.get('delta', 'N/A')
            if isinstance(delta, (int, float)):
                print(f"{year}: {status} (delta: {delta:.4f})")
            else:
                print(f"{year}: {status} (delta: {delta})")
    
    if 'notes' in data and data['notes']:
        print(f"\n{'NOTES':<30}")
        print(f"{'-'*30}")
        for note in data['notes']:
            print(f"• {note}")
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()