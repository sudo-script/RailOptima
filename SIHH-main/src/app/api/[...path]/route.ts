// Next.js App Router API that implements your stub backend directly on Vercel
import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';           // Serverless (Node) runtime
export const dynamic = 'force-dynamic';    // never cache

type Json = string | number | boolean | null | Json[] | { [k: string]: Json };

function json(data: Json, status = 200) {
  return NextResponse.json(data, { status });
}

function notFound(msg = 'Not Found') {
  return json({ error: msg }, 404);
}

function methodNotAllowed() {
  return json({ error: 'Method Not Allowed' }, 405);
}

// ---- Handlers for each stub route ----
function handleRoot() {
  return json({ ok: true, service: 'railoptima', paths: ['/health', '/api/health'] });
}

function handleHealth() {
  return json({ ok: true });
}

function handleStatus() {
  return json({ status: 'API stub running' });
}

function handleEcho(req: NextRequest) {
  const msg = new URL(req.url).searchParams.get('msg') ?? 'hi';
  return json({ echo: msg });
}

function handleStations() {
  return json({ stations: ['Station A', 'Station B', 'Station C'] });
}

function handleTrains() {
  return json({ trains: ['Train 1', 'Train 2', 'Train 3'] });
}

function handleTrain(trainId: string) {
  return json({ train_id: trainId, status: 'on-time', location: 'Station A' });
}

function handleSchedule(trainId: string) {
  return json({
    train_id: trainId,
    schedule: [
      { station: 'Station A', time: '09:00' },
      { station: 'Station B', time: '09:30' },
    ],
  });
}

async function handleOptimizeSchedule(req: NextRequest) {
  const url = new URL(req.url);
  // Accept trains from query (?trains=Train%201&trains=Train%202) or from JSON body
  const trainsFromQuery = url.searchParams.getAll('trains');
  let trains = trainsFromQuery.length ? trainsFromQuery : undefined;

  if (!trains && (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH')) {
    try {
      const bodyText = await req.text();
      if (bodyText) {
        const parsed = JSON.parse(bodyText);
        if (Array.isArray(parsed?.trains)) trains = parsed.trains;
      }
    } catch {
      /* ignore */
    }
  }

  return json({
    optimized: true,
    trains: trains ?? ['Train 1', 'Train 2'],
    message: 'Schedule optimized successfully (stub).',
  });
}

function handleAlerts() {
  return json({
    alerts: [
      { train: 'Train 1', message: 'Minor delay' },
      { train: 'Train 2', message: 'On time' },
    ],
  });
}

async function handleGetUserPrefs(userId: string) {
  return json({ user_id: userId, preferences: { theme: 'dark', notifications: true } });
}

async function handleSetUserPrefs(userId: string, req: NextRequest) {
  let prefs: any = {};
  try {
    const txt = await req.text();
    if (txt) prefs = JSON.parse(txt);
  } catch {/* ignore */}
  return json({ user_id: userId, updated_preferences: prefs });
}

// ---- Router ----
async function router(req: NextRequest) {
  // path segments after /api/
  const segments = req.nextUrl.pathname.replace(/^\/api\/?/, '').split('/').filter(Boolean);

  // Support both "/" and "/health" and "/api/health"
  if (segments.length === 0) {
    return handleRoot();
  }
  if (segments.length === 1 && segments[0] === 'health') {
    return handleHealth();
  }
  if (segments.length === 1 && segments[0] === 'status') {
    return handleStatus();
  }
  if (segments.length === 1 && segments[0] === 'echo') {
    return handleEcho(req);
  }
  if (segments.length === 1 && segments[0] === 'stations') {
    return handleStations();
  }
  if (segments.length === 1 && segments[0] === 'trains') {
    return handleTrains();
  }
  if (segments.length === 2 && segments[0] === 'train') {
    return handleTrain(segments[1]);
  }
  if (segments.length === 2 && segments[0] === 'schedule') {
    return handleSchedule(segments[1]);
  }
  if (
    segments.length === 2 &&
    segments[0] === 'users' &&
    segments[1] &&
    req.method === 'GET'
  ) {
    return handleGetUserPrefs(segments[1]);
  }
  if (
    segments.length === 3 &&
    segments[0] === 'users' &&
    segments[2] === 'preferences' &&
    req.method === 'GET'
  ) {
    return handleGetUserPrefs(segments[1]);
  }
  if (
    segments.length === 3 &&
    segments[0] === 'users' &&
    segments[2] === 'preferences' &&
    (req.method === 'POST' || req.method === 'PUT' || req.method === 'PATCH')
  ) {
    return handleSetUserPrefs(segments[1], req);
  }
  if (segments.length === 2 && segments[0] === 'optimize' && segments[1] === 'schedule') {
    return handleOptimizeSchedule(req);
  }
  if (segments.length === 1 && segments[0] === 'alerts') {
    return handleAlerts();
  }

  return notFound();
}

// ---- HTTP methods ----
export async function GET(req: NextRequest, ctx: { params: { path: string[] } }) {
  return router(req);
}
export async function POST(req: NextRequest, ctx: { params: { path: string[] } }) {
  return router(req);
}
export async function PUT(req: NextRequest, ctx: { params: { path: string[] } }) {
  return router(req);
}
export async function PATCH(req: NextRequest, ctx: { params: { path: string[] } }) {
  return router(req);
}
export async function DELETE() {
  return methodNotAllowed();
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
