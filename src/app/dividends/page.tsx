'use client';

import { useState, useMemo } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { formatCurrency } from '@/lib/utils';
import {
    PieChart, Pie, Cell,
    BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
    Coins,
    Users,
    DollarSign,
    Download,
    Calculator,
    Percent,
} from 'lucide-react';

interface Member {
    id: string;
    name: string;
    totalContributions: number;
    months: number;
    role: string;
}

const chamaMembers: Record<string, Member[]> = {
    'Mwanzo Group': [
        { id: '1', name: 'Peter Wekesa', totalContributions: 120000, months: 12, role: 'Chair' },
        { id: '2', name: 'Grace Ochieng', totalContributions: 105000, months: 12, role: 'Secretary' },
        { id: '3', name: 'John Kimani', totalContributions: 98000, months: 11, role: 'Treasurer' },
        { id: '4', name: 'Mary Wanjiku', totalContributions: 88000, months: 10, role: 'Member' },
        { id: '5', name: 'David Otieno', totalContributions: 75000, months: 9, role: 'Member' },
        { id: '6', name: 'Sarah Akinyi', totalContributions: 72000, months: 12, role: 'Member' },
        { id: '7', name: 'James Mwangi', totalContributions: 65000, months: 8, role: 'Member' },
        { id: '8', name: 'Faith Njeri', totalContributions: 60000, months: 12, role: 'Member' },
    ],
    'Tujitegemee': [
        { id: '9', name: 'Hassan Ali', totalContributions: 95000, months: 12, role: 'Chair' },
        { id: '10', name: 'Amina Bakari', totalContributions: 88000, months: 11, role: 'Secretary' },
        { id: '11', name: 'Omar Said', totalContributions: 82000, months: 12, role: 'Treasurer' },
        { id: '12', name: 'Fatma Hussein', totalContributions: 70000, months: 10, role: 'Member' },
        { id: '13', name: 'Yusuf Mwangi', totalContributions: 65000, months: 9, role: 'Member' },
        { id: '14', name: 'Zainab Mohamed', totalContributions: 60000, months: 12, role: 'Member' },
    ],
    'Faraja Savings': [
        { id: '15', name: 'Agnes Chebet', totalContributions: 110000, months: 12, role: 'Chair' },
        { id: '16', name: 'Kipchoge Korir', totalContributions: 95000, months: 11, role: 'Secretary' },
        { id: '17', name: 'Beatrice Jebet', totalContributions: 90000, months: 12, role: 'Treasurer' },
        { id: '18', name: 'Moses Kiprono', totalContributions: 78000, months: 10, role: 'Member' },
        { id: '19', name: 'Lucy Chepkoech', totalContributions: 72000, months: 12, role: 'Member' },
    ],
};

const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#f97316', '#ec4899'];

