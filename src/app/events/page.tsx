'use client';

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select } from '@/components/ui/input';
import {
    Radio,
    RefreshCw,
    Loader2,
    ChevronDown,
    ChevronUp,
    Zap,
    CreditCard,
    ShoppingCart,
    Users,
    Bell,
    FileText,
} from 'lucide-react';

interface KafkaEvent {
    id: string;
    type: string;
    payload: Record<string, unknown>;
    timestamp: string;
    source: string;
}

const eventIcons: Record<string, { icon: typeof Zap; color: string; bg: string }> = {
    payment: { icon: CreditCard, color: 'text-green-600', bg: 'bg-green-100' },
    order: { icon: ShoppingCart, color: 'text-blue-600', bg: 'bg-blue-100' },
    member: { icon: Users, color: 'text-purple-600', bg: 'bg-purple-100' },
    notification: { icon: Bell, color: 'text-yellow-600', bg: 'bg-yellow-100' },
    loan: { icon: FileText, color: 'text-red-600', bg: 'bg-red-100' },
};

function getEventStyle(type: string) {
    const key = Object.keys(eventIcons).find((k) => type.toLowerCase().includes(k));
    return eventIcons[key || ''] || { icon: Zap, color: 'text-gray-600', bg: 'bg-gray-100' };
}

