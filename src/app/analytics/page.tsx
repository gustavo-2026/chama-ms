'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Select } from '@/components/ui/input';
import { formatCurrency, formatNumber } from '@/lib/utils';
import {
    AreaChart, Area,
    BarChart, Bar,
    PieChart, Pie, Cell,
    LineChart, Line,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
    TrendingUp,
    TrendingDown,
    DollarSign,
    Users,
    Building2,
    ArrowUpRight,
} from 'lucide-react';

// Mock data
const monthlyContributions = [
    { month: 'Apr', amount: 280000, loans: 120000 },
    { month: 'May', amount: 320000, loans: 180000 },
    { month: 'Jun', amount: 350000, loans: 150000 },
    { month: 'Jul', amount: 310000, loans: 200000 },
    { month: 'Aug', amount: 380000, loans: 160000 },
    { month: 'Sep', amount: 420000, loans: 220000 },
    { month: 'Oct', amount: 395000, loans: 175000 },
    { month: 'Nov', amount: 450000, loans: 250000 },
    { month: 'Dec', amount: 520000, loans: 300000 },
    { month: 'Jan', amount: 480000, loans: 270000 },
    { month: 'Feb', amount: 540000, loans: 310000 },
    { month: 'Mar', amount: 580000, loans: 280000 },
];

const loanBreakdown = [
    { name: 'Active', value: 45, color: '#3b82f6' },
    { name: 'Completed', value: 120, color: '#22c55e' },
    { name: 'Pending', value: 15, color: '#f59e0b' },
    { name: 'Defaulted', value: 8, color: '#ef4444' },
];

const topChamas = [
    { name: 'Mwanzo Group', contributions: 450000, members: 50 },
    { name: 'Faraja Savings', contributions: 420000, members: 50 },
    { name: 'Tujitegemee', contributions: 380000, members: 48 },
    { name: 'Chama Maendeleo', contributions: 320000, members: 50 },
    { name: 'Umoja Kazi', contributions: 180000, members: 45 },
];

const memberGrowth = [
    { month: 'Apr', members: 150, active: 140 },
    { month: 'May', members: 165, active: 155 },
    { month: 'Jun', members: 178, active: 168 },
    { month: 'Jul', members: 190, active: 178 },
    { month: 'Aug', members: 205, active: 192 },
    { month: 'Sep', members: 215, active: 200 },
    { month: 'Oct', members: 222, active: 208 },
    { month: 'Nov', members: 230, active: 215 },
    { month: 'Dec', members: 238, active: 222 },
    { month: 'Jan', members: 243, active: 228 },
    { month: 'Feb', members: 248, active: 235 },
    { month: 'Mar', members: 250, active: 240 },
];

