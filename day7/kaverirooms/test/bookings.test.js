'use strict';
// Unit tests for the booking rules. Each test gets its own copy of the data folder.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const rules = require('../src/rules');
const { createStore } = require('../src/store');
const { createBooking, listBookings, cancelBooking, BookingError } = require('../src/bookings');

/** A store on a temporary copy of test/fixtures/ (the original data, so your own bookings don't change the results). */
function tempStore() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'kaverirooms-'));
  fs.cpSync(path.join(__dirname, 'fixtures'), dir, { recursive: true });
  return createStore(dir);
}

const valid = { roomId: 'kabini', date: '2026-12-09', start: '10:00', end: '11:00', title: 'Pairing', organiser: 'Asha', attendees: 2 };

test('times convert to minutes since midnight', () => {
  assert.equal(rules.toMinutes('00:00'), 0);
  assert.equal(rules.toMinutes('09:30'), 570);
  assert.equal(rules.toMinutes('20:00'), 1200);
});

test('end times are exclusive, so back-to-back bookings do not overlap', () => {
  assert.equal(rules.overlaps({ start: '09:00', end: '10:00' }, { start: '10:00', end: '11:00' }), false);
  assert.equal(rules.overlaps({ start: '09:00', end: '10:30' }, { start: '10:00', end: '11:00' }), true);
  assert.equal(rules.overlaps({ start: '09:00', end: '12:00' }, { start: '10:00', end: '11:00' }), true);
});

test('dates must be real dates', () => {
  assert.equal(rules.isValidDate('2026-12-09'), true);
  assert.equal(rules.isValidDate('2026-02-30'), false);
  assert.equal(rules.isValidDate('09-12-2026'), false);
});

test('a valid booking is saved with the next id', () => {
  const store = tempStore();
  const booking = createBooking(store, valid);
  assert.equal(booking.id, 'B-1010');
  assert.deepEqual(listBookings(store, { date: '2026-12-09', roomId: 'kabini' }).map((b) => b.id), ['B-1010']);
});

test('an overlapping booking in the same room is a 409 that names the other booking', () => {
  const store = tempStore();
  assert.throws(() => createBooking(store, { ...valid, roomId: 'hemavathi', date: '2026-12-15', start: '14:30', end: '15:30' }),
    (error) => error instanceof BookingError && error.status === 409 && error.details.conflictWith === 'B-1003');
});

test('the same time in another room is fine', () => {
  const store = tempStore();
  const booking = createBooking(store, { ...valid, roomId: 'shimsha', date: '2026-12-15', start: '14:30', end: '15:30' });
  assert.equal(booking.roomId, 'shimsha');
});

for (const [name, change, message] of [
  ['unknown room', { roomId: 'nethravathi' }, /Unknown room/],
  ['too many people', { attendees: 5 }, /holds 4 people/],
  ['weekend', { date: '2026-12-12' }, /weekends/],
  ['holiday', { date: '2026-12-25' }, /Christmas/],
  ['before opening time', { start: '07:30', end: '08:30' }, /between 08:00 and 20:00/],
  ['quarter-hour start', { start: '10:15' }, /half hour/],
  ['end before start', { start: '11:00', end: '10:00' }, /after start/],
  ['missing title', { title: '  ' }, /title is required/],
]) {
  test(`rejects a booking: ${name}`, () => {
    assert.throws(() => createBooking(tempStore(), { ...valid, ...change }),
      (error) => error instanceof BookingError && error.status === 400 && message.test(error.message));
  });
}

test('cancelling removes the booking; cancelling twice is a 404', () => {
  const store = tempStore();
  cancelBooking(store, 'B-1009');
  assert.equal(listBookings(store, { date: '2026-12-11' }).length, 0);
  assert.throws(() => cancelBooking(store, 'B-1009'), (error) => error.status === 404);
});
