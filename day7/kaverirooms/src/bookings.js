'use strict';
// Single bookings: validate a request, check it against the room's other bookings, and save it.

const rules = require('./rules');

/** An error the API turns into an HTTP response: status 400 (bad request), 404 (not found) or 409 (conflict). */
class BookingError extends Error {
  constructor(status, message, details = {}) {
    super(message);
    this.name = 'BookingError';
    this.status = status;
    this.details = details;
  }
}

/** Check a booking request against the office rules. Returns the room. Throws a BookingError (400) on the first problem. */
function validateBooking(input, rooms, holidays) {
  if (!input || typeof input !== 'object') throw new BookingError(400, 'Send the booking as a JSON object');
  const room = rooms.find((r) => r.id === input.roomId);
  if (!room) throw new BookingError(400, `Unknown room: ${input.roomId}`);
  if (!rules.isValidDate(input.date)) throw new BookingError(400, 'date must be a real date written as YYYY-MM-DD');
  if (!rules.isValidTime(input.start) || !rules.isValidTime(input.end)) {
    throw new BookingError(400, 'start and end must be times on the hour or half hour, written as HH:MM');
  }
  if (rules.toMinutes(input.start) >= rules.toMinutes(input.end)) throw new BookingError(400, 'end must be after start');
  if (rules.toMinutes(input.start) < rules.toMinutes(rules.OFFICE_OPENS) ||
      rules.toMinutes(input.end) > rules.toMinutes(rules.OFFICE_CLOSES)) {
    throw new BookingError(400, `Bookings must be between ${rules.OFFICE_OPENS} and ${rules.OFFICE_CLOSES}`);
  }
  const title = typeof input.title === 'string' ? input.title.trim() : '';
  if (!title || title.length > rules.MAX_TITLE_LENGTH) {
    throw new BookingError(400, `title is required (at most ${rules.MAX_TITLE_LENGTH} characters)`);
  }
  if (typeof input.organiser !== 'string' || !input.organiser.trim()) throw new BookingError(400, 'organiser is required');
  if (!Number.isInteger(input.attendees) || input.attendees < 1) throw new BookingError(400, 'attendees must be a whole number, 1 or more');
  if (input.attendees > room.capacity) {
    throw new BookingError(400, `${room.name} holds ${room.capacity} people; you asked for ${input.attendees}`);
  }
  if (rules.isWeekend(input.date)) throw new BookingError(400, 'The office is closed at weekends');
  const holiday = rules.findHoliday(holidays, input.date);
  if (holiday) throw new BookingError(400, `The office is closed on ${input.date} (${holiday.name})`);
  return room;
}

/** The existing booking in the same room that overlaps this time slot, or undefined. */
function findConflict(bookings, slot) {
  return bookings.find((b) => b.roomId === slot.roomId && b.date === slot.date && rules.overlaps(b, slot));
}

/** Validate, check for a clash, and save a new booking. Returns the saved booking. */
function createBooking(store, input) {
  const { rooms, holidays, bookings } = store.load();
  validateBooking(input, rooms, holidays);
  const conflict = findConflict(bookings, input);
  if (conflict) {
    throw new BookingError(409, `${input.roomId} is already booked ${conflict.start}-${conflict.end} on ${input.date} (${conflict.id})`,
      { conflictWith: conflict.id });
  }
  const booking = {
    id: store.nextBookingId(bookings),
    roomId: input.roomId,
    date: input.date,
    start: input.start,
    end: input.end,
    title: input.title.trim(),
    organiser: input.organiser.trim(),
    attendees: input.attendees,
  };
  store.saveBookings([...bookings, booking]);
  return booking;
}

/** Bookings for one date (and optionally one room), in room order, then by start time. */
function listBookings(store, { date, roomId } = {}) {
  const { rooms, bookings } = store.load();
  const roomOrder = new Map(rooms.map((room, index) => [room.id, index]));
  return bookings
    .filter((b) => (!date || b.date === date) && (!roomId || b.roomId === roomId))
    .sort((a, b) => (a.date.localeCompare(b.date)) ||
      (roomOrder.get(a.roomId) - roomOrder.get(b.roomId)) ||
      (rules.toMinutes(a.start) - rules.toMinutes(b.start)));
}

/** Delete one booking by id. Throws a BookingError (404) if there's no such booking. */
function cancelBooking(store, id) {
  const { bookings } = store.load();
  const remaining = bookings.filter((b) => b.id !== id);
  if (remaining.length === bookings.length) throw new BookingError(404, `No booking ${id}`);
  store.saveBookings(remaining);
}

module.exports = { BookingError, validateBooking, findConflict, createBooking, listBookings, cancelBooking };
