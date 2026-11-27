'use strict';
// FR-12: recurring weekly bookings. A series books the same room, same time, every 7 days, skipping holidays and clashes.

const rules = require('./rules');
const { BookingError, validateBooking, findConflict } = require('./bookings');

const MIN_WEEKS = 2;
const MAX_WEEKS = 12;

/** Add a number of days to a YYYY-MM-DD date. */
function addDays(date, days) {
  const [year, month, day] = date.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day + days)).toISOString().slice(0, 10);
}

/** The dates of a series: the first date, then every 7 days, `weeks` dates in all. */
function seriesDates(firstDate, weeks) {
  return Array.from({ length: weeks }, (_, week) => addDays(firstDate, 7 * week));
}

/** Check a series request (FR-12 rules 2-4). Throws a BookingError (400) on the first problem. */
function validateSeries(input, rooms) {
  if (!input || typeof input !== 'object') throw new BookingError(400, 'Send the series as a JSON object');
  if (!Number.isInteger(input.weeks) || input.weeks < MIN_WEEKS || input.weeks > MAX_WEEKS) {
    throw new BookingError(400, `weeks must be a whole number from ${MIN_WEEKS} to ${MAX_WEEKS}`);
  }
  // Every week gets the single-booking checks, except holidays: a holiday skips that week instead (rule 5)
  validateBooking(input, rooms, []);
}

/** Book a series. Returns { seriesId, booked, skipped }. Throws 400 if the request breaks a rule, 409 if no week is free. */
function createSeries(store, input) {
  const { rooms, holidays, bookings } = store.load();
  validateSeries(input, rooms);

  const seriesId = store.nextSeriesId(bookings);
  const booked = [];
  const skipped = [];
  let all = bookings;
  for (const date of seriesDates(input.date, input.weeks)) {
    const holiday = rules.findHoliday(holidays, date);
    const conflict = holiday ? undefined : findConflict(all, { ...input, date });
    if (holiday) {
      skipped.push({ date, reason: `holiday: ${holiday.name}` });
    } else if (conflict) {
      skipped.push({ date, reason: `conflict with ${conflict.id}` });
    } else {
      const booking = {
        id: store.nextBookingId(all),
        roomId: input.roomId,
        date,
        start: input.start,
        end: input.end,
        title: input.title.trim(),
        organiser: input.organiser.trim(),
        attendees: input.attendees,
        seriesId,
      };
      booked.push(booking);
      all = [...all, booking];
    }
  }

  if (booked.length === 0) {
    throw new BookingError(409, 'None of the weeks could be booked, so nothing was saved', { skipped });
  }
  store.saveBookings(all);
  return { seriesId, booked, skipped };
}

/** Cancel every booking in a series. Returns the number cancelled. Throws a BookingError (404) if there's no such series. */
function cancelSeries(store, seriesId) {
  const { bookings } = store.load();
  const remaining = bookings.filter((b) => b.seriesId !== seriesId);
  const cancelled = bookings.length - remaining.length;
  if (cancelled === 0) throw new BookingError(404, `No series ${seriesId}`);
  store.saveBookings(remaining);
  return cancelled;
}

module.exports = { MIN_WEEKS, MAX_WEEKS, seriesDates, validateSeries, createSeries, cancelSeries };
