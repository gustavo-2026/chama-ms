'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/input';
import { formatDate, getRoleColor, getStatusColor } from '@/lib/utils';
import { Search, Filter, User, Mail, Phone, Building2 } from 'lucide-react';

// Mock data
const mockMembers = [
  { id: '1', name: 'Peter Wekesa', email: 'peter@chama.co.ke', phone: '254712345678', organization: 'Mwanzo Group', role: 'CHAIR', status: 'ACTIVE' },
  { id: '2', name: 'Grace Ochieng', email: 'grace@chama.co.ke', phone: '254723456789', organization: 'Mwanzo Group', role: 'SECRETARY', status: 'ACTIVE' },
  { id: '3', name: 'David Otieno', email: 'david@chama.co.ke', phone: '254734567890', organization: 'Mwanzo Group', role: 'TREASURER', status: 'ACTIVE' },
  { id: '4', name: 'Mary Wanjiku', email: 'mary@chama.co.ke', phone: '254745678901', organization: 'Tujitegemee', role: 'CHAIR', status: 'ACTIVE' },
  { id: '5', name: 'John Kimani', email: 'john@chama.co.ke', phone: '254756789012', organization: 'Tujitegemee', role: 'MEMBER', status: 'SUSPENDED' },
];

export default function MembersPage() {
  const [search, setSearch] = useState('');
  const [orgFilter, setOrgFilter] = useState('all');
  const [roleFilter, setRoleFilter] = useState('all');

  const filtered = mockMembers.filter((m) => {
    const matches = 
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      m.email.toLowerCase().includes(search.toLowerCase());
    const matchesOrg = orgFilter === 'all' || m.organization === orgFilter;
    const matchesRole = roleFilter === 'all' || m.role === roleFilter;
    return matches && matchesOrg && matchesRole;
  });

  return (
    <DashboardLayout>
      <Header title="Members" subtitle="Manage all members across chamas" />

      <div className="p-6 space-y-6">
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search members..."
              className="pl-9"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Select value={orgFilter} onChange={(e) => setOrgFilter(e.target.value)}>
            <option value="all">All Organizations</option>
            <option value="Mwanzo Group">Mwanzo Group</option>
            <option value="Tujitegemee">Tujitegemee</option>
          </Select>
          <Select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
            <option value="all">All Roles</option>
            <option value="CHAIR">Chair</option>
            <option value="SECRETARY">Secretary</option>
            <option value="TREASURER">Treasurer</option>
            <option value="MEMBER">Member</option>
          </Select>
        </div>

        {/* Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Total</p><p className="text-2xl font-bold">{mockMembers.length}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Active</p><p className="text-2xl font-bold text-green-600">{mockMembers.filter(m => m.status === 'ACTIVE').length}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Chairs</p><p className="text-2xl font-bold">{mockMembers.filter(m => m.role === 'CHAIR').length}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-sm text-gray-500">Suspended</p><p className="text-2xl font-bold text-red-600">{mockMembers.filter(m => m.status === 'SUSPENDED').length}</p></CardContent></Card>
        </div>

        {/* Members Table */}
        <Card>
          <CardHeader><CardTitle>All Members ({filtered.length})</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Member</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Organization</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Role</th>
                    <th className="pb-3 text-left text-sm font-medium text-gray-500">Status</th>
                    <th className="pb-3 text-right text-sm font-medium text-gray-500">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((member) => (
                    <tr key={member.id} className="border-b last:border-0">
                      <td className="py-4">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <span className="text-sm font-medium text-primary-600">{member.name.split(' ').map(n => n[0]).join('')}</span>
                          </div>
                          <div>
                            <p className="font-medium">{member.name}</p>
                            <p className="text-sm text-gray-500">{member.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-center gap-2 text-gray-600">
                          <Building2 className="h-4 w-4" />
                          {member.organization}
                        </div>
                      </td>
                      <td className="py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(member.role)}`}>
                          {member.role}
                        </span>
                      </td>
                      <td className="py-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(member.status)}`}>
                          {member.status}
                        </span>
                      </td>
                      <td className="py-4 text-right">
                        <Button variant="ghost" size="sm">View</Button>
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
