'use client';

import { useEffect, useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency, formatNumber } from '@/lib/utils';
import {
  Building2,
  Users,
  DollarSign,
  TrendingUp,
  ArrowUpRight,
  ArrowDownRight,
  CreditCard,
  Activity,
} from 'lucide-react';
import Link from 'next/link';

// Mock data for demonstration
const mockStats = {
  total_chamas: 5,
  active_chamas: 5,
  total_members: 250,
  total_contributions: 1500000,
  total_loans: 2500000,
  platform_revenue: 45000,
};

const mockRecentActivity = [
  { id: 1, type: 'chama', action: 'New chama registered', name: 'Mwanzo Group', time: '2 hours ago' },
  { id: 2, type: 'member', action: 'New member joined', name: 'Grace Ochieng', time: '3 hours ago' },
  { id: 3, type: 'contribution', action: 'Contribution received', name: 'KES 5,000', time: '5 hours ago' },
  { id: 4, type: 'loan', action: 'Loan approved', name: 'KES 50,000', time: '1 day ago' },
];

const mockTopChamas = [
  { name: 'Mwanzo Group', members: 50, contributions: 450000, growth: 12 },
  { name: 'Tujitegemee', members: 48, contributions: 380000, growth: 8 },
  { name: 'Chama Maendeleo', members: 50, contributions: 320000, growth: -3 },
];

export default function DashboardPage() {
  const [stats] = useState(mockStats);

  const statsCards = [
    {
      title: 'Total Chamas',
      value: stats.total_chamas,
      icon: Building2,
      color: 'bg-blue-500',
      change: '+2 this month',
      changeType: 'positive' as const,
    },
    {
      title: 'Total Members',
      value: stats.total_members,
      icon: Users,
      color: 'bg-green-500',
      change: '+25 this month',
      changeType: 'positive' as const,
    },
    {
      title: 'Total Contributions',
      value: formatCurrency(stats.total_contributions),
      icon: DollarSign,
      color: 'bg-yellow-500',
      change: '+15% vs last month',
      changeType: 'positive' as const,
    },
    {
      title: 'Platform Revenue',
      value: formatCurrency(stats.platform_revenue),
      icon: TrendingUp,
      color: 'bg-purple-500',
      change: '+8% vs last month',
      changeType: 'positive' as const,
    },
  ];

  return (
    <DashboardLayout>
      <Header title="Dashboard" subtitle="Welcome back, Admin" />
      
      <div className="p-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statsCards.map((stat) => (
            <Card key={stat.title}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-lg ${stat.color}`}>
                      <stat.icon className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">
                        {stat.title}
                      </p>
                      <p className="text-2xl font-bold">{stat.value}</p>
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex items-center text-sm">
                  {stat.changeType === 'positive' ? (
                    <ArrowUpRight className="mr-1 h-4 w-4 text-green-500" />
                  ) : (
                    <ArrowDownRight className="mr-1 h-4 w-4 text-red-500" />
                  )}
                  <span className={stat.changeType === 'positive' ? 'text-green-500' : 'text-red-500'}>
                    {stat.change}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Charts and Tables */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Top Performing Chamas */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base font-medium">
                Top Performing Chamas
              </CardTitle>
              <Link href="/chamas">
                <Button variant="ghost" size="sm">
                  View all
                </Button>
              </Link>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockTopChamas.map((chama, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center text-sm font-medium text-primary-600">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {chama.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {chama.members} members
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">
                        {formatCurrency(chama.contributions)}
                      </p>
                      <p
                        className={`text-sm ${
                          chama.growth >= 0 ? 'text-green-500' : 'text-red-500'
                        }`}
                      >
                        {chama.growth >= 0 ? '+' : ''}
                        {chama.growth}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-base font-medium">
                Recent Activity
              </CardTitle>
              <Button variant="ghost" size="sm">
                View all
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockRecentActivity.map((activity) => (
                  <div
                    key={activity.id}
                    className="flex items-center gap-3"
                  >
                    <div className="h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center">
                      {activity.type === 'chama' && <Building2 className="h-4 w-4" />}
                      {activity.type === 'member' && <Users className="h-4 w-4" />}
                      {activity.type === 'contribution' && <CreditCard className="h-4 w-4" />}
                      {activity.type === 'loan' && <DollarSign className="h-4 w-4" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-gray-500">{activity.name}</p>
                    </div>
                    <p className="text-xs text-gray-400">{activity.time}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-4">
          <Link href="/chamas/onboard">
            <Button className="w-full h-12" variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              Onboard New Chama
            </Button>
          </Link>
          <Link href="/members">
            <Button className="w-full h-12" variant="outline">
              <Users className="mr-2 h-4 w-4" />
              Manage Members
            </Button>
          </Link>
          <Link href="/transactions">
            <Button className="w-full h-12" variant="outline">
              <Activity className="mr-2 h-4 w-4" />
              View Transactions
            </Button>
          </Link>
          <Link href="/reports">
            <Button className="w-full h-12" variant="outline">
              <TrendingUp className="mr-2 h-4 w-4" />
              Generate Reports
            </Button>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}
