import React, { useState, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState('');

  const startCrawl = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('http://localhost:8000/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to start crawl');
      }

      const data = await response.json();
      console.log('Crawl started:', data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/logs');
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      const data = await response.json();
      setLogs(data.logs);
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  useEffect(() => {
    const interval = setInterval(fetchLogs, 5000); // Rafraîchir les logs toutes les 5 secondes
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-2xl font-bold mb-4">Web Crawler</h1>
          
          <div className="flex gap-4 mb-6">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to crawl..."
              className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={startCrawl}
              disabled={loading || !url}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Crawling...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Start Crawl
                </>
              )}
            </button>
          </div>

          {error && (
            <div className="p-4 mb-6 bg-red-100 text-red-700 rounded-lg">
              {error}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Crawler Logs</h2>
          <div className="bg-gray-900 text-gray-100 p-4 rounded-lg h-[500px] overflow-y-auto font-mono text-sm">
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))
            ) : (
              <p className="text-gray-500">No logs available...</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;