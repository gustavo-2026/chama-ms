'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/input';
import { formatCurrency } from '@/lib/utils';
import {
    Target,
    Plus,
    TrendingUp,
    CheckCircle2,
    Clock,
    Flame,
    Trophy,
    Calendar,
    Pencil,
    X,
} from 'lucide-react';

interface SavingsGoal {
    id: string;
    chama: string;
    title: string;
    target: number;
    current: number;
    deadline: string;
    category: string;
    monthlyTarget: number;
    color: string;
}

const initialGoals: SavingsGoal[] = [
    {
        id: '1', chama: 'Mwanzo Group', title: 'Land Purchase Fund',
        target: 2000000, current: 850000, deadline: '2026-12-31',
        category: 'Investment', monthlyTarget: 120000, color: '#3b82f6',
    },
    {
        id: '2', chama: 'Mwanzo Group', title: 'Emergency Reserve',
        target: 500000, current: 425000, deadline: '2026-06-30',
        category: 'Emergency', monthlyTarget: 25000, color: '#ef4444',
    },
    {
        id: '3', chama: 'Tujitegemee', title: 'Equipment Purchase',
        target: 800000, current: 560000, deadline: '2026-09-30',
        category: 'Business', monthlyTarget: 40000, color: '#22c55e',
    },
    {
        id: '4', chama: 'Faraja Savings', title: 'Education Scholarship Fund',
        target: 1200000, current: 1080000, deadline: '2026-04-30',
        category: 'Education', monthlyTarget: 60000, color: '#8b5cf6',
    },
    {
        id: '5', chama: 'Chama Maendeleo', title: 'Office Renovation',
        target: 600000, current: 120000, deadline: '2027-03-31',
        category: 'Infrastructure', monthlyTarget: 40000, color: '#f59e0b',
    },
    {
        id: '6', chama: 'Tujitegemee', title: 'Year-End Dividends Pool',
        target: 1000000, current: 720000, deadline: '2026-12-31',
        category: 'Dividends', monthlyTarget: 30000, color: '#06b6d4',
    },
];

const categoryIcons: Record<string, string> = {
    Investment: '🏠', Emergency: '🚨', Business: '💼',
    Education: '🎓', Infrastructure: '🏗️', Dividends: '💎',
};

function ProgressRing({ percent, color, size = 80 }: { percent: number; color: string; size?: number }) {
    const strokeWidth = 6;
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (Math.min(percent, 100) / 100) * circumference;

    return (
        <svg width={size} height={size} className="transform -rotate-90">
            <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--muted-bg)" strokeWidth={strokeWidth} />
            <circle
                cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={strokeWidth}
                strokeDasharray={circumference} strokeDashoffset={offset}
                strokeLinecap="round" className="transition-all duration-1000 ease-out"
            />
        </svg>
    );
}

