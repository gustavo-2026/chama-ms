'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
    GitCompareArrows,
    TrendingUp,
    TrendingDown,
    Users,
    DollarSign,
    ShieldCheck,
    AlertTriangle,
    Check,
} from 'lucide-react';

interface ChamaData {
    id: string;
    name: string;
    members: number;
    totalContributions: number;
    monthlyContribution: number;
    loansIssued: number;
    loanDefaultRate: number;
    growthRate: number;
    activeMemberRate: number;
    avgContributionPerMember: number;
    region: string;
    status: string;
    color: string;
}

const chamaData: ChamaData[] = [
    {
        id: '1', name: 'Mwanzo Group', members: 50, totalContributions: 450000,
        monthlyContribution: 45000, loansIssued: 35, loanDefaultRate: 2.1,
        growthRate: 12, activeMemberRate: 96, avgContributionPerMember: 9000,
        region: 'Nairobi', status: 'ACTIVE', color: '#3b82f6',
    },
    {
        id: '2', name: 'Tujitegemee', members: 48, totalContributions: 380000,
        monthlyContribution: 38000, loansIssued: 28, loanDefaultRate: 1.5,
        growthRate: 8, activeMemberRate: 98, avgContributionPerMember: 7917,
        region: 'Mombasa', status: 'ACTIVE', color: '#22c55e',
    },
    {
        id: '3', name: 'Chama Maendeleo', members: 50, totalContributions: 320000,
        monthlyContribution: 32000, loansIssued: 22, loanDefaultRate: 3.2,
        growthRate: -3, activeMemberRate: 90, avgContributionPerMember: 6400,
        region: 'Kisumu', status: 'ACTIVE', color: '#f59e0b',
    },
    {
        id: '4', name: 'Umoja Kazi', members: 45, totalContributions: 180000,
        monthlyContribution: 18000, loansIssued: 15, loanDefaultRate: 8.5,
        growthRate: -5, activeMemberRate: 78, avgContributionPerMember: 4000,
        region: 'Nakuru', status: 'SUSPENDED', color: '#ef4444',
    },
    {
        id: '5', name: 'Faraja Savings', members: 50, totalContributions: 420000,
        monthlyContribution: 42000, loansIssued: 30, loanDefaultRate: 0.8,
        growthRate: 15, activeMemberRate: 100, avgContributionPerMember: 8400,
        region: 'Eldoret', status: 'ACTIVE', color: '#8b5cf6',
    },
];

const monthlyPerformance = [
    { month: 'Oct', Mwanzo: 42000, Tujitegemee: 36000, Maendeleo: 34000, Umoja: 20000, Faraja: 40000 },
    { month: 'Nov', Mwanzo: 44000, Tujitegemee: 37000, Maendeleo: 33000, Umoja: 19000, Faraja: 41000 },
    { month: 'Dec', Mwanzo: 48000, Tujitegemee: 38000, Maendeleo: 32000, Umoja: 18000, Faraja: 43000 },
    { month: 'Jan', Mwanzo: 43000, Tujitegemee: 37500, Maendeleo: 31000, Umoja: 17000, Faraja: 41500 },
    { month: 'Feb', Mwanzo: 46000, Tujitegemee: 39000, Maendeleo: 33000, Umoja: 18500, Faraja: 42000 },
    { month: 'Mar', Mwanzo: 45000, Tujitegemee: 38000, Maendeleo: 32000, Umoja: 18000, Faraja: 42000 },
];

