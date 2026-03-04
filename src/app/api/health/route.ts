import { NextResponse } from 'next/server';

const services = [
    { name: 'Core Service', url: 'http://localhost:8001', port: 8001 },
    { name: 'Marketplace', url: 'http://localhost:8002', port: 8002 },
    { name: 'Payments', url: 'http://localhost:8003', port: 8003 },
    { name: 'Notifications', url: 'http://localhost:8004', port: 8004 },
    { name: 'Messaging', url: 'http://localhost:8005', port: 8005 },
    { name: 'Kafka Event Bus', url: 'http://localhost:9092', port: 9092 },
];

export async function GET() {
    const results = await Promise.all(
        services.map(async (service) => {
            const start = Date.now();
            try {
                const res = await fetch(`${service.url}/health`, {
                    signal: AbortSignal.timeout(3000),
                });
                const latency = Date.now() - start;
                const data = await res.json();
                return {
                    ...service,
                    status: 'healthy' as const,
                    latency,
                    details: data,
                };
            } catch {
                return {
                    ...service,
                    status: 'unhealthy' as const,
                    latency: Date.now() - start,
                    details: null,
                };
            }
        })
    );
    return NextResponse.json(results);
}
