"use client";
import { useState, useEffect } from "react";

interface ComplianceSource {
  id: string;
  title: string;
  section_tags: string[];
  description: string;
  domain: string;
  url: string;
}

interface FraudSignal {
  name: string;
  value: number | null;
  severity: string;
  rationale: string;
}

interface FraudScore {
  value: number;
  scale: string;
  band: string;
}

interface FraudScoreResponse {
  ticker: string;
  data_quality: string;
  signals: FraudSignal[];
  score: FraudScore;
  recommendations: Array<{ test: string; why: string }>;
  sources_meta: string[];
}

interface Control {
  id: string;
  process: string;
  assertions: string[];
  type: string;
  frequency: string;
  evidence: string;
  sox_sections: string[];
}

interface ControlsResponse {
  processes: string[];
  assertions: string[];
  controls: Control[];
}

export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState<'sources' | 'fraud'>('sources');
  const [sources, setSources] = useState<ComplianceSource[]>([]);
  const [controls, setControls] = useState<ControlsResponse | null>(null);
  const [fraudData, setFraudData] = useState<FraudScoreResponse | null>(null);
  const [ticker, setTicker] = useState('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState('');

  const tags = ['SOX', 'ICFR', 'Fraud', 'FRM', 'Auditing'];

  useEffect(() => {
    loadSources();
    loadControls();
  }, []);

  const loadSources = async () => {
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append('q', searchQuery);
      if (selectedTag) params.append('tag', selectedTag);
      
      const response = await fetch(`http://127.0.0.1:8000/api/compliance/sources?${params}`);
      const data = await response.json();
      setSources(data.sources || []);
    } catch (error) {
      console.error('Error loading sources:', error);
    }
  };

  const loadControls = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/compliance/controls');
      const data = await response.json();
      setControls(data);
    } catch (error) {
      console.error('Error loading controls:', error);
    }
  };

  const loadFraudScore = async () => {
    if (!ticker.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/fraud/score?ticker=${ticker}`);
      const data = await response.json();
      setFraudData(data);
    } catch (error) {
      console.error('Error loading fraud score:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, [searchQuery, selectedTag]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getBandColor = (band: string) => {
    switch (band) {
      case 'high': return 'bg-red-500';
      case 'elevated': return 'bg-orange-500';
      case 'moderate': return 'bg-yellow-500';
      case 'low': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('sources')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'sources'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📚 Official Sources
              </button>
              <button
                onClick={() => setActiveTab('fraud')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'fraud'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔍 Fraud Risk Analysis
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'sources' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Official Compliance Sources</h2>
                  
                  <div className="flex flex-wrap gap-4 mb-4">
                    <div className="flex-1 min-w-64">
                      <input
                        type="text"
                        placeholder="Search sources..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div className="flex gap-2">
                      {tags.map(tag => (
                        <button
                          key={tag}
                          onClick={() => setSelectedTag(selectedTag === tag ? '' : tag)}
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            selectedTag === tag
                              ? 'bg-blue-100 text-blue-800'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {tag}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="grid gap-4">
                  {sources.map(source => (
                    <div key={source.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">{source.title}</h3>
                          <p className="text-gray-600 mb-3">{source.description}</p>
                          <div className="flex flex-wrap gap-2 mb-3">
                            {source.section_tags.map(tag => (
                              <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                                {tag}
                              </span>
                            ))}
                          </div>
                          <div className="text-sm text-gray-500">
                            Source: {source.domain}
                          </div>
                        </div>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                          Open Source
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'fraud' && (
              <div>
                <div className="mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Fraud Risk Analysis</h2>
                  
                  <div className="flex gap-4 mb-6">
                    <input
                      type="text"
                      placeholder="Enter ticker symbol (e.g., AAPL)"
                      value={ticker}
                      onChange={(e) => setTicker(e.target.value.toUpperCase())}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      onClick={loadFraudScore}
                      disabled={loading || !ticker.trim()}
                      className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loading ? 'Analyzing...' : 'Analyze Fraud Risk'}
                    </button>
                  </div>
                </div>

                {fraudData && (
                  <div className="space-y-6">
                    {/* Fraud Score Summary */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-semibold text-gray-900">Fraud Risk Score</h3>
                        <div className="flex items-center gap-3">
                          <div className={`w-4 h-4 rounded-full ${getBandColor(fraudData.score.band)}`}></div>
                          <span className="text-lg font-bold capitalize">{fraudData.score.band}</span>
                        </div>
                      </div>
                      <div className="text-3xl font-bold text-gray-900 mb-2">
                        {fraudData.score.value}/100
                      </div>
                      <div className="text-sm text-gray-600">
                        Data Quality: <span className="font-medium capitalize">{fraudData.data_quality}</span>
                      </div>
                    </div>

                    {/* Fraud Signals */}
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">Fraud Risk Signals</h3>
                      <div className="grid gap-4">
                        {fraudData.signals.map((signal, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-4">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-medium text-gray-900 capitalize">
                                {signal.name.replace(/_/g, ' ')}
                              </h4>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(signal.severity)}`}>
                                {signal.severity}
                              </span>
                            </div>
                            {signal.value !== null && (
                              <div className="text-lg font-semibold text-gray-700 mb-2">
                                {signal.value}
                              </div>
                            )}
                            <p className="text-sm text-gray-600">{signal.rationale}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recommendations */}
                    {fraudData.recommendations.length > 0 && (
                      <div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">Audit Recommendations</h3>
                        <div className="grid gap-3">
                          {fraudData.recommendations.map((rec, index) => (
                            <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                              <div className="font-medium text-blue-900 mb-1">{rec.test}</div>
                              <div className="text-sm text-blue-700">{rec.why}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Sources */}
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-4">Reference Sources</h3>
                      <div className="flex flex-wrap gap-2">
                        {fraudData.sources_meta.map((source, index) => (
                          <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full">
                            {source}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
