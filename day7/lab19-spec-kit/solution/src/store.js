'use strict';
// Reads and writes the JSON files in a data folder. KaveriRooms is small, so every request reads the files again.

const fs = require('node:fs');
const path = require('node:path');

/** Read a JSON file, or return fallback if the file doesn't exist. */
function readJson(file, fallback) {
  if (!fs.existsSync(file)) return fallback;
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

/** Write a JSON file in one step: write a temporary file, then rename it, so a crash never leaves half a file. */
function writeJson(file, value) {
  const temporary = `${file}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n', 'utf8');
  fs.renameSync(temporary, file);
}

/** A store for the data folder: rooms.json, holidays.json and bookings.json. */
function createStore(dataDir) {
  const file = (name) => path.join(dataDir, name);
  return {
    dataDir,
    load() {
      return {
        rooms: readJson(file('rooms.json'), []),
        holidays: readJson(file('holidays.json'), []),
        bookings: readJson(file('bookings.json'), []),
      };
    },
    saveBookings(bookings) {
      writeJson(file('bookings.json'), bookings);
    },
    /** The next free id: one more than the highest B-number so far, starting at B-1001. */
    nextBookingId(bookings) {
      const numbers = bookings.map((b) => Number(String(b.id).replace(/^B-/, ''))).filter(Number.isFinite);
      return `B-${Math.max(1000, ...numbers) + 1}`;
    },
    /** The next series id (FR-12): one more than the highest S-number in the bookings so far, starting at S-1001. */
    nextSeriesId(bookings) {
      const numbers = bookings.filter((b) => b.seriesId).map((b) => Number(String(b.seriesId).replace(/^S-/, ''))).filter(Number.isFinite);
      return `S-${Math.max(1000, ...numbers) + 1}`;
    },
  };
}

module.exports = { createStore, readJson, writeJson };
