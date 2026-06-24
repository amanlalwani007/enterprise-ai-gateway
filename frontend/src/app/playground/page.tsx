'use client';
import React, { useState } from 'react';
import DashboardLayout from '../../components/DashboardLayout';
import { Send, RefreshCw } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface CompareResult {
  model: string;
  content?: string;
  tokens?: number;
  cost?: number;
  error?: string;
}

export default function PlaygroundPage() {
  const [prompt, setPrompt] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [models, setModels] = useState('["gpt-4", "gpt-3.5-turbo"]');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(256);
  const [results, setResults] = useState<CompareResult[]>([]);
  const [loading, setLoading] = useState(false);

  async function handleCompare() {
    if (!prompt.trim()) return;
    setLoading(true);
    setResults([]);
    try {
      const params = new URLSearchParams({
        prompt,
        models,
        temperature: temperature.toString(),
        max_tokens: maxTokens.toString(),
      });
      if (systemPrompt) params.set('system_prompt', systemPrompt);

      const res = await fetch(`${API_BASE}/v1/admin/playground/compare?${params}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch (err) {
      setResults([{ model: 'error', error: 'Failed to compare models' }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Prompt Playground</h2>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">System Prompt</label>
              <textarea
                className="w-full border border-gray-300 rounded-lg p-3 text-sm h-24"
                placeholder="Optional system prompt..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Prompt</label>
              <textarea
                className="w-full border border-gray-300 rounded-lg p-3 text-sm h-32"
                placeholder="Enter your prompt..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Models (JSON array)</label>
              <input
                className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                value={models}
                onChange={(e) => setModels(e.target.value)}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Temperature</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                  step="0.1"
                  min="0"
                  max="2"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Tokens</label>
                <input
                  type="number"
                  className="w-full border border-gray-300 rounded-lg p-2 text-sm"
                  min="1"
                  max="4096"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                />
              </div>
            </div>

            <button
              onClick={handleCompare}
              disabled={loading || !prompt.trim()}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
              {loading ? 'Comparing...' : 'Compare Models'}
            </button>
          </div>

          <div className="lg:col-span-2 space-y-4">
            {results.length === 0 && !loading && (
              <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-400">
                Enter a prompt and click Compare to see results side-by-side
              </div>
            )}

            {results.map((r, i) => (
              <div key={i} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex justify-between">
                  <span className="font-mono text-sm font-medium text-indigo-600">{r.model}</span>
                  {r.tokens && <span className="text-xs text-gray-500">{r.tokens} tokens</span>}
                </div>
                <div className="p-4 text-sm text-gray-800 whitespace-pre-wrap">
                  {r.content || <span className="text-red-500">{r.error}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
