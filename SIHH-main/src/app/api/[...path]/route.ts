import { NextRequest, NextResponse } from 'next/server';
export const runtime = 'nodejs';

const API_BASE_URL = process.env.API_BASE_URL;

async function handleRequest(req: NextRequest, path: string[], method: string) {
  if (!API_BASE_URL) {
    return NextResponse.json(
      { error: 'API_BASE_URL is not set on the server' },
      { status: 500 },
    );
  }

  const url = `${API_BASE_URL}/${path.join('/')}${req.nextUrl.search}`;
  const init: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: method === 'GET' || method === 'HEAD' ? undefined : await req.text(),
    // Optional: forward auth header if you use it
    // headers: Object.fromEntries(req.headers),
  };

  try {
    const r = await fetch(url, init);
    const body = await r.text();
    return new NextResponse(body, {
      status: r.status,
      headers: { 'content-type': r.headers.get('content-type') ?? 'application/json' },
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: 'Upstream API unreachable', detail: String(err?.message ?? err) },
      { status: 502 },
    );
  }
}

export async function GET(req: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(req, params.path, 'GET');
}
export async function POST(req: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(req, params.path, 'POST');
}
export async function PUT(req: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(req, params.path, 'PUT');
}
export async function DELETE(req: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(req, params.path, 'DELETE');
}
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
