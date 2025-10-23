"use client";
import { useState, useEffect } from "react";

interface CompanySummary {
  ticker: string;
  ticker_normalized: string;
  exists: boolean;
  instrument_type: string;
  company_name: string;
  sector: string;
  industry: string;
  real_time: {
    price: number;
    currency: string;
    timestamp: string;
  };
  beta: number | null;
  alpha: number | null;
  data_quality: string;
  missing: string[];
  audit: {
    generated_at: string;
    sources_used: string[];
  };
}

interface AutocompleteResult {
  symbol: string;
  company_name: string;
  exchange: string;
  display: string;
}

interface MetricsData {
  ticker: string;
  metrics: {
    beneish_m_score: number | null;
    beneish_reason: string | null;
    beneish_components: {
      DSRI: number | null;
      GMI: number | null;
      AQI: number | null;
      SGI: number | null;
      DEPI: number | null;
      SGAI: number | null;
      LVGI: number | null;
      TATA: number | null;
    };
    altman: {
      z: number | null;
      z_prime: number | null;
    };
    ratios: {
      current: number | null;
      quick: number | null;
      debt_to_equity: number | null;
      roe: number | null;
      roe_adjusted: number | null;
      roa: number | null;
      pe: number | null;
      pb: number | null;
      ps: number | null;
      peg: number | null;
      dividend_yield: number | null;
      dividend_payout_ratio: number | null;
      dividend_coverage_ratio: number | null;
    };
    piotroski: {
      score: number | null;
      signals: {
        F1: number;
        F2: number;
        F3: number;
        F4: number;
        F5: number;
        F6: number;
        F7: number;
        F8: number;
        F9: number;
      };
    };
    dupont: {
      roe_3step: {
        roe: number | null;
        npm: number | null;
        asset_turnover: number | null;
        equity_multiplier: number | null;
      };
      roe_5step: {
        roe: number | null;
        tax_burden: number | null;
        interest_burden: number | null;
        operating_margin: number | null;
        asset_turnover: number | null;
        equity_multiplier: number | null;
      };
    };
  };
  data_quality: string;
  missing: string[];
  audit: {
    period_used: string;
    ttm_quarters: number;
    statement_alignment: string;
    generated_at: string;
    sources_used: string[];
  };
}

