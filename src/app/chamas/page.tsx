'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/input';
import { formatDate, formatCurrency, getStatusColor } from '@/lib/utils';
import {
  Building2,
  Search,
  Plus,
  MoreVertical,
  MapPin,
  Users,
  DollarSign,
  Edit,
  Trash2,
  Eye,
} from 'lucide-react';
import Link from 'next/link';

// Mock data
const mockChamas = [
  {
    id: 'org_1',
    name: 'Mwanzo Group',
    code: 'MWANZO',
    region: 'Nairobi',
    status: 'ACTIVE',
    members: 50,
    total_contributions: 450000,
    created_at: '2025-01-15',
  },
  {
    id: 'org_2',
    name: 'Tujitegemee Group',
    code: 'TUJITE',
    region: 'Mombasa',
    status: 'ACTIVE',
    members: 48,
    total_contributions: 380000,
    created_at: '2025-02-01',
  },
  {
    id: 'org_3',
    name: 'Chama Cha Maendeleo',
    code: 'MAENDE',
    region: 'Kisumu',
    status: 'ACTIVE',
    members: 50,
    total_contributions: 320000,
    created_at: '2025-03-10',
  },
  {
    id: 'org_4',
    name: 'Umoja Kazi Group',
    code: 'UMOJA',
    region: 'Nakuru',
    status: 'SUSPENDED',
    members: 45,
    total_contributions: 180000,
    created_at: '2025-04-20',
  },
  {
    id: 'org_5',
    name: 'Faraja Savings Circle',
    code: 'FARAJA',
    region: 'Eldoret',
    status: 'ACTIVE',
    members: 50,
    total_contributions: 420000,
    created_at: '2025-05-05',
  },
];

export default function ChamasPage() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredChamas = mockChamas.filter((chama) => {
    const matchesSearch =
      chama.name.toLowerCase().includes(search.toLowerCase()) ||
      chama.code.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      statusFilter === 'all' || chama.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <DashboardLayout>
      <Header title="Chamas" subtitle="Manage all chamas on the platform" />

      <div className="p-6 space-y-6">
        {/* Actions Bar */}
        <div className="flex flex-col sm:flex-row gap-4 justify-between">
          <div className="flex gap-2 flex-1">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search chamas..."
                className="pl-9"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="ACTIVE">Active</option>
              <option value="SUSPENDED">Suspended</option>
              <option value="PENDING">Pending</option>
            </Select>
          </div>
          <Link href="/chamas/onboard">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Onboard Chama
            </Button>
          </Link>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Total Chamas</p>
              <p className="text-2xl font-bold">{mockChamas.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Active</p>
              <p className="text-2xl font-bold text-green-600">
                {mockChamas.filter((c) => c.status === 'ACTIVE').length}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Total Members</p>
              <p className="text-2xl font-bold">
                {mockChamas.reduce((sum, c) => sum + c.members, 0)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-gray-500">Total Contributions</p>
              <p className="text-2xl font-bold">
                {formatCurrency(
                  mockChamas.reduce((sum, c) => sum + c.total_contributions, 0)
                )}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Chamas Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Chamas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Name
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Region
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Members
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Contributions
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Status
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">
                      Created
                    </th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-500">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredChamas.map((chama) => (
                    <tr key={chama.id} className="border-b last:border-0">
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-lg bg-primary-100 flex items-center justify-center">
                            <Building2 className="h-5 w-5 text-primary-600" />
                          </div>
                          <div>
                            <p className="font-medium">{chama.name}</p>
                            <p className="text-sm text-gray-500">{chama.code}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-center gap-1 text-gray-600">
                          <MapPin className="h-4 w-4" />
                          {chama.region}
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-center gap-1 text-gray-600">
                          <Users className="h-4 w-4" />
                          {chama.members}
                        </div>
                      </td>
                      <td className="py-4 font-medium">
                        {formatCurrency(chama.total_contributions)}
                      </td>
                      <td className="py-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                            chama.status
                          )}`}
                        >
                          {chama.status}
                        </span>
                      </td>
                      <td className="py-4 text-gray-500">
                        {formatDate(chama.created_at)}
                      </td>
                      <td className="py-4">
                        <div className="flex items-center justify-end gap-1">
                          <Link href={`/chamas/${chama.id}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
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