export default function AnalyticsPage() {
    const [period, setPeriod] = useState('12months');

    const totalContributions = monthlyContributions.reduce((sum, d) => sum + d.amount, 0);
    const totalLoans = monthlyContributions.reduce((sum, d) => sum + d.loans, 0);
    const prevContributions = monthlyContributions.slice(0, 6).reduce((sum, d) => sum + d.amount, 0);
    const currContributions = monthlyContributions.slice(6).reduce((sum, d) => sum + d.amount, 0);
    const contributionGrowth = ((currContributions - prevContributions) / prevContributions * 100).toFixed(1);

    return (
        <DashboardLayout>
            <Header title="Analytics" subtitle="Platform performance and insights" />

            <div className="p-6 space-y-6">
                {/* Controls */}
                <div className="flex justify-between items-center">
                    <div className="flex gap-2">
                        <Select value={period} onChange={(e) => setPeriod(e.target.value)}>
                            <option value="6months">Last 6 Months</option>
                            <option value="12months">Last 12 Months</option>
                            <option value="ytd">Year to Date</option>
                        </Select>
                    </div>
                </div>

                {/* KPI Cards */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Total Contributions</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{formatCurrency(totalContributions)}</p>
                                </div>
                                <div className="p-2 rounded-lg bg-green-100">
                                    <DollarSign className="h-5 w-5 text-green-600" />
                                </div>
                            </div>
                            <div className="flex items-center gap-1 mt-2 text-green-600 text-sm">
                                <TrendingUp className="h-4 w-4" />
                                <span>+{contributionGrowth}% growth</span>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Total Loans</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{formatCurrency(totalLoans)}</p>
                                </div>
                                <div className="p-2 rounded-lg bg-blue-100">
                                    <ArrowUpRight className="h-5 w-5 text-blue-600" />
                                </div>
                            </div>
                            <div className="flex items-center gap-1 mt-2 text-blue-600 text-sm">
                                <TrendingUp className="h-4 w-4" />
                                <span>{loanBreakdown[0].value} active loans</span>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Active Members</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{formatNumber(240)}</p>
                                </div>
                                <div className="p-2 rounded-lg bg-purple-100">
                                    <Users className="h-5 w-5 text-purple-600" />
                                </div>
                            </div>
                            <div className="flex items-center gap-1 mt-2 text-purple-600 text-sm">
                                <TrendingUp className="h-4 w-4" />
                                <span>96% retention rate</span>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Active Chamas</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{formatNumber(5)}</p>
                                </div>
                                <div className="p-2 rounded-lg bg-orange-100">
                                    <Building2 className="h-5 w-5 text-orange-600" />
                                </div>
                            </div>
                            <div className="flex items-center gap-1 mt-2 text-orange-600 text-sm">
                                <TrendingUp className="h-4 w-4" />
                                <span>4 in good standing</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Charts Row 1 */}
                <div className="grid gap-6 lg:grid-cols-2">
                    {/* Contribution Trends */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Contribution & Loan Trends</CardTitle>
                            <CardDescription>Monthly financial flow over the last 12 months</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={monthlyContributions}>
                                    <defs>
                                        <linearGradient id="colorContributions" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorLoans" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--table-border)" />
                                    <XAxis dataKey="month" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                                    <YAxis tick={{ fill: 'var(--muted)', fontSize: 12 }} tickFormatter={(v) => `${v / 1000}k`} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--card-bg)',
                                            border: '1px solid var(--card-border)',
                                            borderRadius: '8px',
                                            color: 'var(--foreground)',
                                        }}
                                        formatter={(value: number) => [formatCurrency(value), '']}
                                    />
                                    <Legend />
                                    <Area type="monotone" dataKey="amount" name="Contributions" stroke="#22c55e" fill="url(#colorContributions)" strokeWidth={2} />
                                    <Area type="monotone" dataKey="loans" name="Loans" stroke="#3b82f6" fill="url(#colorLoans)" strokeWidth={2} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Loan Status Pie */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Loan Status Distribution</CardTitle>
                            <CardDescription>Breakdown of all loans by current status</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={loanBreakdown}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={70}
                                        outerRadius={110}
                                        paddingAngle={4}
                                        dataKey="value"
                                        label={({ name, value }) => `${name}: ${value}`}
                                    >
                                        {loanBreakdown.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--card-bg)',
                                            border: '1px solid var(--card-border)',
                                            borderRadius: '8px',
                                            color: 'var(--foreground)',
                                        }}
                                    />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>

                {/* Charts Row 2 */}
                <div className="grid gap-6 lg:grid-cols-2">
                    {/* Top Chamas */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Top Chamas by Contributions</CardTitle>
                            <CardDescription>Highest contributing organizations</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={topChamas} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--table-border)" />
                                    <XAxis type="number" tick={{ fill: 'var(--muted)', fontSize: 12 }} tickFormatter={(v) => `${v / 1000}k`} />
                                    <YAxis type="category" dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 12 }} width={120} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--card-bg)',
                                            border: '1px solid var(--card-border)',
                                            borderRadius: '8px',
                                            color: 'var(--foreground)',
                                        }}
                                        formatter={(value: number) => [formatCurrency(value), 'Contributions']}
                                    />
                                    <Bar dataKey="contributions" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    {/* Member Growth */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Member Growth</CardTitle>
                            <CardDescription>Total vs active members over time</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={memberGrowth}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--table-border)" />
                                    <XAxis dataKey="month" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                                    <YAxis tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'var(--card-bg)',
                                            border: '1px solid var(--card-border)',
                                            borderRadius: '8px',
                                            color: 'var(--foreground)',
                                        }}
                                    />
                                    <Legend />
                                    <Line type="monotone" dataKey="members" name="Total Members" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} />
                                    <Line type="monotone" dataKey="active" name="Active Members" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </DashboardLayout>
    );
}
