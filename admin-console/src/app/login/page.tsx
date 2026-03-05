'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (email === 'admin@chama.ke' && password === 'admin') router.push('/dashboard');
  };
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #111827 0%, #4f46e5 100%)' }}>
      <div style={{ background: 'white', borderRadius: '1rem', padding: '2.5rem', width: '100%', maxWidth: '420px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' }}>
        <h1 style={{ textAlign: 'center', fontSize: '1.75rem', marginBottom: '0.5rem' }}>🏦 Chama Admin</h1>
        <p style={{ textAlign: 'center', color: '#6b7280', marginBottom: '2rem' }}>Sign in to manage your platform</p>
        <form onSubmit={handleLogin}>
          <div className="form-group"><label className="form-label">Email</label><input type="email" className="form-input" placeholder="admin@chama.ke" value={email} onChange={e => setEmail(e.target.value)} /></div>
          <div className="form-group"><label className="form-label">Password</label><input type="password" className="form-input" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} /></div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>Sign In</button>
        </form>
        <p style={{ marginTop: '1.5rem', textAlign: 'center', color: '#6b7280', fontSize: '0.875rem' }}>Demo: admin@chama.ke / admin</p>
      </div>
    </div>
  );
}
