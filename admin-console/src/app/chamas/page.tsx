'use client';
import Link from 'next/link';
const mockChamas = [{ id: 1, name: 'Nairobi Professionals', code: 'NP001', members: 45, status: 'active' }, { id: 2, name: 'Kenya Women Savings', code: 'KWS002', members: 38, status: 'active' }, { id: 3, name: 'Nairobi Traders', code: 'NT003', members: 52, status: 'active' }];
export default function ChamasPage() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">🏦 Chama Admin</div>
        <nav className="sidebar-nav">
          <Link href="/dashboard" className="nav-item">📊 Dashboard</Link>
          <Link href="/chamas" className="nav-item active">🏢 Chamas</Link>
          <Link href="/members" className="nav-item">👥 Members</Link>
          <Link href="/transactions" className="nav-item">💰 Transactions</Link>
          <Link href="/settings" className="nav-item">⚙️ Settings</Link>
        </nav>
      </aside>
      <main className="main-content">
        <h1 className="page-title">Chamas</h1>
        <div className="card">
          <table><thead><tr><th>Name</th><th>Code</th><th>Members</th><th>Status</th></tr></thead>
            <tbody>{mockChamas.map(c => <tr key={c.id}><td>{c.name}</td><td><code>{c.code}</code></td><td>{c.members}</td><td><span className="badge badge-success">{c.status}</span></td></tr>)}</tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
