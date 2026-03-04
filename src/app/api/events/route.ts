import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const res = await fetch('http://localhost:9092/events?limit=50', {
            signal: AbortSignal.timeout(3000),
        });
        const data = await res.json();
        return NextResponse.json(data);
    } catch {
        return NextResponse.json({ events: [] });
    }
}
