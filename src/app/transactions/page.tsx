'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/input';
import { formatDate, formatCurrency, getStatusColor } from '@/lib/utils';
import { Search, Download, Filter, CreditCard, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const mockTransactions = [
  { id: '1', type: 'CONTRIBUTION', amount: 5000, member: 'Peter Wekesa', chama: 'Mwanzo Group', status: 'COMPLETED', date: '2026-03-01' },
  { id: '2', type: 'LOAN_DISBURSEMENT', amount: 50000, member: 'Grace Ochieng', chama: 'Mwanzo Group', status: 'COMPLETED', date: '2026-02-28' },
  { id: '3', type: 'LOAN_REPAYMENT', amount: 10000, member: 'David Otieno', chama: 'Mwanzo Group', status: 'COMPLETED', date: '2026-02-25' },
  { id: '4', type: 'CONTRIBUTION', amount: 3000, member: 'Mary Wanjiku', chama: 'Tujitegemee', status: 'PENDING', date: '2026-03-02' },
  { id: '5', type: 'EXPENSE', amount: 15000, member: 'John Kimani', chama: 'Chama Maendeleo', status: 'COMPLETED', date: '2026-02-20' },
];

export default function TransactionsPage() {
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filtered = mockTransactions.filter((t) => {
    const matches = t.member.toLowerCase().includes(search.toLowerCase()) || t.chama.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'all' || t.type === typeFilter;
    const matchesStatus = statusFilter === 'all' || t.status === statusFilter;
    return matches && matchesType && matchesStatus;
  });

  const totalAmount = filtered.reduce((sum, t) => sum + t.amount, 0);

  return (
    <DashboardLayout>
      <Header title="Transactions" subtitle="Monitor all platform transactions" />

      <div className="p-6 space-y-6">
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input placeholder="Search transactions..." className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            <option value="all">All Types</option>
            <option value="CONTRIBUTION">Contribution</option>
            <option value="LOAN_DISBURSEMENT">Loan Disbursement</option>
            <option value="LOAN_REPAYMENT">Loan Repayment</option>
            <option value="EXPENSE">Expense</option>
          </Select>
          <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All Status</option>
            <option value="COMPLETED">Completed</option>
            <option value="PENDING">Pending</option>
            <option value="FAILED">Failed</option>
          </Select>
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" /> Export
          </Button>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Total Transactions</p><p className="text-2xl font-bold">{filtered.length}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Total Amount</p><p className="text-2xl font-bold">{formatCurrency(totalAmount)}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Completed</p><p className="text-2xl font-bold text-green-600">{filtered.filter(t => t.status === 'COMPLETED').length}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Pending</p><p className="text-2xl font-bold text-yellow-600">{filtered.filter(t => t.status === 'PENDING').length}</p></CardContent></Card>
        </div>

        {/* Table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>All Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Type</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Member</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Chama</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Amount</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Status</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((t) => (
                    <tr key={t.id} className="border-b last:border-0">
                      <td className="py-4">
                        <div className="flex items-center gap-2">
                          {t.type === 'CONTRIBUTION' || t.type === 'LOAN_REPAYMENT' ? (
                            <ArrowDownRight className="h-4 w-4 text-green-500" />
                          ) : (
                            <ArrowUpRight className="h-4 w-4 text-blue-500" />
                          )}
                          <span className="text-sm">{t.type.replace('_', ' ')}</span>
                        </div>
                      </td>
                      <td className="py-4 font-medium">{t.member}</td>
                      <td className="py-4 text-gray-600">{t.chama}</td>
                      <td className="py-4 font-medium">{formatCurrency(t.amount)}</td>
                      <td className="py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(t.status)}`}>
                          {t.status}
                        </span>
                      </td>
                      <td className="py-4 text-gray-500">{formatDate(t.date)}</td>
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
