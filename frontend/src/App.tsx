import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import CaptureQueue from './screens/CaptureQueue'
import Fleet from './screens/Fleet'
import Indicators from './screens/Indicators'
import SignalQueue from './screens/SignalQueue'
import NCDrafts from './screens/NCDrafts'

// The five screens of plan/DASHBOARD.md. Capture queue is the one that matters.
const nav = [
  { to: '/capture', label: 'Capture queue' },
  { to: '/fleet', label: 'Fleet' },
  { to: '/indicators', label: 'Indicators' },
  { to: '/signals', label: 'Signals' },
  { to: '/ncs', label: 'NC drafts' },
]

export default function App() {
  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900">
      <header className="flex items-center gap-6 border-b border-neutral-200 bg-white px-6 py-3">
        <span className="font-semibold tracking-tight">Asteria PMS</span>
        <nav className="flex gap-4 text-sm">
          {nav.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                isActive ? 'text-neutral-900 font-medium' : 'text-neutral-500 hover:text-neutral-900'
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="p-6">
        <Routes>
          <Route path="/" element={<Navigate to="/capture" replace />} />
          <Route path="/capture" element={<CaptureQueue />} />
          <Route path="/fleet" element={<Fleet />} />
          <Route path="/indicators" element={<Indicators />} />
          <Route path="/signals" element={<SignalQueue />} />
          <Route path="/ncs" element={<NCDrafts />} />
        </Routes>
      </main>
    </div>
  )
}
