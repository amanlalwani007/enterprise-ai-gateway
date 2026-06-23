import React from 'react';
import { LayoutDashboard, Users, CreditCard, ShieldAlert, BarChart3, Settings } from 'lucide-react';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200">
        <div className="p-6">
          <h1 className="text-xl font-bold text-indigo-600">AI Gateway</h1>
        </div>
        <nav className="mt-6">
          <a href="#" className="flex items-center px-6 py-3 text-gray-700 bg-gray-100 border-r-4 border-indigo-600">
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-700">
            <Users className="w-5 h-5 mr-3" />
            Teams
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-700">
            <CreditCard className="w-5 h-5 mr-3" />
            Budgets
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-700">
            <ShieldAlert className="w-5 h-5 mr-3" />
            PII Masking
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-700">
            <BarChart3 className="w-5 h-5 mr-3" />
            Analytics
          </a>
          <a href="#" className="flex items-center px-6 py-3 text-gray-500 hover:bg-gray-50 hover:text-gray-700">
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="bg-white border-b border-gray-200 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-gray-800">Usage Overview</h2>
          <div className="flex items-center">
            <span className="text-sm text-gray-500 mr-4">Organization: Acme Corp</span>
            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold text-sm">
              A
            </div>
          </div>
        </header>
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
