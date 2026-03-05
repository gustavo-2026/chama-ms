import Link from 'next/link';
export default function SettingsPage() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-logo">🏦 Chama Admin</div>
        <nav className="sidebar-nav">
          <Link href="/dashboard" className="nav-item">📊 Dashboard</Link>
          <Link href="/chamas" className="nav-item">🏢 Chamas</Link>
          <Link href="/members" className="nav-item">👥 Members</Link>
          <Link href="/transactions" className="nav-item">💰 Transactions</Link>
          <Link href="/settings" className="nav-item">⚙️ Settings</Link>
        </nav>
      </aside>
      <main className="main-content">
        <h1 className="page-title">Settings</h1>
        <div className="card"><p>Settings page content coming soon...</p></div>
      </main>
    </div>
  );
}
