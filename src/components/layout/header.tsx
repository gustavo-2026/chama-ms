'use client';

import { useEffect, useState } from 'react';
import { Bell, Search, Sun, Moon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

export function Header({ title, subtitle }: HeaderProps) {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    setDark(document.documentElement.classList.contains('dark'));
  }, []);

  const toggleTheme = () => {
    const newDark = !dark;
    setDark(newDark);
    if (newDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('chama_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('chama_theme', 'light');
    }
  };

  return (
    <header
      className="sticky top-0 z-10 flex h-16 items-center gap-4 px-6 transition-theme"
      style={{
        background: 'var(--header-bg)',
        borderBottom: '1px solid var(--header-border)',
      }}
    >
      {/* Title */}
      <div className="flex-1">
        <h1 className="text-xl font-semibold" style={{ color: 'var(--foreground)' }}>{title}</h1>
        {subtitle && (
          <p className="text-sm" style={{ color: 'var(--muted)' }}>{subtitle}</p>
        )}
      </div>

      {/* Search */}
      <div className="relative w-64 hidden md:block">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: 'var(--muted)' }} />
        <Input
          type="search"
          placeholder="Search..."
          className="pl-9"
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        {/* Dark mode toggle */}
        <Button variant="ghost" size="sm" onClick={toggleTheme} title={dark ? 'Light mode' : 'Dark mode'}>
          {dark ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} />}
        </Button>

        <Button variant="ghost" size="sm" className="relative">
          <Bell size={20} />
          <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-[10px] text-white flex items-center justify-center">
            3
          </span>
        </Button>

        <div className="flex items-center gap-2 ml-4">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-medium">
            A
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>Admin</p>
            <p className="text-xs" style={{ color: 'var(--muted)' }}>Super Admin</p>
          </div>
        </div>
      </div>
    </header>
  );
}
