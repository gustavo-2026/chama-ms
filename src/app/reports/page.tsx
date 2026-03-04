'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/input';
import { formatCurrency, formatNumber } from '@/lib/utils';
import {
    FileText,
    Download,
    BarChart3,
    PieChart,
    TrendingUp,
    Calendar,
} from 'lucide-react';

const reportTypes = [
    { id: 'contributions', name: 'Contributions Report', icon: BarChart3, description: 'Monthly and annual contribution summaries' },
    { id: 'loans', name: 'Loans Report', icon: TrendingUp, description: 'Loan disbursements, repayments, and defaults' },
    { id: 'membership', name: 'Membership Report', icon: PieChart, description: 'Member growth, retention, and demographics' },
    { id: 'financial', name: 'Financial Summary', icon: FileText, description: 'Complete financial overview across all chamas' },
];

const mockReportData = [
    { month: 'Jan', contributions: 120000, loans: 80000, members: 180 },
    { month: 'Feb', contributions: 145000, loans: 95000, members: 195 },
    { month: 'Mar', contributions: 160000, loans: 70000, members: 210 },
    { month: 'Apr', contributions: 155000, loans: 120000, members: 225 },
    { month: 'May', contributions: 180000, loans: 90000, members: 240 },
    { month: 'Jun', contributions: 195000, loans: 110000, members: 250 },
];

export default function ReportsPage() {
    const [selectedReport, setSelectedReport] = useState('contributions');
    const [period, setPeriod] = useState('6months');

    const totalContributions = mockReportData.reduce((sum, d) => sum + d.contributions, 0);
    const totalLoans = mockReportData.reduce((sum, d) => sum + d.loans, 0);
    const latestMembers = mockReportData[mockReportData.length - 1].members;

    return (
        <DashboardLayout>
            <Header title="Reports" subtitle="Generate and download platform reports" />

            <div className="p-6 space-y-6">
                {/* Controls */}
                <div className="flex flex-col sm:flex-row gap-4 justify-between">
                    <div className="flex gap-2">
                        <Select value={period} onChange={(e) => setPeriod(e.target.value)}>
                            <option value="1month">Last Month</option>
                            <option value="3months">Last 3 Months</option>
                            <option value="6months">Last 6 Months</option>
                            <option value="1year">Last Year</option>
                        </Select>
                    </div>
                    <Button variant="outline">
                        <Download className="mr-2 h-4 w-4" />
                        Export All
                    </Button>
                </div>

                {/* Summary Cards */}
                <div className="grid gap-4 md:grid-cols-3">
                    <Card>
                        <CardContent className="p-4">
                            <p className="text-sm text-gray-500">Total Contributions</p>
                            <p className="text-2xl font-bold text-green-600">{formatCurrency(totalContributions)}</p>
                            <p className="text-xs text-gray-400 mt-1">Across all chamas</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <p className="text-sm text-gray-500">Total Loans Disbursed</p>
                            <p className="text-2xl font-bold text-blue-600">{formatCurrency(totalLoans)}</p>
                            <p className="text-xs text-gray-400 mt-1">Active and completed</p>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <p className="text-sm text-gray-500">Active Members</p>
                            <p className="text-2xl font-bold">{formatNumber(latestMembers)}</p>
                            <p className="text-xs text-gray-400 mt-1">Current period</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Report Types */}
                <div className="grid gap-4 md:grid-cols-2">
                    {reportTypes.map((report) => (
                        <Card
                            key={report.id}
                            className={`cursor-pointer transition-all ${selectedReport === report.id
                                    ? 'ring-2 ring-primary-600 border-primary-600'
                                    : 'hover:border-gray-300'
                                }`}
                            onClick={() => setSelectedReport(report.id)}
                        >
                            <CardContent className="p-6">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-3 rounded-lg bg-primary-100">
                                            <report.icon className="h-6 w-6 text-primary-600" />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-gray-900">{report.name}</h3>
                                            <p className="text-sm text-gray-500 mt-1">{report.description}</p>
                                        </div>
                                    </div>
                                    <Button variant="ghost" size="sm">
                                        <Download className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                {/* Data Table */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle>Monthly Breakdown</CardTitle>
                            <CardDescription>Detailed monthly data for the selected period</CardDescription>
                        </div>
                        <Button variant="outline" size="sm">
                            <Download className="mr-2 h-4 w-4" />
                            Export CSV
                        </Button>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b">
                                        <th className="pb-3 text-left text-sm font-medium text-gray-500">Month</th>
                                        <th className="pb-3 text-left text-sm font-medium text-gray-500">Contributions</th>
                                        <th className="pb-3 text-left text-sm font-medium text-gray-500">Loans</th>
                                        <th className="pb-3 text-left text-sm font-medium text-gray-500">Members</th>
                                        <th className="pb-3 text-left text-sm font-medium text-gray-500">Net</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {mockReportData.map((row) => (
                                        <tr key={row.month} className="border-b last:border-0">
                                            <td className="py-3 font-medium">{row.month}</td>
                                            <td className="py-3 text-green-600">{formatCurrency(row.contributions)}</td>
                                            <td className="py-3 text-blue-600">{formatCurrency(row.loans)}</td>
                                            <td className="py-3">{row.members}</td>
                                            <td className="py-3 font-medium">{formatCurrency(row.contributions - row.loans)}</td>
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
