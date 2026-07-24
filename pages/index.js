import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [updates, setUpdates] = useState([]);
  const [filteredUpdates, setFilteredUpdates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastScraped, setLastScraped] = useState(null);
  
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedJurisdiction, setSelectedJurisdiction] = useState('');
  const [selectedImpact, setSelectedImpact] = useState('');
  const [sortBy, setSortBy] = useState('date-desc');
  
  // Computed filters
  const [categories, setCategories] = useState([]);
  const [jurisdictions, setJurisdictions] = useState([]);
  const [impacts, setImpacts] = useState([]);

  // Fetch data from GitHub repository
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Replace with your GitHub repo details
        const githubUser = "ArunavDixit";
        const githubRepo = 'regulatory-dashboard';
        const branch = 'main';
        
        const dataUrl = "https://raw.githubusercontent.com/ArunavDixit/PCS---Knowledge-Dashboard/main/data.json";
        
        const response = await fetch(dataUrl, {
          cache: 'no-store'
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch data: ${response.status}`);
        }
        
        const data = await response.json();
        const items = data.updates || [];
        
        setUpdates(items);
        setLastScraped(data.last_scraped);
        
        // Extract unique values for filters
        const uniqueCategories = [...new Set(
          items.map(item => item.classification?.category).filter(Boolean)
        )].sort();
        
        const uniqueJurisdictions = [...new Set(
          items.map(item => item.classification?.jurisdiction).filter(Boolean)
        )].sort();
        
        const uniqueImpacts = [...new Set(
          items.map(item => item.classification?.impact_level).filter(Boolean)
        )];
        
        setCategories(uniqueCategories);
        setJurisdictions(uniqueJurisdictions);
        setImpacts(uniqueImpacts);
        
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // Refresh every 30 minutes
    const interval = setInterval(fetchData, 30 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...updates];
    
    // Search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.title.toLowerCase().includes(term) ||
        item.source.toLowerCase().includes(term) ||
        item.classification?.one_line_summary?.toLowerCase().includes(term) ||
        item.classification?.why_it_matters?.toLowerCase().includes(term)
      );
    }
    
    // Category filter
    if (selectedCategory) {
      filtered = filtered.filter(item => 
        item.classification?.category === selectedCategory
      );
    }
    
    // Jurisdiction filter
    if (selectedJurisdiction) {
      filtered = filtered.filter(item => 
        item.classification?.jurisdiction === selectedJurisdiction
      );
    }
    
    // Impact level filter
    if (selectedImpact) {
      filtered = filtered.filter(item => 
        item.classification?.impact_level === selectedImpact
      );
    }
    
    // Sort
    if (sortBy === 'date-desc') {
      filtered.sort((a, b) => new Date(b.published) - new Date(a.published));
    } else if (sortBy === 'date-asc') {
      filtered.sort((a, b) => new Date(a.published) - new Date(b.published));
    } else if (sortBy === 'impact') {
      const impactOrder = { 'Critical': 0, 'Important': 1, 'Informational': 2 };
      filtered.sort((a, b) => 
        (impactOrder[a.classification?.impact_level] ?? 3) - 
        (impactOrder[b.classification?.impact_level] ?? 3)
      );
    }
    
    setFilteredUpdates(filtered);
  }, [updates, searchTerm, selectedCategory, selectedJurisdiction, selectedImpact, sortBy]);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getImpactBadgeColor = (level) => {
    switch (level) {
      case 'Critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'Important': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Informational': return 'bg-blue-100 text-blue-800 border-blue-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getImpactEmoji = (level) => {
    switch (level) {
      case 'Critical': return '🔥';
      case 'Important': return '⚠️';
      case 'Informational': return 'ℹ️';
      default: return '📌';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-navy-900 mb-2">Regulatory Intelligence</h1>
          <p className="text-gray-600">Loading updates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <style jsx global>{`
        :root {
          --navy: #1a3a52;
          --gold: #d4af37;
        }
      `}</style>
      
      <style jsx>{`
        .text-navy-900 { color: var(--navy); }
        .text-gold { color: var(--gold); }
        .border-gold { border-color: var(--gold); }
        .bg-navy { background-color: var(--navy); }
      `}</style>

      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-navy-900 mb-1">Regulatory Intelligence</h1>
              <p className="text-gray-600">Private Client Solutions Knowledge Hub</p>
            </div>
            <div className="text-right text-sm text-gray-500">
              {lastScraped && (
                <p>Last updated: {formatDate(lastScraped)}</p>
              )}
              <p className="text-gray-600 font-semibold mt-1">{filteredUpdates.length} updates</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-7xl mx-auto px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-800">
            <p className="font-semibold">Error loading data</p>
            <p className="text-sm mt-1">{error}</p>
            <p className="text-sm mt-2 text-gray-600">
              Make sure to set <code className="bg-red-100 px-2 py-1 rounded">YOUR_GITHUB_USERNAME</code> in the page code.
            </p>
          </div>
        )}

        {/* Filters */}
        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 mb-8">
          <div className="mb-4">
            <label className="block text-sm font-semibold text-navy-900 mb-2">Search</label>
            <input
              type="text"
              placeholder="Search by keyword, source, or topic..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-navy-900 focus:ring-1 focus:ring-navy-900"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-semibold text-navy-900 mb-2">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-navy-900 focus:ring-1 focus:ring-navy-900"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-navy-900 mb-2">Jurisdiction</label>
              <select
                value={selectedJurisdiction}
                onChange={(e) => setSelectedJurisdiction(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-navy-900 focus:ring-1 focus:ring-navy-900"
              >
                <option value="">All Jurisdictions</option>
                {jurisdictions.map(jur => (
                  <option key={jur} value={jur}>{jur}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-navy-900 mb-2">Impact Level</label>
              <select
                value={selectedImpact}
                onChange={(e) => setSelectedImpact(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-navy-900 focus:ring-1 focus:ring-navy-900"
              >
                <option value="">All Levels</option>
                {impacts.map(imp => (
                  <option key={imp} value={imp}>{imp}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-navy-900 mb-2">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-navy-900 focus:ring-1 focus:ring-navy-900"
              >
                <option value="date-desc">Newest First</option>
                <option value="date-asc">Oldest First</option>
                <option value="impact">By Impact</option>
              </select>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            Showing {filteredUpdates.length} of {updates.length} updates
          </div>
        </div>

        {/* Updates List */}
        {filteredUpdates.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No updates match your filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredUpdates.map((item, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                {/* Header with impact badge */}
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-navy-900 leading-tight">
                      {item.title}
                    </h3>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getImpactBadgeColor(item.classification?.impact_level)}`}>
                      {getImpactEmoji(item.classification?.impact_level)} {item.classification?.impact_level}
                    </span>
                  </div>
                </div>

                {/* Metadata */}
                <div className="flex flex-wrap gap-2 mb-3 text-sm text-gray-600">
                  <span className="font-medium">{item.source}</span>
                  <span>•</span>
                  <span>{formatDate(item.published)}</span>
                  {item.classification?.category && (
                    <>
                      <span>•</span>
                      <span className="inline-block px-2 py-1 bg-gray-100 rounded text-navy-900 font-medium">
                        {item.classification.category}
                      </span>
                    </>
                  )}
                  {item.classification?.jurisdiction && (
                    <>
                      <span>•</span>
                      <span className="text-gray-700">{item.classification.jurisdiction}</span>
                    </>
                  )}
                </div>

                {/* One-line summary */}
                {item.classification?.one_line_summary && (
                  <p className="text-gray-700 font-medium mb-3 text-sm">
                    {item.classification.one_line_summary}
                  </p>
                )}

                {/* Why it matters */}
                {item.classification?.why_it_matters && (
                  <div className="bg-blue-50 border-l-2 border-blue-300 p-3 mb-4">
                    <p className="text-sm text-blue-900">
                      <span className="font-semibold">Why it matters:</span> {item.classification.why_it_matters}
                    </p>
                  </div>
                )}

                {/* Source link */}
                {item.url && (
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm font-medium text-gold hover:underline"
                  >
                    View Source
                    <svg className="ml-1 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}

                {/* Confidence indicator */}
                {item.classification?.confidence !== undefined && (
                  <p className="text-xs text-gray-400 mt-2">
                    Classification confidence: {Math.round(item.classification.confidence * 100)}%
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-8 text-center text-sm text-gray-500">
          <p>Regulatory Intelligence Dashboard | Updates automatically at 8 AM IST daily</p>
          <p className="mt-1">Last sync: {lastScraped ? formatDate(lastScraped) : 'Never'}</p>
        </div>
      </div>
    </div>
  );
}
