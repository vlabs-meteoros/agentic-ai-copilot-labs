'use strict';
// Unit tests for FR-12 (recurring weekly bookings), on a temporary copy of test/fixtures/.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { createStore } = require('../src/store');
const { seriesDates, createSeries, cancelSeries } = require('../src/series');
const { listBookings } = require('../src/bookings');

function tempStore() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kaverirooms-series-'));
  fs.cpSync(path.join(__dirname, 'fixtures'), dir, { recursive: true });
  return createStore(dir);
}

const fridays = { roomId: 'kabini', date: '2026-12-04', start: '10:00', end: '11:00', title: 'Design review', organiser: 'Ananya Iyer', attendees: 4, weeks: 6 };

test('series dates are every 7 days, across a month and a year end', () => {
  assert.deepEqual(seriesDates('2026-12-18', 3), ['2026-12-18', '2026-12-25', '2027-01-01']);
});

test('holidays are skipped with their name, the other weeks are booked', () => {
  const store = tempStore();
  const result = createSeries(store, fridays);
  assert.equal(result.seriesId, 'S-1001');
  assert.deepEqual(result.booked.map((b) => b.date), ['2026-12-04', '2026-12-11', '2026-12-18', '2027-01-08']);
  assert.deepEqual(result.booked.map((b) => b.id), ['B-1010', 'B-1011', 'B-1012', 'B-1013']);
  assert.deepEqual(result.skipped, [
    { date: '2026-12-25', reason: 'holiday: Christmas' },
    { date: '2027-01-01', reason: "holiday: New Year's Day" },
  ]);
});

test('a clash skips that week and names the other booking', () => {
  const result = createSeries(tempStore(), { ...fridays, roomId: 'hemavathi', date: '2026-12-08', start: '14:30', end: '15:30', weeks: 3 });
  assert.deepEqual(result.skipped, [{ date: '2026-12-15', reason: 'conflict with B-1003' }]);
});

test('a bad request books nothing', () => {
  const store = tempStore();
  const before = store.load().bookings.length;
  for (const change of [{ weeks: 13 }, { weeks: 1 }, { attendees: 9 }, { date: '2026-12-06' }]) {
    assert.throws(() => createSeries(store, { ...fridays, ...change }), (error) => error.status === 400);
  }
  assert.equal(store.load().bookings.length, before);
});

test('no free week is a 409 and saves nothing', () => {
  const store = tempStore();
  assert.throws(() => createSeries(store, { ...fridays, date: '2026-12-25', weeks: 2 }),
    (error) => error.status === 409 && error.details.skipped.length === 2);
  assert.equal(store.load().bookings.length, 9);
});

test('cancelling a series removes all its bookings and leaves the others', () => {
  const store = tempStore();
  const { seriesId } = createSeries(store, fridays);
  assert.equal(cancelSeries(store, seriesId), 4);
  assert.equal(listBookings(store, { date: '2026-12-11' }).length, 1); // B-1009 is still there
  assert.throws(() => cancelSeries(store, seriesId), (error) => error.status === 404);
});
