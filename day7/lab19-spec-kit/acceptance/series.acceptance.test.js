'use strict';
// Lab 19 acceptance test for FR-12 (recurring weekly bookings).
//
// Copy this file into your kaverirooms\test folder and run:   node --test
// It only uses the API contract in docs/FR-12-recurring-bookings.md, so it works whatever your code looks like inside.
// Don't change this file to make it pass: change the code (or ask Copilot to), and check the spec.

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { createServer } = require('../src/server');

// Its own small data set, so your own bookings from the lab don't change the results.
const ROOMS = [
  { id: 'kabini', name: 'Kabini', floor: 1, capacity: 4, equipment: ['TV'] },
  { id: 'hemavathi', name: 'Hemavathi', floor: 1, capacity: 6, equipment: ['TV', 'Whiteboard'] },
];
const HOLIDAYS = [
  { date: '2026-12-25', name: 'Christmas' },
  { date: '2027-01-01', name: "New Year's Day" },
];
const BOOKINGS = [
  { id: 'B-1001', roomId: 'kabini', date: '2026-12-07', start: '09:00', end: '09:30', title: 'Stand-up', organiser: 'Ravi Kumar', attendees: 4 },
  { id: 'B-1003', roomId: 'hemavathi', date: '2026-12-15', start: '14:00', end: '15:00', title: 'Quarterly review', organiser: 'Arjun Menon', attendees: 5 },
];

async function startServer() {
  const dataDir = fs.mkdtempSync(path.join(os.tmpdir(), 'kaverirooms-fr12-'));
  fs.writeFileSync(path.join(dataDir, 'rooms.json'), JSON.stringify(ROOMS));
  fs.writeFileSync(path.join(dataDir, 'holidays.json'), JSON.stringify(HOLIDAYS));
  fs.writeFileSync(path.join(dataDir, 'bookings.json'), JSON.stringify(BOOKINGS));
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
  return { call, close: () => new Promise((resolve) => server.close(resolve)) };
}

/** Run fn with a fresh server, and always stop the server afterwards. */
async function withServer(fn) {
  const app = await startServer();
  try { await fn(app.call); } finally { await app.close(); }
}

const fridays = { roomId: 'kabini', date: '2026-12-04', start: '10:00', end: '11:00', title: 'Design review', organiser: 'Ananya Iyer', attendees: 4, weeks: 6 };
const tuesdays = { roomId: 'hemavathi', date: '2026-12-08', start: '14:30', end: '15:30', title: 'Ops sync', organiser: 'Priya Nair', attendees: 5, weeks: 4 };

test('FR-12 rules 1, 5, 7: six Fridays, two of them holidays -> 4 booked, 2 skipped with the holiday name', () => withServer(async (call) => {
  const { status, body } = await call('POST', '/api/series', fridays);
  assert.equal(status, 201);
  assert.match(body.seriesId, /^S-\d+$/);
  assert.deepEqual(body.booked.map((b) => b.date), ['2026-12-04', '2026-12-11', '2026-12-18', '2027-01-08']);
  for (const booking of body.booked) {
    assert.equal(booking.seriesId, body.seriesId);
    assert.match(booking.id, /^B-\d+$/);
    assert.equal(booking.roomId, 'kabini');
    assert.equal(booking.start, '10:00');
    assert.equal(booking.end, '11:00');
  }
  assert.equal(new Set(body.booked.map((b) => b.id)).size, 4, 'every booking needs its own id');
  assert.deepEqual(body.skipped.map((s) => s.date), ['2026-12-25', '2027-01-01']);
  assert.match(body.skipped[0].reason, /holiday/i);
  assert.match(body.skipped[0].reason, /Christmas/);
  assert.match(body.skipped[1].reason, /New Year/);
}));

test('FR-12 rule 6: a clash skips only that week, and names the booking it clashes with', () => withServer(async (call) => {
  const { status, body } = await call('POST', '/api/series', tuesdays);
  assert.equal(status, 201);
  assert.deepEqual(body.booked.map((b) => b.date), ['2026-12-08', '2026-12-22', '2026-12-29']);
  assert.equal(body.skipped.length, 1);
  assert.equal(body.skipped[0].date, '2026-12-15');
  assert.match(body.skipped[0].reason, /B-1003/);
}));

