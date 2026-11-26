'use strict';
// Booking rules for the Mysuru office. Facilities owns these numbers: change them here, nowhere else.

const OFFICE_OPENS = '08:00';
const OFFICE_CLOSES = '20:00';
const MAX_TITLE_LENGTH = 60;

const DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const TIME_PATTERN = /^([01]\d|2[0-3]):(00|30)$/; // bookings start and end on the hour or half hour

/** Minutes since midnight for "HH:MM", e.g. "09:30" -> 570. */
function toMinutes(time) {
  const [hours, minutes] = time.split(':').map(Number);
  return hours * 60 + minutes;
}

/** True if text is a real calendar date written as YYYY-MM-DD. */
function isValidDate(text) {
  const match = DATE_PATTERN.exec(String(text));
  if (!match) return false;
  const [, year, month, day] = match.map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

/** True if text is a time on the hour or half hour, written as HH:MM. */
function isValidTime(text) {
  return TIME_PATTERN.test(String(text));
}

/** Day of the week for a YYYY-MM-DD date: 0 = Sunday ... 6 = Saturday. */
function weekday(date) {
  const [year, month, day] = date.split('-').map(Number);
  return new Date(Date.UTC(year, month - 1, day)).getUTCDay();
}

/** True if the date falls on a Saturday or Sunday. */
function isWeekend(date) {
  const day = weekday(date);
  return day === 0 || day === 6;
}

/** The holiday on this date ({date, name}), or undefined. */
function findHoliday(holidays, date) {
  return holidays.find((holiday) => holiday.date === date);
}

/** True if two time ranges on the same day overlap. End times are exclusive: 09:00-10:00 and 10:00-11:00 don't overlap. */
function overlaps(a, b) {
  return toMinutes(a.start) < toMinutes(b.end) && toMinutes(b.start) < toMinutes(a.end);
}

module.exports = {
  OFFICE_OPENS,
  OFFICE_CLOSES,
  MAX_TITLE_LENGTH,
  toMinutes,
  isValidDate,
  isValidTime,
  weekday,
  isWeekend,
  findHoliday,
  overlaps,
};
