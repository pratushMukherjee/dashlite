import { NavLink } from 'react-router-dom';
import { Search, Files, MessageSquare, Bot, LayoutDashboard } from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/search', icon: Search, label: 'Search' },
  { to: '/files', icon: Files, label: 'Files' },
  { to: '/ask', icon: MessageSquare, label: 'Ask AI' },
  { to: '/agent', icon: Bot, label: 'Agent' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white border-r border-slate-200 flex flex-col">
      <div className="p-6 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900">
          <span className="text-blue-600">Dash</span>Lite
        </h1>
        <p className="text-xs text-slate-500 mt-1">AI-Powered File Intelligence</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-200">
        <p className="text-xs text-slate-400 text-center">
          Inspired by Dropbox Dash
        </p>
      </div>
    </aside>
  );
}