export default function ComparePage() {
    const [selected, setSelected] = useState<string[]>(['1', '2']);

    const toggleChama = (id: string) => {
        setSelected((prev) =>
            prev.includes(id) ? prev.filter((s) => s !== id) : prev.length < 3 ? [...prev, id] : prev
        );
    };

    const selectedChamas = chamaData.filter((c) => selected.includes(c.id));

    // Radar data (normalized to 100)
    const maxContrib = Math.max(...chamaData.map((c) => c.totalContributions));
    const maxMembers = Math.max(...chamaData.map((c) => c.members));

    const radarData = [
        { metric: 'Contributions', ...Object.fromEntries(selectedChamas.map((c) => [c.name, Math.round((c.totalContributions / maxContrib) * 100)])) },
        { metric: 'Members', ...Object.fromEntries(selectedChamas.map((c) => [c.name, Math.round((c.members / maxMembers) * 100)])) },
        { metric: 'Growth', ...Object.fromEntries(selectedChamas.map((c) => [c.name, Math.max(0, Math.min(100, c.growthRate * 5 + 50))])) },
        { metric: 'Activity', ...Object.fromEntries(selectedChamas.map((c) => [c.name, c.activeMemberRate])) },
        { metric: 'Loan Health', ...Object.fromEntries(selectedChamas.map((c) => [c.name, Math.max(0, 100 - c.loanDefaultRate * 10)])) },
        { metric: 'Avg/Member', ...Object.fromEntries(selectedChamas.map((c) => [c.name, Math.round((c.avgContributionPerMember / 10000) * 100)])) },
    ];

    return (
        <DashboardLayout>
            <Header title="Chama Comparison" subtitle="Side-by-side performance analysis" />

            <div className="p-6 space-y-6">
                {/* Selector */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <GitCompareArrows className="h-5 w-5" />
                            Select Chamas to Compare (max 3)
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex flex-wrap gap-3">
                            {chamaData.map((chama) => {
                                const isSelected = selected.includes(chama.id);
                                return (
                                    <button
                                        key={chama.id}
                                        onClick={() => toggleChama(chama.id)}
                                        className="flex items-center gap-2 px-4 py-2.5 rounded-lg border-2 transition-all duration-200"
                                        style={{
                                            borderColor: isSelected ? chama.color : 'var(--card-border)',
                                            background: isSelected ? `${chama.color}15` : 'transparent',
                                        }}
                                    >
                                        <div className="h-3 w-3 rounded-full" style={{ background: chama.color }} />
                                        <span className="font-medium text-sm" style={{ color: isSelected ? chama.color : 'var(--foreground)' }}>
                                            {chama.name}
                                        </span>
                                        {isSelected && <Check className="h-4 w-4" style={{ color: chama.color }} />}
                                    </button>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                {selectedChamas.length >= 2 && (
                    <>
                        {/* KPI Comparison Table */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Key Metrics Comparison</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="overflow-x-auto">
                                    <table className="w-full">
                                        <thead>
                                            <tr className="border-b" style={{ borderColor: 'var(--table-border)' }}>
                                                <th className="pb-3 text-left text-sm font-medium" style={{ color: 'var(--muted)' }}>Metric</th>
                                                {selectedChamas.map((c) => (
                                                    <th key={c.id} className="pb-3 text-right text-sm font-medium" style={{ color: c.color }}>
                                                        {c.name}
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {[
                                                { label: 'Region', icon: '📍', render: (c: ChamaData) => c.region },
                                                { label: 'Members', icon: '👥', render: (c: ChamaData) => c.members.toString() },
                                                { label: 'Total Contributions', icon: '💰', render: (c: ChamaData) => formatCurrency(c.totalContributions) },
                                                { label: 'Monthly Contribution', icon: '📅', render: (c: ChamaData) => formatCurrency(c.monthlyContribution) },
                                                { label: 'Avg per Member', icon: '👤', render: (c: ChamaData) => formatCurrency(c.avgContributionPerMember) },
                                                { label: 'Loans Issued', icon: '📄', render: (c: ChamaData) => c.loansIssued.toString() },
                                                { label: 'Default Rate', icon: '⚠️', render: (c: ChamaData) => `${c.loanDefaultRate}%` },
                                                { label: 'Growth Rate', icon: '📈', render: (c: ChamaData) => `${c.growthRate > 0 ? '+' : ''}${c.growthRate}%` },
                                                { label: 'Active Members', icon: '✅', render: (c: ChamaData) => `${c.activeMemberRate}%` },
                                            ].map((row) => (
                                                <tr key={row.label} className="border-b last:border-0" style={{ borderColor: 'var(--table-border)' }}>
                                                    <td className="py-3 text-sm" style={{ color: 'var(--foreground)' }}>
                                                        <span className="mr-2">{row.icon}</span>{row.label}
                                                    </td>
                                                    {selectedChamas.map((c) => {
                                                        const isBest = row.label === 'Default Rate'
                                                            ? c.loanDefaultRate === Math.min(...selectedChamas.map((s) => s.loanDefaultRate))
                                                            : row.label === 'Growth Rate'
                                                                ? c.growthRate === Math.max(...selectedChamas.map((s) => s.growthRate))
                                                                : row.label === 'Total Contributions'
                                                                    ? c.totalContributions === Math.max(...selectedChamas.map((s) => s.totalContributions))
                                                                    : row.label === 'Active Members'
                                                                        ? c.activeMemberRate === Math.max(...selectedChamas.map((s) => s.activeMemberRate))
                                                                        : false;
                                                        return (
                                                            <td key={c.id} className="py-3 text-right text-sm font-mono" style={{ color: 'var(--foreground)' }}>
                                                                <span className={isBest ? 'font-bold text-green-600' : ''}>
                                                                    {row.render(c)}
                                                                    {isBest && ' 🏆'}
                                                                </span>
                                                            </td>
                                                        );
                                                    })}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Charts */}
                        <div className="grid gap-6 lg:grid-cols-2">
                            {/* Radar Chart */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Performance Radar</CardTitle>
                                    <CardDescription>Normalized scores across 6 dimensions</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={350}>
                                        <RadarChart data={radarData}>
                                            <PolarGrid stroke="var(--table-border)" />
                                            <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                                            <PolarRadiusAxis tick={{ fill: 'var(--muted)', fontSize: 10 }} domain={[0, 100]} />
                                            {selectedChamas.map((c) => (
                                                <Radar
                                                    key={c.id}
                                                    name={c.name}
                                                    dataKey={c.name}
                                                    stroke={c.color}
                                                    fill={c.color}
                                                    fillOpacity={0.15}
                                                    strokeWidth={2}
                                                />
                                            ))}
                                            <Legend />
                                            <Tooltip
                                                contentStyle={{
                                                    backgroundColor: 'var(--card-bg)',
                                                    border: '1px solid var(--card-border)',
                                                    borderRadius: '8px',
                                                    color: 'var(--foreground)',
                                                }}
                                            />
                                        </RadarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>

                            {/* Monthly Bar Chart */}
                            <Card>
                                <CardHeader>
                                    <CardTitle>Monthly Contributions</CardTitle>
                                    <CardDescription>Side-by-side monthly performance</CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={350}>
                                        <BarChart data={monthlyPerformance}>
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
                                            {selectedChamas.map((c) => {
                                                const key = c.name.split(' ')[0];
                                                return <Bar key={c.id} dataKey={key} name={c.name} fill={c.color} radius={[4, 4, 0, 0]} />;
                                            })}
                                        </BarChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Insights */}
                        <Card>
                            <CardHeader>
                                <CardTitle>Comparison Insights</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                                    {selectedChamas.map((c) => {
                                        const risk = c.loanDefaultRate > 5 ? 'high' : c.loanDefaultRate > 3 ? 'medium' : 'low';
                                        return (
                                            <div key={c.id} className="p-4 rounded-lg border" style={{ borderColor: c.color, borderLeftWidth: '4px' }}>
                                                <h4 className="font-semibold mb-3" style={{ color: c.color }}>{c.name}</h4>
                                                <div className="space-y-2 text-sm">
                                                    <div className="flex items-center gap-2">
                                                        {c.growthRate > 0 ? (
                                                            <TrendingUp className="h-4 w-4 text-green-500" />
                                                        ) : (
                                                            <TrendingDown className="h-4 w-4 text-red-500" />
                                                        )}
                                                        <span style={{ color: 'var(--foreground)' }}>
                                                            {c.growthRate > 0 ? 'Growing' : 'Declining'} at {Math.abs(c.growthRate)}%
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        {risk === 'low' ? (
                                                            <ShieldCheck className="h-4 w-4 text-green-500" />
                                                        ) : (
                                                            <AlertTriangle className={`h-4 w-4 ${risk === 'high' ? 'text-red-500' : 'text-yellow-500'}`} />
                                                        )}
                                                        <span style={{ color: 'var(--foreground)' }}>
                                                            {risk === 'low' ? 'Low' : risk === 'medium' ? 'Medium' : 'High'} loan risk ({c.loanDefaultRate}%)
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <Users className="h-4 w-4" style={{ color: 'var(--muted)' }} />
                                                        <span style={{ color: 'var(--foreground)' }}>{c.activeMemberRate}% members active</span>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <DollarSign className="h-4 w-4" style={{ color: 'var(--muted)' }} />
                                                        <span style={{ color: 'var(--foreground)' }}>{formatCurrency(c.avgContributionPerMember)}/member avg</span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </CardContent>
                        </Card>
                    </>
                )}

                {selectedChamas.length < 2 && (
                    <div className="text-center py-20" style={{ color: 'var(--muted)' }}>
                        <GitCompareArrows className="h-16 w-16 mx-auto mb-4 opacity-30" />
                        <p className="text-lg font-medium">Select at least 2 chamas to compare</p>
                        <p className="text-sm">Choose from the list above to see side-by-side analytics</p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