export default function EventsPage() {
    const [events, setEvents] = useState<KafkaEvent[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [autoRefresh, setAutoRefresh] = useState(true);

    const fetchEvents = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/events');
            const data = await res.json();
            if (Array.isArray(data)) {
                setEvents(data);
            } else if (data.events) {
                setEvents(data.events);
            } else {
                // If no events from server, use mock events to demonstrate the UI
                setEvents(getMockEvents());
            }
        } catch {
            setEvents(getMockEvents());
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchEvents();
    }, [fetchEvents]);

    useEffect(() => {
        if (!autoRefresh) return;
        const interval = setInterval(fetchEvents, 5000);
        return () => clearInterval(interval);
    }, [autoRefresh, fetchEvents]);

    const filtered = events.filter((e) => {
        if (filter === 'all') return true;
        return e.type.toLowerCase().includes(filter);
    });

    return (
        <DashboardLayout>
            <Header title="Event Stream" subtitle="Real-time Kafka event bus activity" />

            <div className="p-6 space-y-6">
                {/* Stats */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-100">
                                    <Radio className="h-5 w-5 text-blue-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Total Events</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>{events.length}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-green-100">
                                    <CreditCard className="h-5 w-5 text-green-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Payment Events</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>
                                        {events.filter((e) => e.type.toLowerCase().includes('payment')).length}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-purple-100">
                                    <ShoppingCart className="h-5 w-5 text-purple-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Order Events</p>
                                    <p className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>
                                        {events.filter((e) => e.type.toLowerCase().includes('order')).length}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${autoRefresh ? 'bg-green-100' : 'bg-gray-100'}`}>
                                    <Zap className={`h-5 w-5 ${autoRefresh ? 'text-green-600' : 'text-gray-600'}`} />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Stream Status</p>
                                    <p className={`text-lg font-bold ${autoRefresh ? 'text-green-600' : 'text-gray-600'}`}>
                                        {autoRefresh ? '● Live' : '○ Paused'}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Controls */}
                <div className="flex flex-col sm:flex-row gap-4 justify-between">
                    <div className="flex gap-2">
                        <Select value={filter} onChange={(e) => setFilter(e.target.value)}>
                            <option value="all">All Events</option>
                            <option value="payment">Payments</option>
                            <option value="order">Orders</option>
                            <option value="member">Members</option>
                            <option value="notification">Notifications</option>
                            <option value="loan">Loans</option>
                        </Select>
                        <Button onClick={fetchEvents} variant="outline" disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                            Refresh
                        </Button>
                    </div>
                    <Button
                        variant={autoRefresh ? 'default' : 'outline'}
                        onClick={() => setAutoRefresh(!autoRefresh)}
                    >
                        <Radio className="mr-2 h-4 w-4" />
                        {autoRefresh ? 'Streaming Live' : 'Start Stream'}
                    </Button>
                </div>

                {/* Event List */}
                <Card>
                    <CardHeader>
                        <CardTitle>Event Log ({filtered.length})</CardTitle>
                        <CardDescription>Click on an event to view its payload</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2 max-h-[600px] overflow-y-auto">
                            {filtered.length === 0 ? (
                                <div className="text-center py-12" style={{ color: 'var(--muted)' }}>
                                    <Radio className="h-12 w-12 mx-auto mb-4 opacity-30" />
                                    <p className="text-lg font-medium">No events found</p>
                                    <p className="text-sm">Events will appear here as they are published to the bus</p>
                                </div>
                            ) : (
                                filtered.map((event) => {
                                    const style = getEventStyle(event.type);
                                    const Icon = style.icon;
                                    const isExpanded = expandedId === event.id;

                                    return (
                                        <div
                                            key={event.id}
                                            className="border rounded-lg p-4 cursor-pointer transition-all hover:shadow-sm"
                                            style={{ borderColor: 'var(--card-border)' }}
                                            onClick={() => setExpandedId(isExpanded ? null : event.id)}
                                        >
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className={`p-2 rounded-lg ${style.bg}`}>
                                                        <Icon className={`h-4 w-4 ${style.color}`} />
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-sm" style={{ color: 'var(--foreground)' }}>
                                                            {event.type}
                                                        </p>
                                                        <p className="text-xs" style={{ color: 'var(--muted)' }}>
                                                            Source: {event.source} · {new Date(event.timestamp).toLocaleTimeString()}
                                                        </p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-mono px-2 py-0.5 rounded" style={{ background: 'var(--muted-bg)', color: 'var(--muted)' }}>
                                                        {event.id.slice(0, 8)}
                                                    </span>
                                                    {isExpanded ? <ChevronUp className="h-4 w-4" style={{ color: 'var(--muted)' }} /> : <ChevronDown className="h-4 w-4" style={{ color: 'var(--muted)' }} />}
                                                </div>
                                            </div>

                                            {isExpanded && (
                                                <div className="mt-3 pt-3 border-t" style={{ borderColor: 'var(--table-border)' }}>
                                                    <pre
                                                        className="text-xs p-3 rounded-lg overflow-x-auto font-mono"
                                                        style={{ background: 'var(--muted-bg)', color: 'var(--muted)' }}
                                                    >
                                                        {JSON.stringify(event.payload, null, 2)}
                                                    </pre>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </DashboardLayout>
    );
}

function getMockEvents(): KafkaEvent[] {
    return [
        { id: 'evt_001', type: 'payment.received', payload: { member: 'Peter Wekesa', amount: 5000, method: 'mpesa', chama: 'Mwanzo Group' }, timestamp: new Date(Date.now() - 120000).toISOString(), source: 'payments-service' },
        { id: 'evt_002', type: 'order.created', payload: { buyer: 'Grace Ochieng', listing: 'Office Supplies', amount: 15000 }, timestamp: new Date(Date.now() - 300000).toISOString(), source: 'marketplace-service' },
        { id: 'evt_003', type: 'member.joined', payload: { name: 'David Otieno', chama: 'Tujitegemee', role: 'MEMBER' }, timestamp: new Date(Date.now() - 600000).toISOString(), source: 'core-service' },
        { id: 'evt_004', type: 'loan.approved', payload: { member: 'Mary Wanjiku', amount: 50000, term: '12 months', rate: '12%' }, timestamp: new Date(Date.now() - 900000).toISOString(), source: 'core-service' },
        { id: 'evt_005', type: 'notification.sent', payload: { type: 'sms', recipient: '254712345678', message: 'Your contribution of KES 5,000 has been received' }, timestamp: new Date(Date.now() - 1200000).toISOString(), source: 'notifications-service' },
        { id: 'evt_006', type: 'payment.completed', payload: { transaction_id: 'TXN_98765', amount: 10000, status: 'COMPLETED', member: 'John Kimani' }, timestamp: new Date(Date.now() - 1500000).toISOString(), source: 'payments-service' },
        { id: 'evt_007', type: 'order.fulfilled', payload: { order_id: 'ORD_12345', seller: 'Faraja Savings', buyer: 'Mwanzo Group', tracking: 'SHIPPED' }, timestamp: new Date(Date.now() - 1800000).toISOString(), source: 'marketplace-service' },
        { id: 'evt_008', type: 'loan.repayment', payload: { member: 'Peter Wekesa', amount: 5500, remaining_balance: 44500, loan_id: 'LN_001' }, timestamp: new Date(Date.now() - 2100000).toISOString(), source: 'core-service' },
        { id: 'evt_009', type: 'member.role_changed', payload: { member: 'Grace Ochieng', old_role: 'MEMBER', new_role: 'SECRETARY', chama: 'Mwanzo Group' }, timestamp: new Date(Date.now() - 2400000).toISOString(), source: 'core-service' },
        { id: 'evt_010', type: 'notification.broadcast', payload: { type: 'push', chama: 'Tujitegemee', message: 'Contribution deadline: March 15, 2026', recipients: 48 }, timestamp: new Date(Date.now() - 2700000).toISOString(), source: 'notifications-service' },
    ];
}
