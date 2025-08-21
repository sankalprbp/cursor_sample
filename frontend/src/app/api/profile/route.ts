import { NextRequest, NextResponse } from 'next/server';

// TODO: replace with real auth/session lookup
async function getCurrentUserId(req: NextRequest): Promise<string | null> {
  // If you use cookies/JWT, parse here. Return null if unauthenticated.
  return 'demo-user-id';
}

export async function PUT(req: NextRequest) {
  const userId = await getCurrentUserId(req);
  if (!userId) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const body = await req.json().catch(() => ({}));
  const name = typeof body.name === 'string' ? body.name.trim() : undefined;
  const phone = typeof body.phone === 'string' ? body.phone.trim() : undefined;
  const avatarUrl = typeof body.avatarUrl === 'string' ? body.avatarUrl.trim() : undefined;

  // Basic validation
  if (name && name.length > 100) return NextResponse.json({ error: 'Name too long' }, { status: 400 });
  if (phone && phone.length > 30) return NextResponse.json({ error: 'Phone too long' }, { status: 400 });

  // TODO: persist to your real backend. For now, echo back.
  const updated = {
    id: userId,
    name: name ?? 'Demo User',
    email: 'demo@example.com',
    phone,
    avatarUrl,
  };

  return NextResponse.json(updated, { status: 200 });
}
