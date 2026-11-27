// KaveriRooms browser app: draws the day grid and talks to the JSON API. Plain JavaScript, no framework.
'use strict';

const SLOT_MINUTES = 30;
const DAY_START = 8 * 60;   // 08:00
const DAY_END = 20 * 60;    // 20:00

const state = { rooms: [], holidays: [], day: new Date().toISOString().slice(0, 10) };
const $ = (selector) => document.querySelector(selector);

/** "HH:MM" for minutes since midnight. */
function toTime(minutes) {
  return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`;
}

/** Minutes since midnight for "HH:MM". */
function toMinutes(time) {
  const [h, m] = time.split(':').map(Number);
  return h * 60 + m;
}

/** Add days to a YYYY-MM-DD date. */
function addDays(date, days) {
  const d = new Date(`${date}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Call the API. Resolves with the parsed JSON (or null for 204); rejects with the server's error message. */
async function api(method, url, body) {
  const response = await fetch(url, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function showMessage(text, kind) {
  const message = $('#message');
  message.textContent = text;
  message.className = kind;
}

/** Draw the grid for state.day: one row per room, one column per half hour. */
async function drawDay() {
  $('#day').value = state.day;
  const weekday = new Date(`${state.day}T00:00:00Z`).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' });
  $('#day-title').textContent = `Bookings for ${weekday}`;

  const holiday = state.holidays.find((h) => h.date === state.day);
  const closed = $('#closed');
  closed.hidden = !holiday;
  closed.textContent = holiday ? `Office closed: ${holiday.name}` : '';

  const bookings = await api('GET', `/api/bookings?date=${state.day}`);
  const slots = [];
  for (let m = DAY_START; m < DAY_END; m += SLOT_MINUTES) slots.push(m);

  const head = `<thead><tr><th class="room"></th>${slots.map((m) => `<th>${m % 60 === 0 ? toTime(m) : ''}</th>`).join('')}</tr></thead>`;
  const rows = state.rooms.map((room) => {
    const cells = [];
    let minute = DAY_START;
    while (minute < DAY_END) {
      const booking = bookings.find((b) => b.roomId === room.id && toMinutes(b.start) === minute);
      if (booking) {
        const span = (toMinutes(booking.end) - toMinutes(booking.start)) / SLOT_MINUTES;
        const label = `${booking.seriesId ? '\u21bb ' : ''}${booking.title} (${booking.organiser}, ${booking.attendees})`;
        const tip = `${booking.id}${booking.seriesId ? ` (weekly series ${booking.seriesId})` : ''} ${booking.start}-${booking.end}: ${label}`;
        cells.push(`<td class="booking${booking.seriesId ? ' series' : ''}" colspan="${span}" data-id="${booking.id}" data-series="${booking.seriesId || ''}" title="${escapeHtml(tip)}">${escapeHtml(label)}</td>`);
        minute = toMinutes(booking.end);
      } else {
        cells.push('<td></td>');
        minute += SLOT_MINUTES;
      }
    }
    return `<tr><th class="room">${escapeHtml(room.name)}<small>${room.capacity} people, floor ${room.floor}</small></th>${cells.join('')}</tr>`;
  });
  $('#grid').innerHTML = `${head}<tbody>${rows.join('')}</tbody>`;
}

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/** Fill the form's room and time drop-downs. */
function fillForm() {
  const form = $('#booking-form');
  form.roomId.innerHTML = state.rooms.map((r) => `<option value="${r.id}">${escapeHtml(r.name)} (${r.capacity})</option>`).join('');
  const times = [];
  for (let m = DAY_START; m <= DAY_END; m += SLOT_MINUTES) times.push(toTime(m));
  form.start.innerHTML = times.slice(0, -1).map((t) => `<option>${t}</option>`).join('');
  form.end.innerHTML = times.slice(1).map((t) => `<option>${t}</option>`).join('');
  form.start.value = '09:00';
  form.end.value = '10:00';
  form.date.value = state.day;
}

async function onSubmit(event) {
  event.preventDefault();
  const form = event.target;
  const input = {
    roomId: form.roomId.value,
    date: form.date.value,
    start: form.start.value,
    end: form.end.value,
    title: form.title.value,
    organiser: form.organiser.value,
    attendees: Number(form.attendees.value),
  };
  const weeks = Number(form.weeks.value);
  try {
    if (weeks > 1) {
      const result = await api('POST', '/api/series', { ...input, weeks });
      showMessage(seriesSummary(result, weeks), 'ok');
    } else {
      const booking = await api('POST', '/api/bookings', input);
      showMessage(`Booked ${booking.id}: ${booking.roomId}, ${booking.date} ${booking.start}-${booking.end}`, 'ok');
    }
    state.day = input.date;
    await drawDay();
  } catch (error) {
    showMessage(error.message, 'error');
  }
}

/** "Booked 4 of 6 weeks (series S-1001). Skipped: 2026-12-25 (holiday: Christmas), ..." */
function seriesSummary(result, weeks) {
  const skipped = result.skipped.map((s) => `${s.date} (${s.reason})`).join(', ');
  return `Booked ${result.booked.length} of ${weeks} weeks (series ${result.seriesId}).${skipped ? ` Skipped: ${skipped}` : ''}`;
}

async function onGridClick(event) {
  const cell = event.target.closest('td.booking');
  if (!cell) return;
  const seriesId = cell.dataset.series;
  try {
    if (seriesId && confirm(`${cell.dataset.id} is part of weekly series ${seriesId}.\n\nOK: cancel EVERY week of the series.\nCancel: decide about this day only.`)) {
      const { cancelled } = await api('DELETE', `/api/series/${seriesId}`);
      showMessage(`Cancelled series ${seriesId} (${cancelled} bookings)`, 'ok');
      await drawDay();
      return;
    }
    if (!confirm(`Cancel booking ${cell.dataset.id}?\n\n${cell.title}`)) return;
    await api('DELETE', `/api/bookings/${cell.dataset.id}`);
    showMessage(`Cancelled ${cell.dataset.id}`, 'ok');
    await drawDay();
  } catch (error) {
    showMessage(error.message, 'error');
  }
}

async function start() {
  const params = new URLSearchParams(location.search);
  if (params.get('date')) state.day = params.get('date');
  [state.rooms, state.holidays] = await Promise.all([api('GET', '/api/rooms'), api('GET', '/api/holidays')]);
  fillForm();
  $('#booking-form').addEventListener('submit', onSubmit);
  $('#grid').addEventListener('click', onGridClick);
  $('#day').addEventListener('change', (e) => { state.day = e.target.value; drawDay(); });
  $('#prev-day').addEventListener('click', () => { state.day = addDays(state.day, -1); drawDay(); });
  $('#next-day').addEventListener('click', () => { state.day = addDays(state.day, 1); drawDay(); });
  await drawDay();
}

start().catch((error) => showMessage(`Can't reach the KaveriRooms server: ${error.message}`, 'error'));