interface HistoricalDownload {
  ok: boolean;
  path: string;
  filename: string;
  rows: number;
  start_available: string;
  end_available: string;
  download_url: string;
}

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [companySummary, setCompanySummary] = useState<CompanySummary | null>(null);
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [downloadParams, setDownloadParams] = useState({
    start: "",
    end: "",
    interval: "1d",
    include_accounting: false
  });
  const [precision, setPrecision] = useState(4);
  
  // Autocomplete state
  const [autocompleteResults, setAutocompleteResults] = useState<AutocompleteResult[]>([]);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [searchTimeout, setSearchTimeout] = useState<NodeJS.Timeout | null>(null);

  const popularTickers = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM"];

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTimeout]);

  // Refetch metrics when precision changes (if we have data)
  useEffect(() => {
    if (metricsData && ticker.trim()) {
      fetchMetrics();
    }
  }, [precision]);

  const fetchMetrics = async () => {
    if (!ticker.trim()) {
      setError("Please enter a ticker symbol");
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // Fetch company summary first
      const summaryResponse = await fetch(`http://127.0.0.1:8000/api/company/summary?ticker=${ticker.trim()}`);
      if (!summaryResponse.ok) {
        throw new Error(`Failed to fetch company summary: ${summaryResponse.statusText}`);
      }
      const summaryData = await summaryResponse.json();
      
      if (!summaryData.exists) {
        throw new Error(`Ticker ${ticker} not found`);
      }

      setCompanySummary(summaryData);

      // Fetch metrics with precision control
      const metricsResponse = await fetch(`http://127.0.0.1:8000/api/metrics/simple?ticker=${ticker.trim()}&precision=${precision}`);
      if (!metricsResponse.ok) {
        throw new Error(`Failed to fetch metrics: ${metricsResponse.statusText}`);
      }
      const metrics = await metricsResponse.json();
      
      setMetricsData(metrics);
      setSuccessMessage(`Successfully loaded metrics for ${summaryData.company_name} (${summaryData.ticker})`);
      
    } catch (err) {
      console.error("Error fetching metrics:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch metrics");
    } finally {
      setLoading(false);
    }
  };

  const downloadHistorical = async () => {
    if (!ticker.trim()) {
      setError("Please enter a ticker symbol");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        ticker: ticker.trim(),
        start: downloadParams.start || new Date(Date.now() - 10 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end: downloadParams.end || new Date().toISOString().split('T')[0],
        interval: downloadParams.interval,
        format: "xlsx"
      });

      if (downloadParams.include_accounting) {
        params.append("include_accounting", "1");
      }

      const response = await fetch(`http://127.0.0.1:8000/api/historical/download?${params}`);
      if (!response.ok) {
        throw new Error(`Failed to download historical data: ${response.statusText}`);
      }
      
      const data: HistoricalDownload = await response.json();
      
      if (data.ok) {
        // Open download URL
        window.open(`http://127.0.0.1:8000${data.download_url}`, '_blank');
        setSuccessMessage(`Historical data downloaded: ${data.filename} (${data.rows} rows)`);
        setShowDownloadModal(false);
      } else {
        throw new Error("Download failed");
      }
      
    } catch (err) {
      console.error("Error downloading historical data:", err);
      setError(err instanceof Error ? err.message : "Failed to download historical data");
    } finally {
      setLoading(false);
    }
  };

  // Autocomplete functions
  const searchTickers = async (query: string) => {
    if (query.length < 2) {
      setAutocompleteResults([]);
      setShowAutocomplete(false);
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/search?query=${encodeURIComponent(query)}`);
      if (response.ok) {
        const results: AutocompleteResult[] = await response.json();
        setAutocompleteResults(results);
        setShowAutocomplete(results.length > 0);
        setSelectedIndex(-1);
      }
    } catch (error) {
      console.error("Error searching tickers:", error);
      setAutocompleteResults([]);
      setShowAutocomplete(false);
    }
  };

  const handleTickerChange = (value: string) => {
    setTicker(value);
    
    // Clear previous timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
    
    // Debounce search
    const timeout = setTimeout(() => {
      searchTickers(value);
    }, 250);
    setSearchTimeout(timeout);
  };

  const handleTickerSelect = (result: AutocompleteResult) => {
    setTicker(result.symbol);
    setShowAutocomplete(false);
    setAutocompleteResults([]);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showAutocomplete || autocompleteResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < autocompleteResults.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < autocompleteResults.length) {
          handleTickerSelect(autocompleteResults[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowAutocomplete(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const formatNumber = (value: number | null, decimals: number = 4): string => {
    if (value === null) return "—";
    return value.toFixed(decimals);
  };

  const formatPercentage = (value: number | null, decimals: number = 2): string => {
    if (value === null) return "—";
    return `${(value * 100).toFixed(decimals)}%`;
  };

  const formatRatio = (value: number | null, decimals: number = precision): string => {
    if (value === null) return "—";
    return value.toFixed(decimals);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <header className="bg-white/80 backdrop-blur-md shadow-lg border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">📊</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  Financial Metrics Analyzer
                </h1>
                <p className="text-sm text-gray-600 mt-1">Professional financial analysis & fraud detection</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8 mb-8">
          <div className="flex flex-col space-y-6">
            <div className="relative">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                🔍 Company Ticker Search
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => handleTickerChange(e.target.value.toUpperCase())}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter ticker symbol (e.g., AAPL, BTC-USD, SPY)"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 text-lg font-medium"
                  onKeyPress={(e) => e.key === 'Enter' && fetchMetrics()}
                />
                
                {/* Autocomplete Dropdown */}
                {showAutocomplete && autocompleteResults.length > 0 && (
                  <div className="absolute z-20 w-full mt-2 bg-white/95 backdrop-blur-md border border-gray-200 rounded-xl shadow-2xl max-h-80 overflow-y-auto">
                    {autocompleteResults.map((result, index) => (
                      <div
                        key={`${result.symbol}-${result.exchange}-${index}`}
                        onClick={() => handleTickerSelect(result)}
                        className={`px-4 py-3 cursor-pointer hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-b-0 ${
                          index === selectedIndex ? 'bg-blue-100 border-l-4 border-blue-500' : ''
                        }`}
                      >
                        <div className="font-semibold text-gray-900">{result.symbol}</div>
                        <div className="text-sm text-gray-600">{result.company_name}</div>
                        <div className="text-xs text-gray-500">{result.exchange}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
            
            <div className="flex flex-wrap gap-3 mb-6">
              {popularTickers.map((t) => (
                <button
                  key={t}
                  onClick={() => setTicker(t)}
                  className="px-4 py-2 text-sm bg-gradient-to-r from-gray-100 to-gray-200 hover:from-blue-100 hover:to-indigo-100 rounded-lg transition-all duration-200 font-medium text-gray-700 hover:text-blue-700 shadow-sm hover:shadow-md"
                >
                  {t}
                </button>
              ))}
            </div>

            <div className="flex items-center space-x-4 mb-6">
              <label className="text-sm font-semibold text-gray-700">Precision:</label>
              <select
                value={precision}
                onChange={(e) => setPrecision(parseInt(e.target.value))}
                className="px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200"
              >
                <option value={2}>2 decimals (0.87)</option>
                <option value={4}>4 decimals (0.8673)</option>
                <option value={6}>6 decimals (0.867313)</option>
                <option value={8}>8 decimals (0.86731258)</option>
              </select>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={fetchMetrics}
                disabled={loading}
                className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none font-semibold text-lg"
              >
                {loading ? "⏳ Loading..." : "📊 Fetch Metrics"}
              </button>
              
              <button
                onClick={() => setShowDownloadModal(true)}
                disabled={loading}
                className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none font-semibold text-lg"
              >
                📥 Download History
              </button>
            </div>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="mb-8 p-6 bg-gradient-to-r from-red-50 to-pink-50 border-l-4 border-red-500 rounded-xl shadow-lg">
            <div className="flex items-center">
              <span className="text-red-500 text-xl mr-3">⚠️</span>
              <p className="text-red-800 font-medium">{error}</p>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="mb-8 p-6 bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-500 rounded-xl shadow-lg">
            <div className="flex items-center">
              <span className="text-green-500 text-xl mr-3">✅</span>
              <p className="text-green-800 font-medium">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Company Information */}
        {companySummary && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="text-3xl mr-3">🏢</span>
              Company Information
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Company</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{companySummary.company_name}</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Ticker</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{companySummary.ticker}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Sector</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{companySummary.sector}</p>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Industry</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{companySummary.industry}</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-50 to-amber-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Price</span>
                <p className="text-lg font-bold text-gray-900 mt-1">
                  ${formatNumber(companySummary.real_time.price, 2)} {companySummary.real_time.currency}
                </p>
              </div>
              <div className="bg-gradient-to-br from-cyan-50 to-blue-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Beta</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{formatNumber(companySummary.beta, 3)}</p>
              </div>
              <div className="bg-gradient-to-br from-teal-50 to-green-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Alpha</span>
                <p className="text-lg font-bold text-gray-900 mt-1">{formatNumber(companySummary.alpha, 4)}</p>
              </div>
              <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-4 rounded-xl">
                <span className="text-sm font-semibold text-gray-600">Data Quality</span>
                <p className="text-lg font-bold text-gray-900 mt-1 capitalize">{companySummary.data_quality}</p>
              </div>
            </div>
          </div>
        )}

        {/* Metrics */}
        {metricsData && (
          <div className="bg-white/70 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50 p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-8 flex items-center">
              <span className="text-3xl mr-3">📈</span>
              Financial Metrics
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Beneish M-Score */}
              <div className="bg-gradient-to-br from-red-50 to-pink-50 border border-red-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">🔍</span>
                  Beneish M-Score
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">M-Score:</span>
                    <span className="font-bold text-lg text-gray-900">
                      {metricsData.metrics.beneish_m_score !== null ? formatNumber(metricsData.metrics.beneish_m_score, 2) : "N/A"}
                    </span>
                  </div>
                  {metricsData.metrics.beneish_m_score === null && metricsData.metrics.beneish_reason && (
                    <div className="text-xs text-gray-600 bg-yellow-50 p-2 rounded">
                      Reason: {metricsData.metrics.beneish_reason}
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="bg-white/50 rounded-lg p-2 text-center">
                      <span className="font-semibold text-gray-700">DSRI:</span>
                      <span className="ml-1">{formatNumber(metricsData.metrics.beneish_components.DSRI, 2)}</span>
                    </div>
                    <div className="bg-white/50 rounded-lg p-2 text-center">
                      <span className="font-semibold text-gray-700">GMI:</span>
                      <span className="ml-1">{formatNumber(metricsData.metrics.beneish_components.GMI, 2)}</span>
                    </div>
                    <div className="bg-white/50 rounded-lg p-2 text-center">
                      <span className="font-semibold text-gray-700">AQI:</span>
                      <span className="ml-1">{formatNumber(metricsData.metrics.beneish_components.AQI, 2)}</span>
                    </div>
                    <div className="bg-white/50 rounded-lg p-2 text-center">
                      <span className="font-semibold text-gray-700">SGI:</span>
                      <span className="ml-1">{formatNumber(metricsData.metrics.beneish_components.SGI, 2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Altman Z-Score */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">⚖️</span>
                  Altman Z-Score
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Z-Score:</span>
                    <span className="font-bold text-lg text-gray-900">{formatNumber(metricsData.metrics.altman.z)}</span>
                  </div>
                </div>
              </div>

              {/* Financial Ratios */}
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6 shadow-lg lg:col-span-1">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">📊</span>
                  Financial Ratios
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Current Ratio:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.current)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Quick Ratio:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.quick)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Debt-to-Equity:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.debt_to_equity)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">ROE (Return on Equity):</span>
                    <span className="font-bold text-lg text-gray-900" title="High ROE may indicate aggressive share buybacks rather than operational efficiency">{formatPercentage(metricsData.metrics.ratios.roe)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">ROE Adjusted:</span>
                    <span className="font-bold text-lg text-gray-900" title="ROE calculated using Total Assets - Total Liabilities for more stable comparison">{formatPercentage(metricsData.metrics.ratios.roe_adjusted)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">ROA (Return on Assets):</span>
                    <span className="font-bold text-lg text-gray-900">{formatPercentage(metricsData.metrics.ratios.roa)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Comprehensive Metrics */}
            <div className="mt-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                <span className="text-3xl mr-3">🎯</span>
                Comprehensive Analysis
              </h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Piotroski F-Score */}
                <div className="bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-200 rounded-2xl p-6 shadow-lg">
                  <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                    <span className="text-2xl mr-2">⭐</span>
                    Piotroski F-Score
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                      <span className="text-sm font-semibold text-gray-700">F-Score:</span>
                      <span className="font-bold text-lg text-gray-900">{metricsData.metrics.piotroski.fscore_display}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs">
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F1:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F1 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F2:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F2 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F3:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F3 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F4:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F4 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F5:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F5 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F6:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F6 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F7:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F7 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F8:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F8 ? '✓' : '✗'}</span>
                      </div>
                      <div className="bg-white/50 rounded-lg p-2 text-center">
                        <span className="font-semibold text-gray-700">F9:</span>
                        <span className="ml-1">{metricsData.metrics.piotroski.signals.F9 ? '✓' : '✗'}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* DuPont Analysis */}
                <div className="bg-gradient-to-br from-orange-50 to-yellow-50 border border-orange-200 rounded-2xl p-6 shadow-lg">
                  <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                    <span className="text-2xl mr-2">🔬</span>
                    DuPont Analysis
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                      <span className="text-sm font-semibold text-gray-700">3-Step ROE:</span>
                      <span className="font-bold text-lg text-gray-900">{formatPercentage(metricsData.metrics.dupont.roe_3step.roe)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                      <span className="text-sm font-semibold text-gray-700">Net Profit Margin:</span>
                      <span className="font-bold text-lg text-gray-900">{formatPercentage(metricsData.metrics.dupont.roe_3step.npm)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                      <span className="text-sm font-semibold text-gray-700">Asset Turnover:</span>
                      <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.dupont.roe_3step.asset_turnover)}</span>
                    </div>
                    <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                      <span className="text-sm font-semibold text-gray-700">Equity Multiplier:</span>
                      <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.dupont.roe_3step.equity_multiplier)}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Price-Based Ratios */}
              <div className="mt-8 bg-gradient-to-br from-cyan-50 to-blue-50 border border-cyan-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">💰</span>
                  Price-Based Ratios
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">P/E:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.pe)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">P/B:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.pb)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">P/S:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.ps)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">PEG:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.peg)}</span>
                  </div>
                </div>
              </div>

              {/* Dividend Metrics */}
              <div className="mt-8 bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="text-2xl mr-2">💎</span>
                  Dividend Metrics
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Dividend Yield:</span>
                    <span className="font-bold text-lg text-gray-900">{formatPercentage(metricsData.metrics.ratios.dividend_yield)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Payout Ratio:</span>
                    <span className="font-bold text-lg text-gray-900">{formatPercentage(metricsData.metrics.ratios.dividend_payout_ratio)}</span>
                  </div>
                  <div className="flex justify-between items-center bg-white/50 rounded-lg p-3">
                    <span className="text-sm font-semibold text-gray-700">Coverage Ratio:</span>
                    <span className="font-bold text-lg text-gray-900">{formatRatio(metricsData.metrics.ratios.dividend_coverage_ratio)}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Data Quality Info */}
            <div className="mt-8 p-6 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200">
              <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="text-xl mr-2">ℹ️</span>
                Data Quality Information
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="bg-white/50 rounded-lg p-3">
                  <span className="font-semibold text-gray-700">Period Used:</span>
                  <p className="text-gray-900 font-medium">{metricsData.audit.period_used}</p>
                </div>
                <div className="bg-white/50 rounded-lg p-3">
                  <span className="font-semibold text-gray-700">TTM Quarters:</span>
                  <p className="text-gray-900 font-medium">{metricsData.audit.ttm_quarters}</p>
                </div>
                <div className="bg-white/50 rounded-lg p-3">
                  <span className="font-semibold text-gray-700">Statement Alignment:</span>
                  <p className="text-gray-900 font-medium">{metricsData.audit.statement_alignment}</p>
                </div>
              </div>
              {metricsData.missing.length > 0 && (
                <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="font-semibold text-yellow-800">Missing Data:</span>
                  <p className="text-yellow-700">{metricsData.missing.join(", ")}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Download Modal */}
        {showDownloadModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl w-full max-w-lg border border-gray-200/50">
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 flex items-center">
                    <span className="text-3xl mr-3">📥</span>
                    Download Historical Data
                  </h3>
                  <button
                    onClick={() => setShowDownloadModal(false)}
                    className="text-gray-400 hover:text-gray-600 transition-colors text-2xl"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Ticker Symbol</label>
                    <input
                      type="text"
                      value={ticker}
                      disabled
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl bg-gray-50 text-gray-600"
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Start Date</label>
                      <input
                        type="date"
                        value={downloadParams.start}
                        onChange={(e) => setDownloadParams(prev => ({ ...prev, start: e.target.value }))}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">End Date</label>
                      <input
                        type="date"
                        value={downloadParams.end}
                        onChange={(e) => setDownloadParams(prev => ({ ...prev, end: e.target.value }))}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">Interval</label>
                    <select
                      value={downloadParams.interval}
                      onChange={(e) => setDownloadParams(prev => ({ ...prev, interval: e.target.value }))}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200"
                    >
                      <option value="1d">Daily</option>
                      <option value="1wk">Weekly</option>
                      <option value="1mo">Monthly</option>
                    </select>
                  </div>
                  
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="include_accounting"
                      checked={downloadParams.include_accounting}
                      onChange={(e) => setDownloadParams(prev => ({ ...prev, include_accounting: e.target.checked }))}
                      className="w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <label htmlFor="include_accounting" className="ml-3 text-sm font-medium text-gray-700">
                      Include accounting statements (scraped if needed)
                    </label>
                  </div>
                </div>
                
                <div className="flex space-x-4 mt-8">
                  <button
                    onClick={downloadHistorical}
                    disabled={loading}
                    className="flex-1 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none font-semibold"
                  >
                    {loading ? "⏳ Downloading..." : "📥 Download Excel"}
                  </button>
                  <button
                    onClick={() => setShowDownloadModal(false)}
                    className="px-6 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-all duration-200 font-semibold"
                  >
                    Cancel
      </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}