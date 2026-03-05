'use client';
import Link from 'next/link';
const Sidebar = () => (
  <aside className="sidebar">
    <div className="sidebar-logo">🏦 Chama Admin</div>
    <nav className="sidebar-nav">
      <Link href="/dashboard" className="nav-item active">📊 Dashboard</Link>
      <Link href="/chamas" className="nav-item">🏢 Chamas</Link>
      <Link href="/members" className="nav-item">👥 Members</Link>
      <Link href="/transactions" className="nav-item">💰 Transactions</Link>
      <Link href="/settings" className="nav-item">⚙️ Settings</Link>
    </nav>
  </aside>
);
export default function DashboardPage() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <h1 className="page-title">Dashboard</h1>
        <div className="stats-grid">
          {[{ label: 'Total Chamas', value: '89', change: '+18%' }, { label: 'Total Members', value: '2,847', change: '+12%' }, { label: 'Volume', value: 'KES 5.2M', change: '+24%' }, { label: 'Revenue', value: 'KES 156K', change: '+8%' }].map(s => (
            <div key={s.label} className="stat-card"><div className="stat-label">{s.label}</div><div className="stat-value">{s.value}</div><div style={{ color: '#10b981', fontSize: '0.875rem', marginTop: '0.5rem' }}>↑ {s.change}</div></div>
          ))}
        </div>
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Recent Activity</h3>
          <table><thead><tr><th>Action</th><th>Chama</th><th>Status</th></tr></thead>
            <tbody>
              <tr><td>New chama registered</td><td>Kenya Women Savings</td><td><span className="badge badge-success">Active</span></td></tr>
              <tr><td>Large contribution</td><td>Nairobi Traders</td><td><span className="badge badge-success">Completed</span></td></tr>
              <tr><td>Loan approved</td><td>Mombasa Fishers</td><td><span className="badge badge-success">Approved</span></td></tr>
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
