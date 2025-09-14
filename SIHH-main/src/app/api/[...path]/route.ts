import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const json = (data: any, status = 200) => NextResponse.json(data, { status });
const notFound = () => json({ error: 'Not Found' }, 404);
const methodNotAllowed = () => json({ error: 'Method Not Allowed' }, 405);

// ---- handlers (your stub API)
function root() { return json({ ok: true, service: 'railoptima', paths: ['/api/health'] }); }
function health() { return json({ ok: true }); }
function status() { return json({ status: 'API stub running' }); }
function echo(req: NextRequest) { return json({ echo: new URL(req.url).searchParams.get('msg') ?? 'hi' }); }
function stations() { return json({ stations: ['Station A', 'Station B', 'Station C'] }); }
function trains() { return json({ trains: ['Train 1', 'Train 2', 'Train 3'] }); }
function train(id: string) { return json({ train_id: id, status: 'on-time', location: 'Station A' }); }
function schedule(id: string) {
  return json({ train_id: id, schedule: [{ station: 'Station A', time: '09:00' }, { station: 'Station B', time: '09:30' }] });
}
async function optimize(req: NextRequest) {
  const url = new URL(req.url);
  const qs = url.searchParams.getAll('trains');
  let trains = qs.length ? qs : undefined;
  if (!trains && ['POST','PUT','PATCH'].includes(req.method)) {
    try { const b = await req.text(); const j = b && JSON.parse(b); if (Array.isArray(j?.trains)) trains = j.trains; } catch {}
  }
  return json({ optimized: true, trains: trains ?? ['Train 1', 'Train 2'], message: 'Schedule optimized successfully (stub).' });
}
function alerts() { return json({ alerts: [{ train: 'Train 1', message: 'Minor delay' }, { train: 'Train 2', message: 'On time' }] }); }
async function getPrefs(userId: string) { return json({ user_id: userId, preferences: { theme: 'dark', notifications: true } }); }
async function setPrefs(userId: string, req: NextRequest) {
  let prefs: any = {}; try { const t = await req.text(); if (t) prefs = JSON.parse(t); } catch {}
  return json({ user_id: userId, updated_preferences: prefs });
}

// ---- tiny router
async function route(req: NextRequest) {
  const segs = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);
  if (segs.length === 0) return root();
  if (segs[0] === 'health' && segs.length === 1) return health();
  if (segs[0] === 'status' && segs.length === 1) return status();
  if (segs[0] === 'echo' && segs.length === 1) return echo(req);
  if (segs[0] === 'stations' && segs.length === 1) return stations();
  if (segs[0] === 'trains' && segs.length === 1) return trains();
  if (segs[0] === 'train' && segs.length === 2) return train(segs[1]);
  if (segs[0] === 'schedule' && segs.length === 2) return schedule(segs[1]);
  if (segs[0] === 'optimize' && segs[1] === 'schedule') return optimize(req);
  if (segs[0] === 'alerts' && segs.length === 1) return alerts();
  if (segs[0] === 'users' && segs.length === 3 && segs[2] === 'preferences' && req.method === 'GET') return getPrefs(segs[1]);
  if (segs[0] === 'users' && segs.length === 3 && segs[2] === 'preferences' && ['POST','PUT','PATCH'].includes(req.method))
    return setPrefs(segs[1], req);
  return notFound();
}

export async function GET(req: NextRequest) { return route(req); }
export async function POST(req: NextRequest) { return route(req); }
export async function PUT(req: NextRequest) { return route(req); }
export async function PATCH(req: NextRequest) { return route(req); }
export async function DELETE() { return methodNotAllowed(); }
export async function OPTIONS() {
  return new NextResponse(null, { status: 200, headers: {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
  }});
}
