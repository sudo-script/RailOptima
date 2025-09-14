import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const json = (data: any, status = 200) => NextResponse.json(data, { status });
const methodNotAllowed = () => json({ error: 'Method Not Allowed' }, 405);

// ---- DATA SHAPES your UI expects ----
// /api/trains            -> Train[]                      (array)
// /api/trains/count      -> { total_active_trains: n }   (object)
// /api/stations          -> string[]                     (array)
// /api/disruptions       -> Disruption[]                 (array)
// /api/kpi               -> { ... }                      (object)
// /api/alerts            -> Alert[]                      (array)
// /api/optimize (POST)   -> { ... }                      (object)
// /api/health            -> { ok: true }                 (object)

function root() { return json({ ok: true, service: 'railoptima' }); }
function health() { return json({ ok: true }); }

// arrays
function stations() { return json(['Station A', 'Station B', 'Station C']); }
function trainsList() {
  return json([
    { id:'T1', name:'Train 1', route:'A-B', departure_time:'09:00', arrival_time:'09:30', capacity:300, delay_minutes:0 },
    { id:'T2', name:'Train 2', route:'B-C', departure_time:'10:00', arrival_time:'10:40', capacity:280, delay_minutes:3 }
  ]);
}
function disruptions() {
  return json([
    { id:'D1', type:'signal', severity:'low', affected_trains:['T1'], affected_stations:['Station B'], start_time:new Date().toISOString(), description:'Signal check' }
  ]);
}
function alerts() {
  return json([
    { id:'A1', train:'T1', level:'info', message:'Minor delay cleared' }
  ]);
}

// objects
function trainsCount() { return json({ total_active_trains: 2, timestamp: new Date().toISOString() }); }
function kpiData() {
  return json({
    on_time_percentage: 96.2,
    avg_delay_minutes: 2.4,
    incidents_today: 1,
    network_load: 0.54,
    timestamp: new Date().toISOString()
  });
}
function trainById(id: string) {
  return json({ id, name:`Train ${id}`, route:'A-B', departure_time:'09:00', arrival_time:'09:30', capacity:300, delay_minutes:0 });
}
async function optimize(req: NextRequest) {
  let payload: any = {};
  try { const t = await req.text(); payload = t ? JSON.parse(t) : {}; } catch {}
  return json({ optimized:true, message:'Schedule optimized (stub)', input: payload, result:{ objective:'min_delay', improvement_pct:12.3 } });
}

async function route(req: NextRequest) {
  const segs = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);
  // root & health
  if (segs.length === 0) return root();
  if (segs[0] === 'health' && segs.length === 1) return health();

  // trains
  if (segs[0] === 'trains' && segs.length === 1 && req.method === 'GET') return trainsList(); // /api/trains
  if (segs[0] === 'trains' && segs[1] === 'count') return trainsCount();                       // /api/trains/count
  if (segs[0] === 'trains' && segs.length === 2) return trainById(segs[1]);                   // /api/trains/:id

  // arrays
  if (segs[0] === 'stations')     return stations();      // returns string[]
  if (segs[0] === 'disruptions')  return disruptions();   // returns Disruption[]
  if (segs[0] === 'alerts')       return alerts();        // returns Alert[]

  // objects
  if (segs[0] === 'kpi')          return kpiData();

  // optimize (POST/PUT/PATCH supported)
  if (segs[0] === 'optimize')     return optimize(req);

  return json({ error: 'Not Found' }, 404);
}

export async function GET(req: NextRequest)   { return route(req); }
export async function POST(req: NextRequest)  { return route(req); }
export async function PUT(req: NextRequest)   { return route(req); }
export async function PATCH(req: NextRequest) { return route(req); }
export async function DELETE()                { return methodNotAllowed(); }
export async function OPTIONS() {
  return new NextResponse(null, { status: 200, headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }});
}
