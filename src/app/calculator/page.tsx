'use client';

import { useState, useMemo } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { formatCurrency } from '@/lib/utils';
import {
    AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import { Calculator, DollarSign, Percent, CalendarDays, TrendingUp } from 'lucide-react';

export default function CalculatorPage() {
    const [principal, setPrincipal] = useState(50000);
    const [rate, setRate] = useState(12);
    const [months, setMonths] = useState(12);

    const calculation = useMemo(() => {
        const monthlyRate = rate / 100 / 12;
        let monthlyPayment: number;

        if (monthlyRate === 0) {
            monthlyPayment = principal / months;
        } else {
            monthlyPayment = principal * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
        }

        const totalPayment = monthlyPayment * months;
        const totalInterest = totalPayment - principal;

        // Amortization schedule
        let balance = principal;
        const schedule = [];
        let cumulativePrincipal = 0;
        let cumulativeInterest = 0;

        for (let i = 1; i <= months; i++) {
            const interestPayment = balance * monthlyRate;
            const principalPayment = monthlyPayment - interestPayment;
            balance -= principalPayment;
            cumulativePrincipal += principalPayment;
            cumulativeInterest += interestPayment;

            schedule.push({
                month: i,
                payment: Math.round(monthlyPayment),
                principal: Math.round(principalPayment),
                interest: Math.round(interestPayment),
                balance: Math.max(0, Math.round(balance)),
                cumulativePrincipal: Math.round(cumulativePrincipal),
                cumulativeInterest: Math.round(cumulativeInterest),
            });
        }

        return {
            monthlyPayment: Math.round(monthlyPayment),
            totalPayment: Math.round(totalPayment),
            totalInterest: Math.round(totalInterest),
            schedule,
        };
    }, [principal, rate, months]);

    const chartData = calculation.schedule.map((s) => ({
        month: `M${s.month}`,
        Principal: s.cumulativePrincipal,
        Interest: s.cumulativeInterest,
    }));

    return (
        <DashboardLayout>
            <Header title="Loan Calculator" subtitle="Plan and visualize loan repayments" />

            <div className="p-6 space-y-6">
                <div className="grid gap-6 lg:grid-cols-3">
                    {/* Inputs */}
                    <Card className="lg:col-span-1">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Calculator className="h-5 w-5" />
                                Loan Parameters
                            </CardTitle>
                            <CardDescription>Adjust values to calculate repayment</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <DollarSign className="h-4 w-4" />
                                    Loan Amount (KES)
                                </label>
                                <Input
                                    type="number"
                                    value={principal}
                                    onChange={(e) => setPrincipal(Number(e.target.value))}
                                    min={1000}
                                    step={1000}
                                />
                                <input
                                    type="range"
                                    min={1000}
                                    max={500000}
                                    step={1000}
                                    value={principal}
                                    onChange={(e) => setPrincipal(Number(e.target.value))}
                                    className="w-full mt-2 accent-blue-600"
                                />
                                <div className="flex justify-between text-xs mt-1" style={{ color: 'var(--muted)' }}>
                                    <span>KES 1,000</span>
                                    <span>KES 500,000</span>
                                </div>
                            </div>

                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <Percent className="h-4 w-4" />
                                    Annual Interest Rate (%)
                                </label>
                                <Input
                                    type="number"
                                    value={rate}
                                    onChange={(e) => setRate(Number(e.target.value))}
                                    min={0}
                                    max={50}
                                    step={0.5}
                                />
                                <input
                                    type="range"
                                    min={0}
                                    max={50}
                                    step={0.5}
                                    value={rate}
                                    onChange={(e) => setRate(Number(e.target.value))}
                                    className="w-full mt-2 accent-blue-600"
                                />
                                <div className="flex justify-between text-xs mt-1" style={{ color: 'var(--muted)' }}>
                                    <span>0%</span>
                                    <span>50%</span>
                                </div>
                            </div>

                            <div>
                                <label className="flex items-center gap-2 text-sm font-medium mb-2" style={{ color: 'var(--muted)' }}>
                                    <CalendarDays className="h-4 w-4" />
                                    Loan Term (Months)
                                </label>
                                <Input
                                    type="number"
                                    value={months}
                                    onChange={(e) => setMonths(Math.max(1, Number(e.target.value)))}
                                    min={1}
                                    max={60}
                                />
                                <input
                                    type="range"
                                    min={1}
                                    max={60}
                                    value={months}
                                    onChange={(e) => setMonths(Number(e.target.value))}
                                    className="w-full mt-2 accent-blue-600"
                                />
                                <div className="flex justify-between text-xs mt-1" style={{ color: 'var(--muted)' }}>
                                    <span>1 month</span>
                                    <span>60 months</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Results */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Summary */}
                        <div className="grid gap-4 md:grid-cols-3">
                            <Card className="bg-gradient-to-br from-blue-500 to-blue-700 text-white border-0">
                                <CardContent className="p-5">
                                    <p className="text-sm text-blue-100">Monthly Payment</p>
                                    <p className="text-3xl font-bold mt-1">{formatCurrency(calculation.monthlyPayment)}</p>
                                </CardContent>
                            </Card>
                            <Card className="bg-gradient-to-br from-green-500 to-green-700 text-white border-0">
                                <CardContent className="p-5">
                                    <p className="text-sm text-green-100">Total Repayment</p>
                                    <p className="text-3xl font-bold mt-1">{formatCurrency(calculation.totalPayment)}</p>
                                </CardContent>
                            </Card>
                            <Card className="bg-gradient-to-br from-purple-500 to-purple-700 text-white border-0">
                                <CardContent className="p-5">
                                    <p className="text-sm text-purple-100">Total Interest</p>
                                    <p className="text-3xl font-bold mt-1">{formatCurrency(calculation.totalInterest)}</p>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Chart */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <TrendingUp className="h-5 w-5" />
                                    Cumulative Payment Breakdown
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <ResponsiveContainer width="100%" height={250}>
                                    <AreaChart data={chartData}>
                                        <defs>
                                            <linearGradient id="colorPrincipal" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                            <linearGradient id="colorInterest" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="var(--table-border)" />
                                        <XAxis dataKey="month" tick={{ fill: 'var(--muted)', fontSize: 11 }} interval={Math.max(0, Math.floor(months / 10) - 1)} />
                                        <YAxis tick={{ fill: 'var(--muted)', fontSize: 11 }} tickFormatter={(v) => `${v / 1000}k`} />
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
                                        <Area type="monotone" dataKey="Principal" stroke="#3b82f6" fill="url(#colorPrincipal)" strokeWidth={2} />
                                        <Area type="monotone" dataKey="Interest" stroke="#ef4444" fill="url(#colorInterest)" strokeWidth={2} />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </CardContent>
                        </Card>
                    </div>
                </div>

                {/* Amortization Schedule */}
                <Card>
                    <CardHeader>
                        <CardTitle>Amortization Schedule</CardTitle>
                        <CardDescription>Month-by-month breakdown of your loan repayment</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto max-h-96">
                            <table className="w-full">
                                <thead className="sticky top-0" style={{ background: 'var(--card-bg)' }}>
                                    <tr className="border-b">
                                        <th className="pb-3 text-left text-sm font-medium" style={{ color: 'var(--muted)' }}>Month</th>
                                        <th className="pb-3 text-right text-sm font-medium" style={{ color: 'var(--muted)' }}>Payment</th>
                                        <th className="pb-3 text-right text-sm font-medium" style={{ color: 'var(--muted)' }}>Principal</th>
                                        <th className="pb-3 text-right text-sm font-medium" style={{ color: 'var(--muted)' }}>Interest</th>
                                        <th className="pb-3 text-right text-sm font-medium" style={{ color: 'var(--muted)' }}>Balance</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {calculation.schedule.map((row) => (
                                        <tr key={row.month} className="border-b last:border-0">
                                            <td className="py-2.5 font-medium" style={{ color: 'var(--foreground)' }}>{row.month}</td>
                                            <td className="py-2.5 text-right font-mono text-sm" style={{ color: 'var(--foreground)' }}>{formatCurrency(row.payment)}</td>
                                            <td className="py-2.5 text-right font-mono text-sm text-blue-600">{formatCurrency(row.principal)}</td>
                                            <td className="py-2.5 text-right font-mono text-sm text-red-500">{formatCurrency(row.interest)}</td>
                                            <td className="py-2.5 text-right font-mono text-sm font-medium" style={{ color: 'var(--foreground)' }}>{formatCurrency(row.balance)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    );
}
