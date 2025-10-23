from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache
from datetime import date
import json
import pandas as pd
from finance_clean.compute import compute_all
from finance_clean.normalize import sanitize_for_json

app = FastAPI(title="Financial Metrics API", version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:3000","http://127.0.0.1:3000","*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@lru_cache(maxsize=256)
def _cached_metrics(ticker:str,salt:str)->dict:
    return compute_all(ticker)

@app.get("/health")
def health():
    return {"ok":True}

@app.get("/metrics/{ticker}")
def metrics(ticker:str,force_refresh:bool=False):
    try:
        salt="" if force_refresh else str(date.today())
        res=_cached_metrics(ticker.upper(),salt)
        if not res or "ratios" not in res:raise HTTPException(status_code=502,detail="Computation failed")
        return res
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get("/metrics/{ticker}/dump")
def dump(ticker:str):
    try:
        res=compute_all(ticker.upper())
        return json.loads(json.dumps(res,default=str))
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get("/api/company/summary")
def company_summary(ticker:str):
    try:
        res=compute_all(ticker.upper())
        
        # Get company info directly from yfinance
        import yfinance as yf
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        response = {
            "ticker": res["ticker"],
            "ticker_normalized": res["ticker"],
            "exists": True,
            "instrument_type": "EQUITY",
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "real_time": {
                "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                "currency": res["currency"],
                "timestamp": "2024-01-01T00:00:00Z"
            },
            "beta": info.get("beta", 0),
            "alpha": res.get("alpha", 0),
            "data_quality": "complete" if not res.get("error") else "error",
            "missing": [],
            "audit": {
                "generated_at": "2024-01-01T00:00:00Z",
                "sources_used": ["yfinance"]
            }
        }
        
        # Sanitize the response for JSON serialization
        return sanitize_for_json(response)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get("/api/metrics/simple")
def metrics_simple(ticker:str, precision:int=4):
    try:
        res=compute_all(ticker.upper())
        
        # Round ratios to specified precision
        def round_ratio(value, decimals=precision):
            if value is None or pd.isna(value):
                return None
            return round(float(value), decimals)
        
        response = {
            "ticker": res["ticker"],
            "metrics": {
                "beneish_m_score": round_ratio(res.get("beneish", {}).get("m")),
                "beneish_reason": res.get("beneish", {}).get("reason"),
                "beneish_components": {k: round_ratio(v) for k, v in res.get("beneish", {}).get("components", {}).items()},
                "altman": {
                    "z": round_ratio(res.get("altman", {}).get("z")),
                    "z_prime": round_ratio(res.get("altman", {}).get("z_prime"))
                },
                "ratios": {
                    "current": round_ratio(res["ratios"].get("current")),
                    "quick": round_ratio(res["ratios"].get("quick")),
                    "debt_to_equity": round_ratio(res["ratios"].get("debt_to_equity")),
                    "roe": round_ratio(res["ratios"].get("roe")),
                    "roe_adjusted": round_ratio(res["ratios"].get("roe_adjusted")),
                    "roa": round_ratio(res["ratios"].get("roa")),
                    "pe": round_ratio(res["price_based"].get("pe")),
                    "pb": round_ratio(res["price_based"].get("pb")),
                    "ps": round_ratio(res["price_based"].get("ps")),
                    "peg": round_ratio(res["price_based"].get("peg")),
                    "dividend_yield": round_ratio(res["dividends"].get("dividend_yield")),
                    "dividend_payout_ratio": round_ratio(res["dividends"].get("dividend_payout_ratio")),
                    "dividend_coverage_ratio": round_ratio(res["dividends"].get("dividend_coverage_ratio"))
                },
                "piotroski": {
                    "score": res.get("piotroski", {}).get("score"),
                    "fscore_display": res.get("piotroski", {}).get("fscore_display", "N/A"),
                    "signals": res.get("piotroski", {}).get("signals", {})
                },
                "dupont": res.get("dupont", {})
            },
            "data_quality": "complete" if not res.get("error") else "error",
            "missing": res.get("notes", []),
            "audit": {
                "period_used": "Annual",
                "ttm_quarters": 4,
                "statement_alignment": "aligned",
                "generated_at": "2024-01-01T00:00:00Z",
                "sources_used": ["yfinance"]
            }
        }
        
        # Sanitize the response for JSON serialization
        return sanitize_for_json(response)
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get("/api/search")
def search_tickers(query:str):
    try:
        # Comprehensive list of real Yahoo Finance tickers organized by category
        ticker_database = {
            # Technology Giants
            "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "MSFT": {"name": "Microsoft Corporation", "exchange": "NASDAQ", "sector": "Technology"},
            "GOOGL": {"name": "Alphabet Inc. Class A", "exchange": "NASDAQ", "sector": "Technology"},
            "GOOG": {"name": "Alphabet Inc. Class C", "exchange": "NASDAQ", "sector": "Technology"},
            "AMZN": {"name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
            "META": {"name": "Meta Platforms Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "NVDA": {"name": "NVIDIA Corporation", "exchange": "NASDAQ", "sector": "Technology"},
            "TSLA": {"name": "Tesla Inc.", "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
            "NFLX": {"name": "Netflix Inc.", "exchange": "NASDAQ", "sector": "Communication Services"},
            "ADBE": {"name": "Adobe Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "CRM": {"name": "Salesforce Inc.", "exchange": "NYSE", "sector": "Technology"},
            "INTC": {"name": "Intel Corporation", "exchange": "NASDAQ", "sector": "Technology"},
            "AMD": {"name": "Advanced Micro Devices Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "ORCL": {"name": "Oracle Corporation", "exchange": "NYSE", "sector": "Technology"},
            "IBM": {"name": "International Business Machines Corporation", "exchange": "NYSE", "sector": "Technology"},
            "CSCO": {"name": "Cisco Systems Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "QCOM": {"name": "QUALCOMM Incorporated", "exchange": "NASDAQ", "sector": "Technology"},
            "AVGO": {"name": "Broadcom Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            "TXN": {"name": "Texas Instruments Incorporated", "exchange": "NASDAQ", "sector": "Technology"},
            "MU": {"name": "Micron Technology Inc.", "exchange": "NASDAQ", "sector": "Technology"},
            
            # Financial Services
            "JPM": {"name": "JPMorgan Chase & Co.", "exchange": "NYSE", "sector": "Financial Services"},
            "BAC": {"name": "Bank of America Corporation", "exchange": "NYSE", "sector": "Financial Services"},
            "WFC": {"name": "Wells Fargo & Company", "exchange": "NYSE", "sector": "Financial Services"},
            "GS": {"name": "Goldman Sachs Group Inc.", "exchange": "NYSE", "sector": "Financial Services"},
            "MS": {"name": "Morgan Stanley", "exchange": "NYSE", "sector": "Financial Services"},
            "C": {"name": "Citigroup Inc.", "exchange": "NYSE", "sector": "Financial Services"},
            "AXP": {"name": "American Express Company", "exchange": "NYSE", "sector": "Financial Services"},
            "V": {"name": "Visa Inc.", "exchange": "NYSE", "sector": "Financial Services"},
            "MA": {"name": "Mastercard Incorporated", "exchange": "NYSE", "sector": "Financial Services"},
            "PYPL": {"name": "PayPal Holdings Inc.", "exchange": "NASDAQ", "sector": "Financial Services"},
            "SQ": {"name": "Block Inc.", "exchange": "NYSE", "sector": "Financial Services"},
            "COIN": {"name": "Coinbase Global Inc.", "exchange": "NASDAQ", "sector": "Financial Services"},
            
            # Healthcare & Pharmaceuticals
            "JNJ": {"name": "Johnson & Johnson", "exchange": "NYSE", "sector": "Healthcare"},
            "PFE": {"name": "Pfizer Inc.", "exchange": "NYSE", "sector": "Healthcare"},
            "UNH": {"name": "UnitedHealth Group Incorporated", "exchange": "NYSE", "sector": "Healthcare"},
            "ABBV": {"name": "AbbVie Inc.", "exchange": "NYSE", "sector": "Healthcare"},
            "MRK": {"name": "Merck & Co. Inc.", "exchange": "NYSE", "sector": "Healthcare"},
            "TMO": {"name": "Thermo Fisher Scientific Inc.", "exchange": "NYSE", "sector": "Healthcare"},
            "ABT": {"name": "Abbott Laboratories", "exchange": "NYSE", "sector": "Healthcare"},
            "DHR": {"name": "Danaher Corporation", "exchange": "NYSE", "sector": "Healthcare"},
            "BMY": {"name": "Bristol Myers Squibb Company", "exchange": "NYSE", "sector": "Healthcare"},
            "AMGN": {"name": "Amgen Inc.", "exchange": "NASDAQ", "sector": "Healthcare"},
            "GILD": {"name": "Gilead Sciences Inc.", "exchange": "NASDAQ", "sector": "Healthcare"},
            "CVS": {"name": "CVS Health Corporation", "exchange": "NYSE", "sector": "Healthcare"},
            
            # Consumer & Retail
            "WMT": {"name": "Walmart Inc.", "exchange": "NYSE", "sector": "Consumer Staples"},
            "PG": {"name": "Procter & Gamble Company", "exchange": "NYSE", "sector": "Consumer Staples"},
            "KO": {"name": "The Coca-Cola Company", "exchange": "NYSE", "sector": "Consumer Staples"},
            "PEP": {"name": "PepsiCo Inc.", "exchange": "NASDAQ", "sector": "Consumer Staples"},
            "MCD": {"name": "McDonald's Corporation", "exchange": "NYSE", "sector": "Consumer Discretionary"},
            "SBUX": {"name": "Starbucks Corporation", "exchange": "NASDAQ", "sector": "Consumer Discretionary"},
            "NKE": {"name": "NIKE Inc.", "exchange": "NYSE", "sector": "Consumer Discretionary"},
            "HD": {"name": "The Home Depot Inc.", "exchange": "NYSE", "sector": "Consumer Discretionary"},
            "LOW": {"name": "Lowe's Companies Inc.", "exchange": "NYSE", "sector": "Consumer Discretionary"},
            "TGT": {"name": "Target Corporation", "exchange": "NYSE", "sector": "Consumer Discretionary"},
            "COST": {"name": "Costco Wholesale Corporation", "exchange": "NASDAQ", "sector": "Consumer Staples"},
            
            # Energy & Utilities
            "XOM": {"name": "Exxon Mobil Corporation", "exchange": "NYSE", "sector": "Energy"},
            "CVX": {"name": "Chevron Corporation", "exchange": "NYSE", "sector": "Energy"},
            "COP": {"name": "ConocoPhillips", "exchange": "NYSE", "sector": "Energy"},
            "EOG": {"name": "EOG Resources Inc.", "exchange": "NYSE", "sector": "Energy"},
            "SLB": {"name": "Schlumberger Limited", "exchange": "NYSE", "sector": "Energy"},
            "NEE": {"name": "NextEra Energy Inc.", "exchange": "NYSE", "sector": "Utilities"},
            "DUK": {"name": "Duke Energy Corporation", "exchange": "NYSE", "sector": "Utilities"},
            "SO": {"name": "The Southern Company", "exchange": "NYSE", "sector": "Utilities"},
            
            # Industrial & Materials
            "BA": {"name": "The Boeing Company", "exchange": "NYSE", "sector": "Industrials"},
            "CAT": {"name": "Caterpillar Inc.", "exchange": "NYSE", "sector": "Industrials"},
            "GE": {"name": "General Electric Company", "exchange": "NYSE", "sector": "Industrials"},
            "HON": {"name": "Honeywell International Inc.", "exchange": "NASDAQ", "sector": "Industrials"},
            "MMM": {"name": "3M Company", "exchange": "NYSE", "sector": "Industrials"},
            "UPS": {"name": "United Parcel Service Inc.", "exchange": "NYSE", "sector": "Industrials"},
            "FDX": {"name": "FedEx Corporation", "exchange": "NYSE", "sector": "Industrials"},
            
            # Communication Services
            "DIS": {"name": "The Walt Disney Company", "exchange": "NYSE", "sector": "Communication Services"},
            "CMCSA": {"name": "Comcast Corporation", "exchange": "NASDAQ", "sector": "Communication Services"},
            "VZ": {"name": "Verizon Communications Inc.", "exchange": "NYSE", "sector": "Communication Services"},
            "T": {"name": "AT&T Inc.", "exchange": "NYSE", "sector": "Communication Services"},
            "TMUS": {"name": "T-Mobile US Inc.", "exchange": "NASDAQ", "sector": "Communication Services"},
            
            # Real Estate
            "AMT": {"name": "American Tower Corporation", "exchange": "NYSE", "sector": "Real Estate"},
            "PLD": {"name": "Prologis Inc.", "exchange": "NYSE", "sector": "Real Estate"},
            "CCI": {"name": "Crown Castle Inc.", "exchange": "NYSE", "sector": "Real Estate"},
            
            # Berkshire Hathaway
            "BRK-B": {"name": "Berkshire Hathaway Inc. Class B", "exchange": "NYSE", "sector": "Financial Services"},
            "BRK-A": {"name": "Berkshire Hathaway Inc. Class A", "exchange": "NYSE", "sector": "Financial Services"},
            
            # ETFs
            "SPY": {"name": "SPDR S&P 500 ETF Trust", "exchange": "NYSE", "sector": "ETF"},
            "QQQ": {"name": "Invesco QQQ Trust", "exchange": "NASDAQ", "sector": "ETF"},
            "VTI": {"name": "Vanguard Total Stock Market Index Fund", "exchange": "NYSE", "sector": "ETF"},
            "VOO": {"name": "Vanguard S&P 500 ETF", "exchange": "NYSE", "sector": "ETF"},
            "IWM": {"name": "iShares Russell 2000 ETF", "exchange": "NYSE", "sector": "ETF"},
        }
        
        query_upper = query.upper()
        results = []
        
        # Search by ticker symbol first (exact match gets priority)
        for symbol, info in ticker_database.items():
            if query_upper in symbol.upper():
                results.append({
                    "symbol": symbol,
                    "company_name": info["name"],
                    "exchange": info["exchange"],
                    "display": f"{symbol} - {info['name']} ({info['exchange']})"
                })
        
        # Then search by company name
        for symbol, info in ticker_database.items():
            if query_upper in info["name"].upper() and symbol not in [r["symbol"] for r in results]:
                results.append({
                    "symbol": symbol,
                    "company_name": info["name"],
                    "exchange": info["exchange"],
                    "display": f"{symbol} - {info['name']} ({info['exchange']})"
                })
        
        return results[:15]  # Limit to 15 results
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

@app.get("/api/historical/download")
def download_historical_data(ticker:str, start:str, end:str, interval:str="1d", format:str="xlsx", include_accounting:bool=False):
    try:
        # For now, return a simple response indicating the feature is not implemented
        return {
            "ok": False,
            "path": "",
            "filename": "",
            "rows": 0,
            "start_available": start,
            "end_available": end,
            "download_url": "",
            "error": "Historical download feature not implemented in clean backend"
        }
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))

# Run commands
# uvicorn app:app --reload --host 127.0.0.1 --port 8000
# curl -s http://127.0.0.1:8000/health
# curl -s http://127.0.0.1:8000/metrics/AAPL | jq .
# fetch("http://127.0.0.1:8000/metrics/MSFT").then(r=>r.json())