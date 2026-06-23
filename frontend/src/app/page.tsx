import React from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { ArrowUpRight, ArrowDownRight, DollarSign, Zap, ShieldCheck, BarChart3 } from 'lucide-react';

export default function Home() {
  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Total Spend Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-green-50 rounded-lg text-green-600">
              <DollarSign className="w-6 h-6" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full flex items-center">
              <ArrowUpRight className="w-3 h-3 mr-1" /> 12%
            </span>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Total Spend</h3>
          <p className="text-2xl font-bold text-gray-900">$1,284.50</p>
        </div>

        {/* Tokens Processed Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
              <Zap className="w-6 h-6" />
            </div>
            <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full flex items-center">
              <ArrowUpRight className="w-3 h-3 mr-1" /> 8%
            </span>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Tokens Processed</h3>
          <p className="text-2xl font-bold text-gray-900">4.2M</p>
        </div>

        {/* Cache Hit Rate Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-orange-50 rounded-lg text-orange-600">
              <BarChart3 className="w-6 h-6" />
            </div>
            <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded-full flex items-center">
              <ArrowDownRight className="w-3 h-3 mr-1" /> 3%
            </span>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">Cache Hit Rate</h3>
          <p className="text-2xl font-bold text-gray-900">32.4%</p>
        </div>

        {/* PII Masked Card */}
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
              <ShieldCheck className="w-6 h-6" />
            </div>
          </div>
          <h3 className="text-gray-500 text-sm font-medium">PII Masked</h3>
          <p className="text-2xl font-bold text-gray-900">1,420</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Team Spend Table */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-semibold text-gray-800">Spend by Team</h3>
            <button className="text-sm text-indigo-600 font-medium hover:text-indigo-700">View All</button>
          </div>
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th className="px-6 py-3 font-semibold">Team Name</th>
                <th className="px-6 py-3 font-semibold">Budget Used</th>
                <th className="px-6 py-3 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Marketing</td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full mr-2">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: '82%' }}></div>
                    </div>
                    <span className="text-xs text-gray-500">$410 / $500</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-xs font-medium text-orange-600">Warning</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Engineering</td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full mr-2">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: '45%' }}></div>
                    </div>
                    <span className="text-xs text-gray-500">$900 / $2,000</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-xs font-medium text-green-600">Healthy</td>
              </tr>
              <tr>
                <td className="px-6 py-4 text-sm text-gray-900">Product</td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <div className="flex-1 h-2 bg-gray-100 rounded-full mr-2">
                      <div className="h-full bg-red-500 rounded-full" style={{ width: '100%' }}></div>
                    </div>
                    <span className="text-xs text-gray-500">$1,000 / $1,000</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-xs font-medium text-red-600">Blocked</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
          <div className="p-6 border-b border-gray-200">
            <h3 className="font-semibold text-gray-800">Recent API Logs</h3>
          </div>
          <div className="p-6 space-y-6">
            <div className="flex items-start">
              <div className="p-2 bg-gray-50 rounded text-gray-400 mr-4">
                <Zap className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm text-gray-900 font-medium">marketing-api-key called gpt-4-turbo</p>
                <p className="text-xs text-gray-500">2 minutes ago • 1,240 tokens • $0.037</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="p-2 bg-orange-50 rounded text-orange-600 mr-4">
                <BarChart3 className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm text-gray-900 font-medium">Cache Hit for "Explain quantum computing..."</p>
                <p className="text-xs text-gray-500">12 minutes ago • Saved $0.02</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="p-2 bg-blue-50 rounded text-blue-600 mr-4">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm text-gray-900 font-medium">PII Masked in request from engineering-team</p>
                <p className="text-xs text-gray-500">45 minutes ago • SSN detected</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
