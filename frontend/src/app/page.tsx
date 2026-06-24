'use client';
import React, { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { ArrowUpRight, ArrowDownRight, DollarSign, Zap, ShieldCheck, BarChart3 } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardData {
  summary: { total_cost: number; total_tokens: number; total_requests: number };
  logs: Array<{ id: number; user_id: string; model: string; total_tokens: number; cost: number; created_at: string }>;
  cache_savings: { estimated_savings_usd: number; total_hits: number; cache_entries: number };
}

function formatCost(cost: number): string {
  return '$' + cost.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return (tokens / 1_000_000).toFixed(1) + 'M';
  if (tokens >= 1_000) return (tokens / 1_000).toFixed(1) + 'K';
  return tokens.toString();
}

export default function Home() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [summaryRes, logsRes, cacheRes] = await Promise.all([
          fetch(`${API_BASE}/v1/admin/costs/summary`),
          fetch(`${API_BASE}/v1/admin/logs/recent?limit=10`),
          fetch(`${API_BASE}/v1/admin/cache/savings`),
        ]);
        if (!summaryRes.ok || !logsRes.ok || !cacheRes.ok) {
          throw new Error('Failed to fetch dashboard data');
        }
        const summaryData = await summaryRes.json();
        const logsData = await logsRes.json();
        const cacheData = await cacheRes.json();
        setData({
          summary: summaryData.summary,
          logs: logsData,
          cache_savings: cacheData,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-500">Loading dashboard data...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !data) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <p className="text-red-500">Could not load dashboard: {error}</p>
        </div>
      </DashboardLayout>
    );
  }

  const { summary, logs, cache_savings } = data;

  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-green-50 rounded-lg text-green-600">
              <DollarSign className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Total Spend</h3>
          <p className="text-2xl font-bold text-gray-900">{formatCost(summary.total_cost)}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Zap className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Tokens Processed</h3>
          <p className="text-2xl font-bold text-gray-900">{formatTokens(summary.total_tokens)}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-orange-50 rounded-lg text-orange-600">
              <BarChart3 className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Cache Savings</h3>
          <p className="text-2xl font-bold text-gray-900">{formatCost(cache_savings.estimated_savings_usd)}</p>
        </div>

        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Cache Hits</h3>
          <p className="text-2xl font-bold text-gray-900">{cache_savings.total_hits.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold text-gray-800">Request Summary</h3>
          </div>
          <div className="p-6 space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-500">Total Requests</span>
              <span className="font-semibold">{summary.total_requests.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Cache Entries</span>
              <span className="font-semibold">{cache_savings.cache_entries.toLocaleString()}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">Recent API Logs</h3>
          </div>
          <div className="p-6 space-y-4">
            {logs.length === 0 && <p className="text-gray-400 text-sm">No logs yet</p>}
            {logs.slice(0, 5).map((log) => (
              <div key={log.id} className="flex items-start">
                <div className="p-2 bg-gray-50 rounded text-gray-400 mr-4">
                  <Zap className="w-4 h-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-gray-900 font-medium truncate">
                    {log.user_id} called {log.model}
                  </p>
                  <p className="text-xs text-gray-500">
                    {log.total_tokens} tokens &bull; {formatCost(log.cost)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
