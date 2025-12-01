# Financial Metrics Analyzer

A professional financial analysis and fraud detection tool that provides comprehensive metrics for investment decision-making. Built with Python FastAPI backend and Next.js frontend.

## Features

### 🔍 **Smart Ticker Search**
- **80+ Real Yahoo Finance Tickers** - Comprehensive database of major stocks, ETFs, and indices
- **Dynamic Autocomplete** - Type 2-3 letters to get instant suggestions
- **Sector Organization** - Technology, Financial Services, Healthcare, Energy, Consumer, and more

### **Advanced Financial Metrics**
- **Beneish M-Score** - Fraud detection model with component analysis
- **Altman Z-Score** - Bankruptcy prediction model
- **Piotroski F-Score** - Financial strength assessment (0-9 scale)
- **DuPont Analysis** - ROE breakdown into components
- **Core Financial Ratios** - Current, Quick, Debt-to-Equity, ROE, ROA
- **Price-Based Ratios** - P/E, P/B, P/S, PEG ratios
- **Dividend Metrics** - Yield, payout ratio, coverage ratio

### *Real-Time Data**
- **Live Market Data** - Current prices, beta, alpha calculations
- **Company Information** - Full name, sector, industry, exchange
- **Data Quality Indicators** - Complete/limited data warnings
- **Alpha Calculation** - CAPM-based alpha vs S&P 500 benchmark

### **Robust Error Handling**
- **ETF Support** - Graceful handling of ETFs with limited financial data
- **Missing Data** - Clear indicators when data is unavailable
- **JSON Safety** - Handles infinity/NaN values properly
- **Rate Limiting** - Respectful API usage

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/financial-metrics-analyzer.git
cd financial-metrics-analyzer
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the backend server
python app.py
```
The backend will be available at `http://127.0.0.1:8000`

3. **Frontend Setup**
```bash
# Navigate to frontend directory
cd audit-ui

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend will be available at `http://localhost:3000`

## API Endpoints

### Company Information
- `GET /api/company/summary?ticker=AAPL` - Get company details and market data
- `GET /api/search?query=aa` - Search for tickers with autocomplete

### Financial Metrics
- `GET /api/metrics/simple?ticker=AAPL&precision=4` - Get comprehensive financial metrics

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)

## Usage Examples

### Search for Companies
Type in the search box to get suggestions:
- `aa` → Apple Inc. (AAPL)
- `mi` → Microsoft (MSFT), AMD, Micron (MU)
- `goo` → Alphabet Class A (GOOGL), Alphabet Class C (GOOG)

### Analyze Financial Health
1. Enter a ticker symbol (e.g., AAPL, MSFT, NVDA)
2. Click "Fetch Metrics" to get comprehensive analysis
3. Review the metrics dashboard:
   - **Beneish M-Score**: Lower values indicate potential fraud risk
   - **Altman Z-Score**: Higher values indicate financial stability
   - **Piotroski F-Score**: Higher scores (7-9) indicate strong fundamentals
   - **Financial Ratios**: Compare against industry benchmarks

### Supported Tickers

#### Technology Giants
AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, NFLX, ADBE, CRM, INTC, AMD, ORCL, IBM, CSCO, QCOM, AVGO, TXN, MU

#### Financial Services
JPM, BAC, WFC, GS, MS, C, AXP, V, MA, PYPL, SQ, COIN

#### Healthcare & Pharmaceuticals
JNJ, PFE, UNH, ABBV, MRK, TMO, ABT, DHR, BMY, AMGN, GILD, CVS

#### Consumer & Retail
WMT, PG, KO, PEP, MCD, SBUX, NKE, HD, LOW, TGT, COST

#### Energy & Utilities
XOM, CVX, COP, EOG, SLB, NEE, DUK, SO

#### ETFs
SPY, QQQ, VTI, VOO, IWM

## Technical Details

### Backend Architecture
- **FastAPI** - Modern Python web framework
- **yfinance** - Yahoo Finance data integration
- **pandas/numpy** - Data processing and calculations
- **finance_clean** - Custom financial calculation engine

### Frontend Architecture
- **Next.js 15** - React framework with Turbopack
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Modern styling
- **Real-time Updates** - Live data fetching

### Financial Models

#### Beneish M-Score Components
- **DSRI** - Days Sales in Receivables Index
- **GMI** - Gross Margin Index
- **AQI** - Asset Quality Index
- **SGI** - Sales Growth Index
- **DEPI** - Depreciation Index
- **SGAI** - Sales General Administrative Index
- **LVGI** - Leverage Index
- **TATA** - Total Accruals to Total Assets

#### Altman Z-Score Formula
```
Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E
```
Where:
- A = Working Capital / Total Assets
- B = Retained Earnings / Total Assets
- C = EBIT / Total Assets
- D = Market Value Equity / Total Liabilities
- E = Sales / Total Assets

## 🛠️ Development

### Project Structure
```
financial-metrics-analyzer/
├── app.py                 # FastAPI backend server
├── requirements.txt       # Python dependencies
├── finance_clean/         # Financial calculation engine
│   ├── __init__.py
│   ├── fetch.py          # Data fetching from yfinance
│   ├── normalize.py      # Data normalization and utilities
│   ├── validate.py       # Data validation functions
│   └── compute.py        # Core financial calculations
├── audit-ui/             # Next.js frontend
│   ├── app/
│   │   ├── page.tsx      # Main application page
│   │   └── layout.tsx    # Application layout
│   ├── package.json      # Node.js dependencies
│   └── next.config.ts    # Next.js configuration
└── README.md             # This file
```


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License & Attribution

### 🔖 Technical Badges
![Built with Python 3.12](https://img.shields.io/badge/Built%20with-Python%203.12-blue)
![Powered by Pandas & NumPy](https://img.shields.io/badge/Powered%20by-Pandas%20%26%20NumPy-green)
![Data Source Yahoo Finance](https://img.shields.io/badge/Data%20Source-Yahoo%20Finance-orange)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

---

### License & Attribution

**© 2025 Tanmay Rajendra Sarfare. All rights reserved.**

This project and its contents (code, documentation, and visuals) are the intellectual property of the author. Unauthorized reproduction, redistribution, or commercial use of any part of this repository is strictly prohibited without prior written permission.

**For academic or professional reference, please cite this repository as:**
```
Sarfare, Tanmay R. (2025). Financial Metrics Analyzer — Professional Financial Analysis and Fraud Detection Tool. GitHub.
https://github.com/TanmaySarfare/Financial-Metrics-Analyzer
```

### Disclaimer

This tool is for educational and research purposes only. It should not be used as the sole basis for investment decisions. Always consult with qualified financial advisors before making investment choices.

**The author assumes no responsibility for any financial losses or decisions made based on this tool's output.**

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/TanmaySarfare/Financial-Metrics-Analyzer/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## Acknowledgments

- **Yahoo Finance** - For providing free financial data
- **FastAPI** - For the excellent Python web framework
- **Next.js** - For the powerful React framework
- **Financial Research Community** - For the academic models and formulas
- **Academic Researchers** - Beneish, Altman, Piotroski for their groundbreaking work

