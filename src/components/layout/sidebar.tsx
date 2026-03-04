'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  Building2,
  CreditCard,
  DollarSign,
  Settings,
  FileText,
  LogOut,
  Menu,
  ChevronLeft,
  Activity,
  BarChart3,
  Calculator,
  Radio,
  GitCompareArrows,
  Target,
  Coins,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Chamas', href: '/chamas', icon: Building2 },
  { name: 'Members', href: '/members', icon: Users },
  { name: 'Transactions', href: '/transactions', icon: CreditCard },
  { name: 'Compare', href: '/compare', icon: GitCompareArrows },
  { name: 'Goals', href: '/goals', icon: Target },
  { name: 'Dividends', href: '/dividends', icon: Coins },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Calculator', href: '/calculator', icon: Calculator },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Events', href: '/events', icon: Radio },
  { name: 'Monitoring', href: '/monitoring', icon: Activity },
  { name: 'Settings', href: '/settings', icon: Settings },
];

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div
      className={cn(
        'flex flex-col h-screen text-white transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
      style={{ background: 'var(--sidebar-bg)' }}
    >
      {/* Logo */}
      <div className="flex h-16 items-center justify-between px-4" style={{ borderBottom: '1px solid var(--sidebar-border)' }}>
        {!collapsed && (
          <Link href="/dashboard" className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Chama Admin
          </Link>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
        >
          {collapsed ? <Menu size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-1 px-2">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-900/30'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white',
                    collapsed && 'justify-center'
                  )}
                  title={collapsed ? item.name : undefined}
                >
                  <item.icon size={20} className={isActive ? 'text-blue-200' : ''} />
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4" style={{ borderTop: '1px solid var(--sidebar-border)' }}>
        <Link
          href="/login"
          className={cn(
            'flex items-center gap-3 text-sm text-gray-500 hover:text-white transition-colors',
            collapsed && 'justify-center'
          )}
        >
          <LogOut size={20} />
          {!collapsed && <span>Logout</span>}
        </Link>
      </div>
    </div>
  );
}