export default function GoalsPage() {
    const [goals, setGoals] = useState(initialGoals);
    const [filterChama, setFilterChama] = useState('all');
    const [showForm, setShowForm] = useState(false);
    const [newGoal, setNewGoal] = useState({ title: '', target: '', chama: 'Mwanzo Group', category: 'Investment', deadline: '' });

    const chamas = [...new Set(goals.map((g) => g.chama))];
    const filtered = filterChama === 'all' ? goals : goals.filter((g) => g.chama === filterChama);

    const totalTarget = filtered.reduce((sum, g) => sum + g.target, 0);
    const totalCurrent = filtered.reduce((sum, g) => sum + g.current, 0);
    const overallPercent = totalTarget > 0 ? Math.round((totalCurrent / totalTarget) * 100) : 0;
    const completedGoals = filtered.filter((g) => g.current >= g.target).length;
    const atRisk = filtered.filter((g) => {
        const daysLeft = Math.max(0, (new Date(g.deadline).getTime() - Date.now()) / 86400000);
        const remaining = g.target - g.current;
        const monthsLeft = daysLeft / 30;
        return monthsLeft > 0 && remaining / monthsLeft > g.monthlyTarget * 1.5;
    }).length;

    const addGoal = () => {
        if (!newGoal.title || !newGoal.target || !newGoal.deadline) return;
        const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];
        setGoals((prev) => [...prev, {
            id: Date.now().toString(), chama: newGoal.chama, title: newGoal.title,
            target: Number(newGoal.target), current: 0, deadline: newGoal.deadline,
            category: newGoal.category, monthlyTarget: Math.round(Number(newGoal.target) / 12),
            color: colors[prev.length % colors.length],
        }]);
        setNewGoal({ title: '', target: '', chama: 'Mwanzo Group', category: 'Investment', deadline: '' });
        setShowForm(false);
    };

    return (
        <DashboardLayout>
            <Header title="Savings Goals" subtitle="Track financial targets across all chamas" />

            <div className="p-6 space-y-6">
                {/* Summary Cards */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-100"><Target className="h-5 w-5 text-blue-600" /></div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Active Goals</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{filtered.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-green-100"><TrendingUp className="h-5 w-5 text-green-600" /></div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Overall Progress</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{overallPercent}%</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-purple-100"><Trophy className="h-5 w-5 text-purple-600" /></div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Completed</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{completedGoals}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-red-100"><Flame className="h-5 w-5 text-red-600" /></div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>At Risk</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{atRisk}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Controls */}
                <div className="flex flex-col sm:flex-row gap-4 justify-between">
                    <Select value={filterChama} onChange={(e) => setFilterChama(e.target.value)}>
                        <option value="all">All Chamas</option>
                        {chamas.map((c) => <option key={c} value={c}>{c}</option>)}
                    </Select>
                    <Button onClick={() => setShowForm(!showForm)}>
                        {showForm ? <X className="mr-2 h-4 w-4" /> : <Plus className="mr-2 h-4 w-4" />}
                        {showForm ? 'Cancel' : 'New Goal'}
                    </Button>
                </div>

                {/* New Goal Form */}
                {showForm && (
                    <Card>
                        <CardHeader><CardTitle className="flex items-center gap-2"><Pencil className="h-4 w-4" /> Create New Goal</CardTitle></CardHeader>
                        <CardContent>
                            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                                <div>
                                    <label className="text-xs font-medium mb-1 block" style={{ color: 'var(--muted)' }}>Goal Title</label>
                                    <Input placeholder="e.g. Vehicle Fund" value={newGoal.title} onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })} />
                                </div>
                                <div>
                                    <label className="text-xs font-medium mb-1 block" style={{ color: 'var(--muted)' }}>Target (KES)</label>
                                    <Input type="number" placeholder="1000000" value={newGoal.target} onChange={(e) => setNewGoal({ ...newGoal, target: e.target.value })} />
                                </div>
                                <div>
                                    <label className="text-xs font-medium mb-1 block" style={{ color: 'var(--muted)' }}>Chama</label>
                                    <Select value={newGoal.chama} onChange={(e) => setNewGoal({ ...newGoal, chama: e.target.value })}>
                                        {chamas.map((c) => <option key={c} value={c}>{c}</option>)}
                                    </Select>
                                </div>
                                <div>
                                    <label className="text-xs font-medium mb-1 block" style={{ color: 'var(--muted)' }}>Category</label>
                                    <Select value={newGoal.category} onChange={(e) => setNewGoal({ ...newGoal, category: e.target.value })}>
                                        {Object.keys(categoryIcons).map((c) => <option key={c} value={c}>{c}</option>)}
                                    </Select>
                                </div>
                                <div>
                                    <label className="text-xs font-medium mb-1 block" style={{ color: 'var(--muted)' }}>Deadline</label>
                                    <Input type="date" value={newGoal.deadline} onChange={(e) => setNewGoal({ ...newGoal, deadline: e.target.value })} />
                                </div>
                            </div>
                            <Button className="mt-4" onClick={addGoal}>Create Goal</Button>
                        </CardContent>
                    </Card>
                )}

                {/* Goals Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {filtered.map((goal) => {
                        const percent = Math.round((goal.current / goal.target) * 100);
                        const remaining = goal.target - goal.current;
                        const daysLeft = Math.max(0, Math.round((new Date(goal.deadline).getTime() - Date.now()) / 86400000));
                        const isComplete = percent >= 100;

                        return (
                            <Card key={goal.id} className="transition-all duration-200 hover:shadow-md overflow-hidden">
                                {/* Color strip at top */}
                                <div className="h-1" style={{ background: goal.color }} />
                                <CardContent className="p-5">
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">{categoryIcons[goal.category] || '🎯'}</span>
                                            <div>
                                                <h3 className="font-semibold" style={{ color: 'var(--foreground)' }}>{goal.title}</h3>
                                                <p className="text-xs" style={{ color: 'var(--muted)' }}>{goal.chama}</p>
                                            </div>
                                        </div>
                                        <div className="relative flex items-center justify-center">
                                            <ProgressRing percent={percent} color={goal.color} size={60} />
                                            <span className="absolute text-xs font-bold" style={{ color: 'var(--foreground)' }}>{percent}%</span>
                                        </div>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="mb-3">
                                        <div className="flex justify-between text-xs mb-1">
                                            <span style={{ color: 'var(--muted)' }}>{formatCurrency(goal.current)}</span>
                                            <span className="font-medium" style={{ color: 'var(--foreground)' }}>{formatCurrency(goal.target)}</span>
                                        </div>
                                        <div className="h-2.5 rounded-full overflow-hidden" style={{ background: 'var(--muted-bg)' }}>
                                            <div
                                                className="h-full rounded-full transition-all duration-1000 ease-out"
                                                style={{ width: `${Math.min(100, percent)}%`, background: `linear-gradient(90deg, ${goal.color}, ${goal.color}dd)` }}
                                            />
                                        </div>
                                    </div>

                                    {/* Details */}
                                    <div className="grid grid-cols-2 gap-3 text-xs">
                                        <div className="flex items-center gap-1.5" style={{ color: 'var(--muted)' }}>
                                            <Calendar className="h-3.5 w-3.5" />
                                            <span>{daysLeft} days left</span>
                                        </div>
                                        <div className="flex items-center gap-1.5" style={{ color: 'var(--muted)' }}>
                                            <Clock className="h-3.5 w-3.5" />
                                            <span>{formatCurrency(goal.monthlyTarget)}/mo</span>
                                        </div>
                                    </div>

                                    {/* Status */}
                                    <div className="mt-3 pt-3 border-t" style={{ borderColor: 'var(--table-border)' }}>
                                        {isComplete ? (
                                            <div className="flex items-center gap-2 text-green-600 text-sm font-medium">
                                                <CheckCircle2 className="h-4 w-4" />
                                                Goal Achieved! 🎉
                                            </div>
                                        ) : remaining > 0 ? (
                                            <p className="text-xs" style={{ color: 'var(--muted)' }}>
                                                <span className="font-medium" style={{ color: 'var(--foreground)' }}>{formatCurrency(remaining)}</span> remaining to reach target
                                            </p>
                                        ) : null}
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </DashboardLayout>
    );
}
