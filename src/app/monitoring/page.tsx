'use client';

import { useState, useEffect, useCallback } from 'react';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Header } from '@/components/layout/header';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Activity,
    RefreshCw,
    Server,
    Wifi,
    WifiOff,
    Clock,
    CheckCircle2,
    XCircle,
    Loader2,
    Zap,
} from 'lucide-react';

interface ServiceStatus {
    name: string;
    url: string;
    port: number;
    status: 'healthy' | 'unhealthy';
    latency: number;
    details: Record<string, unknown> | null;
}

const serviceIcons: Record<string, string> = {
    'Core Service': '🏦',
    'Marketplace': '🛒',
    'Payments': '💳',
    'Notifications': '🔔',
    'Messaging': '💬',
    'Kafka Event Bus': '📡',
};

export default function MonitoringPage() {
    const [services, setServices] = useState<ServiceStatus[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastCheck, setLastCheck] = useState<Date | null>(null);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [countdown, setCountdown] = useState(10);

    const fetchHealth = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/health');
            const data = await res.json();
            setServices(data);
            setLastCheck(new Date());
        } catch {
            // keep previous state
        } finally {
            setLoading(false);
            setCountdown(10);
        }
    }, []);

    // Initial fetch
    useEffect(() => {
        fetchHealth();
    }, [fetchHealth]);

    // Auto-refresh
    useEffect(() => {
        if (!autoRefresh) return;
        const interval = setInterval(() => {
            setCountdown((prev) => {
                if (prev <= 1) {
                    fetchHealth();
                    return 10;
                }
                return prev - 1;
            });
        }, 1000);
        return () => clearInterval(interval);
    }, [autoRefresh, fetchHealth]);

    const healthyCount = services.filter((s) => s.status === 'healthy').length;
    const totalCount = services.length;
    const avgLatency = services.length > 0
        ? Math.round(services.reduce((sum, s) => sum + s.latency, 0) / services.length)
        : 0;

    return (
        <DashboardLayout>
            <Header title="Service Monitoring" subtitle="Real-time health status of all microservices" />

            <div className="p-6 space-y-6">
                {/* Top Stats */}
                <div className="grid gap-4 md:grid-cols-4">
                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${healthyCount === totalCount ? 'bg-green-100' : 'bg-red-100'}`}>
                                    {healthyCount === totalCount ? (
                                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                                    ) : (
                                        <XCircle className="h-5 w-5 text-red-600" />
                                    )}
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Overall Status</p>
                                    <p className={`text-lg font-bold ${healthyCount === totalCount ? 'text-green-600' : 'text-red-600'}`}>
                                        {healthyCount === totalCount ? 'All Healthy' : 'Issues Found'}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-blue-100">
                                    <Server className="h-5 w-5 text-blue-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Services Up</p>
                                    <p className="text-lg font-bold" style={{ color: 'var(--foreground)' }}>{healthyCount} / {totalCount}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-purple-100">
                                    <Zap className="h-5 w-5 text-purple-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Avg Latency</p>
                                    <p className="text-lg font-bold" style={{ color: 'var(--foreground)' }}>{avgLatency}ms</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-yellow-100">
                                    <Clock className="h-5 w-5 text-yellow-600" />
                                </div>
                                <div>
                                    <p className="text-sm" style={{ color: 'var(--muted)' }}>Last Check</p>
                                    <p className="text-lg font-bold" style={{ color: 'var(--foreground)' }}>
                                        {lastCheck ? lastCheck.toLocaleTimeString() : '...'}
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Controls */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Button onClick={fetchHealth} variant="outline" disabled={loading}>
                            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                            Refresh Now
                        </Button>
                        <Button
                            variant={autoRefresh ? 'default' : 'outline'}
                            onClick={() => setAutoRefresh(!autoRefresh)}
                        >
                            <Activity className="mr-2 h-4 w-4" />
                            Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
                        </Button>
                    </div>
                    {autoRefresh && (
                        <span className="text-sm" style={{ color: 'var(--muted)' }}>
                            Next refresh in <span className="font-mono font-bold">{countdown}s</span>
                        </span>
                    )}
                </div>

                {/* Service Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {services.map((service) => (
                        <Card key={service.name} className="transition-all duration-200 hover:shadow-md">
                            <CardContent className="p-6">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <span className="text-2xl">{serviceIcons[service.name] || '⚙️'}</span>
                                        <div>
                                            <h3 className="font-semibold" style={{ color: 'var(--foreground)' }}>{service.name}</h3>
                                            <p className="text-xs font-mono" style={{ color: 'var(--muted)' }}>
                                                :{service.port}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div
                                            className={`h-3 w-3 rounded-full ${service.status === 'healthy'
                                                    ? 'bg-green-500 pulse-green'
                                                    : 'bg-red-500 pulse-red'
                                                }`}
                                        />
                                        {service.status === 'healthy' ? (
                                            <Wifi className="h-4 w-4 text-green-500" />
                                        ) : (
                                            <WifiOff className="h-4 w-4 text-red-500" />
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm" style={{ color: 'var(--muted)' }}>Status</span>
                                        <span className={`text-sm font-medium px-2 py-0.5 rounded-full ${service.status === 'healthy'
                                                ? 'bg-green-100 text-green-700'
                                                : 'bg-red-100 text-red-700'
                                            }`}>
                                            {service.status === 'healthy' ? '● Healthy' : '● Down'}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm" style={{ color: 'var(--muted)' }}>Latency</span>
                                        <span className={`text-sm font-mono font-medium ${service.latency < 100 ? 'text-green-600' : service.latency < 500 ? 'text-yellow-600' : 'text-red-600'
                                            }`}>
                                            {service.latency}ms
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm" style={{ color: 'var(--muted)' }}>Endpoint</span>
                                        <span className="text-xs font-mono" style={{ color: 'var(--muted)' }}>{service.url}</span>
                                    </div>
                                </div>

                                {/* Latency bar */}
                                <div className="mt-4">
                                    <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden" style={{ background: 'var(--muted-bg)' }}>
                                        <div
                                            className={`h-full rounded-full transition-all duration-500 ${service.latency < 100 ? 'bg-green-500' : service.latency < 500 ? 'bg-yellow-500' : 'bg-red-500'
                                                }`}
                                            style={{ width: `${Math.min(100, (service.latency / 500) * 100)}%` }}
                                        />
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        </DashboardLayout>
    );
}
