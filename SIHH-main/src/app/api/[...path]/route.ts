import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const json = (data: any, status = 200) => NextResponse.json(data, { status });
const notFound = () => json({ error: 'Not Found' }, 404);
const methodNotAllowed = () => json({ error: 'Method Not Allowed' }, 405);

// ---- Minimal in-Vercel “backend” matching your frontend client ----
function health()       { return json({ ok: true }); }
function root()         { return json({ ok: true, service: 'railoptima', paths: ['/api/health'] }); }
function stations()     { return json({ stations: ['Station A', 'Station B', 'Station C'] }); }
function trainsList()   { return json([{ id:'T1', name:'Train 1', route:'A-B', departure_time:'09:00', arrival_time:'09:30', capacity: 300, delay_minutes: 0 }]); }
function trainsCount()  { return json({ total_active_trains: 1, timestamp: new Date().toISOString() }); }
function trainById(id: string) {
  return json({ id, name:`Train ${id}`, route:'A-B', departure_time:'09:00', arrival_time:'09:30', capacity: 300, delay_minutes: 0 });
}
function disruptions()  {
  return json([
    { id:'D1', type:'signal', severity:'low', affected_trains:['T1'], affected_stations:['Station B'], start_time:new Date().toISOString(), description:'Signal check' }
  ]);
}
function kpiData() {
  return json({
    on_time_percentage: 96.2,
    avg_delay_minutes: 2.4,
    incidents_today: 1,
    network_load: 0.54,
    timestamp: new Date().toISOString()
  });
}
function alerts() {
  return json({ alerts: [{ train: 'T1', message: 'Minor delay cleared' }] });
}
async function optimize(req: NextRequest) {
  let payload: any = {};
  try { const t = await req.text(); payload = t ? JSON.parse(t) : {}; } catch {}
  return json({
    optimized: true,
    message: 'Schedule optimized successfully (stub).',
    input: payload,
    result: { objective: 'min_delay', improvement_pct: 12.3 }
  });
}
function echo(req: NextRequest) { return json({ echo: new URL(req.url).searchParams.get('msg') ?? 'hi' }); }

// ---- Router that matches your client in `src/lib/api.ts`
async function route(req: NextRequest) {
  const segs = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);

  if (segs.length === 0)                     return root();
  if (segs[0] === 'health' && segs.length===1) return health();

  // trains
  if (segs[0] === 'trains' && segs.length===0) return trainsList();       // safety
  if (segs[0] === 'trains' && segs.length===1 && req.method==='GET') return trainsList();
  if (segs[0] === 'trains' && segs[1] === 'count')                 return trainsCount();
  if (segs[0] === 'trains' && segs.length===2)                     return trainById(segs[1]);

  // other collections used by your hooks/client
  if (segs[0] === 'stations')     return stations();
  if (segs[0] === 'disruptions')  return disruptions();
  if (segs[0] === 'kpi')          return kpiData();          // e.g. apiClient.getKPIData()
  if (segs[0] === 'alerts')       return alerts();

  // optimization (POST from client)
  if (segs[0] === 'optimize')     return optimize(req);

  // diagnostics
  if (segs[0] === 'echo')         return echo(req);

  return notFound();
}

// ---- HTTP methods
export async function GET(req: NextRequest)    { return route(req); }
export async function POST(req: NextRequest)   { return route(req); }
export async function PUT(req: NextRequest)    { return route(req); }
export async function PATCH(req: NextRequest)  { return route(req); }
export async function DELETE()                 { return methodNotAllowed(); }
export async function OPTIONS() {
  return new NextResponse(null, { status: 200, headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }});
}