test('FR-12: series bookings show up in GET /api/bookings with their seriesId', () => withServer(async (call) => {
  const { body: series } = await call('POST', '/api/series', fridays);
  const { body: day } = await call('GET', '/api/bookings?date=2026-12-11');
  const found = day.filter((b) => b.seriesId === series.seriesId);
  assert.equal(found.length, 1);
  assert.equal(found[0].title, 'Design review');
}));

for (const [name, change] of [
  ['weeks above 12', { weeks: 13 }],
  ['weeks below 2', { weeks: 1 }],
  ['weeks not a whole number', { weeks: 'six' }],
  ['more people than the room holds (rule 3)', { attendees: 5 }],
  ['a time that is not on the half hour (rule 3)', { start: '10:15' }],
  ['a Saturday start (rule 4)', { date: '2026-12-05' }],
]) {
  test(`FR-12: 400 and nothing booked for ${name}`, () => withServer(async (call) => {
    const { status, body } = await call('POST', '/api/series', { ...fridays, ...change });
    assert.equal(status, 400);
    assert.equal(typeof body.error, 'string');
    const { body: day } = await call('GET', '/api/bookings?date=2026-12-11');
    assert.equal(day.length, 0, 'a rejected series must not book anything');
  }));
}

test('FR-12 rule 7: no week can be booked -> 409 with the skipped weeks, and nothing saved', () => withServer(async (call) => {
  const { status, body } = await call('POST', '/api/series', { ...fridays, date: '2026-12-25', weeks: 2 });
  assert.equal(status, 409);
  assert.equal(typeof body.error, 'string');
  assert.deepEqual(body.skipped.map((s) => s.date), ['2026-12-25', '2027-01-01']);
}));

test('FR-12 rule 8: cancelling a series cancels every booking in it; a second time is a 404', () => withServer(async (call) => {
  const { body: series } = await call('POST', '/api/series', fridays);
  const cancelled = await call('DELETE', `/api/series/${series.seriesId}`);
  assert.equal(cancelled.status, 200);
  assert.equal(cancelled.body.cancelled, 4);
  const { body: day } = await call('GET', '/api/bookings?date=2026-12-11');
  assert.equal(day.length, 0);
  assert.equal((await call('DELETE', `/api/series/${series.seriesId}`)).status, 404);
  assert.equal((await call('DELETE', '/api/series/S-9999')).status, 404);
}));

test('FR-12 rule 8: one booking of a series can still be cancelled on its own', () => withServer(async (call) => {
  const { body: series } = await call('POST', '/api/series', fridays);
  assert.equal((await call('DELETE', `/api/bookings/${series.booked[1].id}`)).status, 204);
  const cancelled = await call('DELETE', `/api/series/${series.seriesId}`);
  assert.equal(cancelled.body.cancelled, 3);
}));

test('FR-12: the next series gets the next id', () => withServer(async (call) => {
  const first = await call('POST', '/api/series', fridays);
  const second = await call('POST', '/api/series', tuesdays);
  assert.notEqual(first.body.seriesId, second.body.seriesId);
}));

test('FR-12 technical notes: single bookings work exactly as before', () => withServer(async (call) => {
  const single = { roomId: 'kabini', date: '2026-12-09', start: '09:00', end: '10:00', title: 'Pairing', organiser: 'Asha', attendees: 2 };
  const created = await call('POST', '/api/bookings', single);
  assert.equal(created.status, 201);
  assert.equal(created.body.seriesId ?? null, null, 'a single booking has no seriesId');
  const clash = await call('POST', '/api/bookings', { ...single, start: '09:30', end: '10:30' });
  assert.equal(clash.status, 409);
  assert.equal(clash.body.conflictWith, created.body.id);
  assert.equal((await call('DELETE', `/api/bookings/${created.body.id}`)).status, 204);
}));
