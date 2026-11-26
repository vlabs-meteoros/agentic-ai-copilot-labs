'use strict';
// API tests: start the real server on a free port, with a temporary copy of test/fixtures/ (the original data).
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createServer } = require('../src/server');

/** Start a server on a temporary copy of test/fixtures/. Returns {base, call, close}. */
async function startServer() {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kaverirooms-api-'));
  fs.cpSync(path.join(__dirname, 'fixtures'), dataDir, { recursive: true });
  const server = createServer({ dataDir });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  async function call(method, url, body) {
    const response = await fetch(base + url, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : {},
      body: body ? JSON.stringify(body) : undefined,
    });
    const text = await response.text();
    return { status: response.status, body: text ? JSON.parse(text) : null };
  }
  return { base, call, close: () => new Promise((resolve) => server.close(resolve)) };
}

test('GET /api/rooms lists the six rooms', async () => {
  const app = await startServer();
  try {
    const { status, body } = await app.call('GET', '/api/rooms');
    assert.equal(status, 200);
    assert.equal(body.length, 6);
  } finally { await app.close(); }
});

test('GET /api/bookings?date= returns that day in room order', async () => {
  const app = await startServer();
  try {
    const { body } = await app.call('GET', '/api/bookings?date=2026-12-08');
    assert.deepEqual(body.map((b) => b.id), ['B-1006', 'B-1005', 'B-1004', 'B-1007']);
  } finally { await app.close(); }
});

test('POST /api/bookings creates a booking (201), and a clash is a 409', async () => {
  const app = await startServer();
  try {
    const input = { roomId: 'tunga', date: '2026-12-10', start: '09:00', end: '10:30', title: 'Retro', organiser: 'Kavya Shetty', attendees: 7 };
    const created = await app.call('POST', '/api/bookings', input);
    assert.equal(created.status, 201);
    assert.equal(created.body.id, 'B-1010');
    const clash = await app.call('POST', '/api/bookings', { ...input, start: '10:00', end: '11:00' });
    assert.equal(clash.status, 409);
    assert.equal(clash.body.conflictWith, 'B-1010');
  } finally { await app.close(); }
});

test('bad input is a 400 with an error message', async () => {
  const app = await startServer();
  try {
    const { status, body } = await app.call('POST', '/api/bookings', { roomId: 'kabini' });
    assert.equal(status, 400);
    assert.match(body.error, /date/);
  } finally { await app.close(); }
});

test('DELETE /api/bookings/:id is a 204, then a 404', async () => {
  const app = await startServer();
  try {
    assert.equal((await app.call('DELETE', '/api/bookings/B-1001')).status, 204);
    assert.equal((await app.call('DELETE', '/api/bookings/B-1001')).status, 404);
  } finally { await app.close(); }
});

test('the browser app is served from /, and nothing outside public/ is', async () => {
  const app = await startServer();
  try {
    const page = await fetch(`${app.base}/`);
    assert.equal(page.status, 200);
    assert.match(await page.text(), /KaveriRooms/);
    const sneaky = await fetch(`${app.base}/..%2Fpackage.json`);
    assert.equal(sneaky.status, 404);
  } finally { await app.close(); }
});