export default function DividendsPage() {
    const [selectedChama, setSelectedChama] = useState('Mwanzo Group');
    const [totalProfit, setTotalProfit] = useState(180000);
    const [method, setMethod] = useState<'contribution' | 'equal' | 'weighted'>('contribution');
    const [bonusPercent, setBonusPercent] = useState(0);

    const members = chamaMembers[selectedChama] || [];

    const distribution = useMemo(() => {
        const totalContributions = members.reduce((sum, m) => sum + m.totalContributions, 0);
        const totalMonths = members.reduce((sum, m) => sum + m.months, 0);
        const bonusPool = totalProfit * (bonusPercent / 100);
        const distributableProfit = totalProfit - bonusPool;

        return members.map((member) => {
            let share: number;
            let sharePercent: number;

            switch (method) {
                case 'equal':
                    share = distributableProfit / members.length;
                    sharePercent = 100 / members.length;
                    break;
                case 'weighted':
                    // Weight: 70% by contribution, 30% by tenure
                    const contribWeight = totalContributions > 0 ? member.totalContributions / totalContributions : 0;
                    const tenureWeight = totalMonths > 0 ? member.months / totalMonths : 0;
                    const combinedWeight = contribWeight * 0.7 + tenureWeight * 0.3;
                    const totalWeights = members.reduce((sum, m) => {
                        const cw = totalContributions > 0 ? m.totalContributions / totalContributions : 0;
                        const tw = totalMonths > 0 ? m.months / totalMonths : 0;
                        return sum + cw * 0.7 + tw * 0.3;
                    }, 0);
                    sharePercent = (combinedWeight / totalWeights) * 100;
                    share = distributableProfit * (combinedWeight / totalWeights);
                    break;
                case 'contribution':
                default:
                    sharePercent = totalContributions > 0 ? (member.totalContributions / totalContributions) * 100 : 0;
                    share = totalContributions > 0 ? distributableProfit * (member.totalContributions / totalContributions) : 0;
                    break;
            }

            // Add bonus for leadership
            let bonus = 0;
            if (bonusPercent > 0 && (member.role === 'Chair' || member.role === 'Treasurer' || member.role === 'Secretary')) {
                const leaderCount = members.filter((m) => ['Chair', 'Treasurer', 'Secretary'].includes(m.role)).length;
                bonus = bonusPool / leaderCount;
            }

            return {
                ...member,
                share: Math.round(share),
                bonus: Math.round(bonus),
                total: Math.round(share + bonus),
                sharePercent: Math.round(sharePercent * 10) / 10,
                roi: Math.round((share / member.totalContributions) * 100 * 10) / 10,
            };
        });
    }, [members, totalProfit, method, bonusPercent]);

    const totalDistributed = distribution.reduce((sum, d) => sum + d.total, 0);
    const avgROI = distribution.length > 0 ? Math.round(distribution.reduce((sum, d) => sum + d.roi, 0) / distribution.length * 10) / 10 : 0;

    const pieData = distribution.map((d) => ({ name: d.name, value: d.total }));
    const barData = distribution.map((d) => ({ name: d.name.split(' ')[0], share: d.share, bonus: d.bonus }));

    return (
        <DashboardLayout>
            <Header title="Dividend Distribution" subtitle="Calculate profit sharing for chama members" />

            <div className="p-6 space-y-6">
                {/* Config */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Calculator className="h-5 w-5" />
                            Distribution Parameters
                        </CardTitle>
                        <CardDescription>Configure how profits are divided among members</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <Users className="h-4 w-4" /> Chama
                                </label>
                                <Select value={selectedChama} onChange={(e) => setSelectedChama(e.target.value)}>
                                    {Object.keys(chamaMembers).map((c) => <option key={c} value={c}>{c}</option>)}
                                </Select>
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <DollarSign className="h-4 w-4" /> Total Profit (KES)
                                </label>
                                <Input type="number" value={totalProfit} onChange={(e) => setTotalProfit(Number(e.target.value))} min={0} step={5000} />
                                <input type="range" min={0} max={1000000} step={5000} value={totalProfit} onChange={(e) => setTotalProfit(Number(e.target.value))} className="w-full mt-2 accent-blue-600" />
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <Coins className="h-4 w-4" /> Distribution Method
                                </label>
                                <Select value={method} onChange={(e) => setMethod(e.target.value as 'contribution' | 'equal' | 'weighted')}>
                                    <option value="contribution">By Contribution Ratio</option>
                                    <option value="equal">Equal Split</option>
                                    <option value="weighted">Weighted (70% Contrib, 30% Tenure)</option>
                                </Select>
                            </div>
                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <Percent className="h-4 w-4" /> Leadership Bonus (%)
                                </label>
                                <Input type="number" value={bonusPercent} onChange={(e) => setBonusPercent(Math.min(30, Math.max(0, Number(e.target.value))))} min={0} max={30} />
                                <p className="text-xs mt-1" style={{ color: 'var(--muted)' }}>Extra pool for Chair, Secretary, Treasurer</p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Summary Cards */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card className="bg-gradient-to-br from-blue-500 to-blue-700 text-white border-0">
                        <CardContent className="p-5">
                            <p className="text-sm text-blue-100">Total to Distribute</p>
                            <p className="text-2xl font-bold mt-1">{formatCurrency(totalProfit)}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-500 to-green-700 text-white border-0">
                        <CardContent className="p-5">
                            <p className="text-sm text-green-100">Members</p>
                            <p className="text-2xl font-bold mt-1">{members.length}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-purple-500 to-purple-700 text-white border-0">
                        <CardContent className="p-5">
                            <p className="text-sm text-purple-100">Avg per Member</p>
                            <p className="text-2xl font-bold mt-1">{formatCurrency(Math.round(totalProfit / Math.max(1, members.length)))}</p>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-orange-500 to-orange-700 text-white border-0">
                        <CardContent className="p-5">
                            <p className="text-sm text-orange-100">Avg ROI</p>
                            <p className="text-2xl font-bold mt-1">{avgROI}%</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Charts */}
                <div className="grid gap-6 lg:grid-cols-2">
                    <Card>
                        <CardHeader>
                            <CardTitle>Distribution Share</CardTitle>
                            <CardDescription>Proportional share per member</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={3} dataKey="value"
                                        label={({ name, value }) => `${name}: ${formatCurrency(value)}`}>
                                        {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                    </Pie>
                                    <Tooltip contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '8px', color: 'var(--foreground)' }}
                                        formatter={(value: number) => [formatCurrency(value), '']} />
                                </PieChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Share + Bonus Breakdown</CardTitle>
                            <CardDescription>Base share vs leadership bonus per member</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={barData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="var(--table-border)" />
                                    <XAxis dataKey="name" tick={{ fill: 'var(--muted)', fontSize: 12 }} />
                                    <YAxis tick={{ fill: 'var(--muted)', fontSize: 12 }} tickFormatter={(v) => `${v / 1000}k`} />
                                    <Tooltip contentStyle={{ backgroundColor: 'var(--card-bg)', border: '1px solid var(--card-border)', borderRadius: '8px', color: 'var(--foreground)' }}
                                        formatter={(value: number) => [formatCurrency(value), '']} />
                                    <Legend />
                                    <Bar dataKey="share" name="Base Share" fill="#3b82f6" stackId="a" radius={[0, 0, 0, 0]} />
                                    <Bar dataKey="bonus" name="Leadership Bonus" fill="#f59e0b" stackId="a" radius={[4, 4, 0, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </CardContent>
                    </Card>
                </div>

                {/* Distribution Table */}
                <Card>
                    <CardHeader>
                        <div className="flex justify-between items-center">
                            <div>
                                <CardTitle>Distribution Schedule</CardTitle>
                                <CardDescription>Detailed payout breakdown for each member</CardDescription>
                            </div>
                            <Button variant="outline" onClick={() => {
                                const csv = ['Name,Role,Contributions,Months,Share %,Share,Bonus,Total,ROI %',
                                    ...distribution.map((d) => `${d.name},${d.role},${d.totalContributions},${d.months},${d.sharePercent}%,${d.share},${d.bonus},${d.total},${d.roi}%`)
                                ].join('\n');
                                const blob = new Blob([csv], { type: 'text/csv' });
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href = url; a.download = `dividends_${selectedChama.replace(/\s+/g, '_')}.csv`;
                                a.click(); URL.revokeObjectURL(url);
                            }}>
                                <Download className="mr-2 h-4 w-4" /> Export CSV
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b" style={{ borderColor: 'var(--table-border)' }}>
                                        {['Member', 'Role', 'Contributions', 'Months', 'Share %', 'Base Share', 'Bonus', 'Total Payout', 'ROI'].map((h) => (
                                            <th key={h} className="pb-3 text-left text-sm font-medium" style={{ color: 'var(--muted)' }}>{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {distribution.map((d, i) => (
                                        <tr key={d.id} className="border-b last:border-0" style={{ borderColor: 'var(--table-border)' }}>
                                            <td className="py-3">
                                                <div className="flex items-center gap-2">
                                                    <div className="h-6 w-6 rounded-full flex items-center justify-center text-white text-xs font-bold" style={{ background: COLORS[i % COLORS.length] }}>
                                                        {d.name[0]}
                                                    </div>
                                                    <span className="font-medium text-sm" style={{ color: 'var(--foreground)' }}>{d.name}</span>
                                                </div>
                                            </td>
                                            <td className="py-3">
                                                <span className={`text-xs px-2 py-0.5 rounded-full ${d.role !== 'Member' ? 'bg-blue-100 text-blue-700' : ''}`} style={d.role === 'Member' ? { color: 'var(--muted)' } : {}}>
                                                    {d.role}
                                                </span>
                                            </td>
                                            <td className="py-3 text-sm font-mono" style={{ color: 'var(--foreground)' }}>{formatCurrency(d.totalContributions)}</td>
                                            <td className="py-3 text-sm" style={{ color: 'var(--foreground)' }}>{d.months}</td>
                                            <td className="py-3 text-sm font-mono" style={{ color: 'var(--foreground)' }}>{d.sharePercent}%</td>
                                            <td className="py-3 text-sm font-mono text-blue-600">{formatCurrency(d.share)}</td>
                                            <td className="py-3 text-sm font-mono" style={{ color: d.bonus > 0 ? '#f59e0b' : 'var(--muted)' }}>{d.bonus > 0 ? formatCurrency(d.bonus) : '—'}</td>
                                            <td className="py-3 text-sm font-mono font-bold text-green-600">{formatCurrency(d.total)}</td>
                                            <td className="py-3 text-sm font-mono" style={{ color: 'var(--foreground)' }}>{d.roi}%</td>
                                        </tr>
                                    ))}
                                    {/* Totals */}
                                    <tr className="border-t-2 font-bold" style={{ borderColor: 'var(--foreground)' }}>
                                        <td className="py-3 text-sm" style={{ color: 'var(--foreground)' }} colSpan={5}>Total</td>
                                        <td className="py-3 text-sm font-mono text-blue-600">{formatCurrency(distribution.reduce((s, d) => s + d.share, 0))}</td>
                                        <td className="py-3 text-sm font-mono text-yellow-600">{formatCurrency(distribution.reduce((s, d) => s + d.bonus, 0))}</td>
                                        <td className="py-3 text-sm font-mono text-green-600">{formatCurrency(totalDistributed)}</td>
                                        <td className="py-3 text-sm font-mono" style={{ color: 'var(--foreground)' }}>{avgROI}%</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    );
}
