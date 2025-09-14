import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const json = (data: any, status = 200) =>
  new NextResponse(JSON.stringify(data), {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
  });

/* -------------------- stub data -------------------- */
const TRAINS = [
  { id: 'T1', name: 'Train 1', route: 'A-B', departure_time: '09:00', arrival_time: '09:30', capacity: 300, delay_minutes: 0 },
  { id: 'T2', name: 'Train 2', route: 'B-C', departure_time: '10:00', arrival_time: '10:40', capacity: 280, delay_minutes: 3 },
];

const STATIONS = ['Station A', 'Station B', 'Station C'];

const DISRUPTIONS = [
  { id: 'D1', type: 'signal', severity: 'low', affected_trains: ['T1'], affected_stations: ['Station B'], start_time: new Date().toISOString(), description: 'Signal check' },
];

const ALERTS = [{ id: 'A1', train: 'T1', level: 'info', message: 'Minor delay cleared' }];

/* -------------------- endpoints (JSON only) -------------------- */
function root() { return json({ ok: true, service: 'railoptima' }); }
function health() { return json({ ok: true }); }

function stations() { return json(STATIONS); }
function trainsList() { return json(TRAINS); }
function trainsCount() { return json({ total_active_trains: TRAINS.length, timestamp: new Date().toISOString() }); }
function trainById(id: string) {
  const t = TRAINS.find(x => x.id === id) ?? { id, name: `Train ${id}`, route: 'A-B', departure_time: '09:00', arrival_time: '09:30', capacity: 300, delay_minutes: 0 };
  return json(t);
}
function disruptions() { return json(DISRUPTIONS); }
function alerts() { return json(ALERTS); }
function kpi() {
  return json({ on_time_percentage: 96.2, avg_delay_minutes: 2.4, incidents_today: 1, network_load: 0.54, timestamp: new Date().toISOString() });
}
async function optimize(req: NextRequest) {
  let payload: any = {};
  try { const t = await req.text(); payload = t ? JSON.parse(t) : {}; } catch {}
  return json({ optimized: true, message: 'Schedule optimized (stub)', input: payload, result: { objective: 'min_delay', improvement_pct: 12.3 } });
}

/* ---- IMPORTANT: your UI calls /api/trains/csv but expects JSON; return JSON here ---- */
function trainsCsvJson() {
  const headers = ['id', 'name', 'route', 'departure_time', 'arrival_time', 'capacity', 'delay_minutes'];
  // rows as array of objects (easy for UI to render)
  return json({ headers, rows: TRAINS });
}

/* -------------------- router -------------------- */
async function router(req: NextRequest) {
  const segs = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);

  if (segs.length === 0) return root();
  if (segs[0] === 'health') return health();

  // trains
  if (segs[0] === 'trains' && segs.length === 1 && req.method === 'GET') return trainsList();
  if (segs[0] === 'trains' && segs[1] === 'count') return trainsCount();
  if (segs[0] === 'trains' && segs[1] === 'csv') return trainsCsvJson(); // JSON, not a file
  if (segs[0] === 'train'  && segs.length === 2) return trainById(segs[1]);

  // others
  if (segs[0] === 'stations')    return stations();
  if (segs[0] === 'disruptions') return disruptions();
  if (segs[0] === 'alerts')      return alerts();
  if (segs[0] === 'kpi')         return kpi();

  if (segs[0] === 'optimize')    return optimize(req);

  return json({ error: 'Not Found' }, 404);
}

export async function GET(req: NextRequest)   { return router(req); }
export async function POST(req: NextRequest)  { return router(req); }
export async function PUT(req: NextRequest)   { return router(req); }
export async function PATCH(req: NextRequest) { return router(req); }
export async function DELETE()                { return json({ error: 'Method Not Allowed' }, 405); }
export async function OPTIONS() {
  return new NextResponse(null, { status: 200, headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }});
}
