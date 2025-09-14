import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const j = (data: any, status = 200) =>
  new NextResponse(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });

const asArray = (v: any) => (Array.isArray(v) ? v : v == null ? [] : [v]); // coerce to array

// ---------- DATA your UI likely maps over ----------
function stations() {
  // must be string[]
  return j(['Station A', 'Station B', 'Station C']);
}

function trainsList() {
  // must be Train[]
  return j([
    {
      id: 'T1',
      name: 'Train 1',
      route: 'A-B',
      departure_time: '09:00',
      arrival_time: '09:30',
      capacity: 300,
      delay_minutes: 0,
    },
    {
      id: 'T2',
      name: 'Train 2',
      route: 'B-C',
      departure_time: '10:00',
      arrival_time: '10:40',
      capacity: 280,
      delay_minutes: 3,
    },
  ]);
}

function disruptions() {
  // must be Disruption[]
  return j([
    {
      id: 'D1',
      type: 'signal',
      severity: 'low',
      affected_trains: ['T1'],
      affected_stations: ['Station B'],
      start_time: new Date().toISOString(),
      description: 'Signal check',
    },
  ]);
}

function alerts() {
  // must be Alert[]
  return j([{ id: 'A1', train: 'T1', level: 'info', message: 'Minor delay cleared' }]);
}

// ---------- objects (not arrays) ----------
function health() {
  return j({ ok: true });
}

function trainsCount() {
  return j({ total_active_trains: 2, timestamp: new Date().toISOString() });
}

function kpi() {
  return j({
    on_time_percentage: 96.2,
    avg_delay_minutes: 2.4,
    incidents_today: 1,
    network_load: 0.54,
    timestamp: new Date().toISOString(),
  });
}

function trainById(id: string) {
  return j({
    id,
    name: `Train ${id}`,
    route: 'A-B',
    departure_time: '09:00',
    arrival_time: '09:30',
    capacity: 300,
    delay_minutes: 0,
  });
}

async function optimize(req: NextRequest) {
  let payload: any = {};
  try {
    const t = await req.text();
    payload = t ? JSON.parse(t) : {};
  } catch {
    payload = {};
  }
  return j({
    optimized: true,
    message: 'Schedule optimized (stub)',
    input: payload,
    result: { objective: 'min_delay', improvement_pct: 12.3 },
  });
}

// ---------- debug endpoint to verify shapes quickly ----------
function debug() {
  return j({
    endpoints: {
      '/api/stations': 'string[]',
      '/api/trains': 'Train[]',
      '/api/trains/count': '{ total_active_trains: number }',
      '/api/disruptions': 'Disruption[]',
      '/api/alerts': 'Alert[]',
      '/api/kpi': 'object',
      '/api/train/:id': 'Train',
      '/api/optimize (POST)': 'object',
      '/api/health': '{ ok: true }',
    },
  });
}

// ---------- tiny router ----------
async function router(req: NextRequest) {
  const segs = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);

  if (segs.length === 0) return j({ ok: true, service: 'railoptima' });
  if (segs[0] === 'health') return health();
  if (segs[0] === 'debug') return debug();

  if (segs[0] === 'stations') return stations();
  if (segs[0] === 'trains' && segs.length === 1 && req.method === 'GET') return trainsList();
  if (segs[0] === 'trains' && segs[1] === 'count') return trainsCount();
  if (segs[0] === 'train' && segs.length === 2) return trainById(segs[1]);

  if (segs[0] === 'disruptions') return disruptions();
  if (segs[0] === 'alerts') return alerts();
  if (segs[0] === 'kpi') return kpi();

  if (segs[0] === 'optimize') return optimize(req);

  return j({ error: 'Not Found' }, 404);
}

export async function GET(req: NextRequest) {
  return router(req);
}
export async function POST(req: NextRequest) {
  return router(req);
}
export async function PUT(req: NextRequest) {
  return router(req);
}
export async function PATCH(req: NextRequest) {
  return router(req);
}
export async function DELETE() {
  return j({ error: 'Method Not Allowed' }, 405);
}
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
