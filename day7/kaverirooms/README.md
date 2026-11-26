# KaveriRooms

Meeting-room booking for the Kaveri Systems office in Mysuru: six rooms, one day at a time, booked from the browser or the JSON API.

```powershell
node src/server.js     # then open http://localhost:3000/?date=2026-12-08
node --test            # run the tests
```

Needs Node.js 18 or later. No `npm install`: KaveriRooms uses only Node's built-in modules.

## API

| Method and path | What it does |
|---|---|
| `GET /api/rooms` | The rooms, with capacity, floor and equipment |
| `GET /api/holidays` | Office holidays (no bookings on these days) |
| `GET /api/bookings?date=YYYY-MM-DD&roomId=...` | Bookings for a day (and optionally one room), in room order, then by start time |
| `POST /api/bookings` | Book a room: `{ roomId, date, start, end, title, organiser, attendees }`. 201, 400 (breaks a rule) or 409 (clash) |
| `DELETE /api/bookings/:id` | Cancel a booking: 204, or 404 |

## Booking rules

Monday to Friday, 08:00 to 20:00, start and end on the hour or half hour, not on office holidays (`data/holidays.json`),
no more people than the room holds, and no overlap with another booking in the same room (a meeting can start when the last one ends).

## Files

```
src/rules.js      office rules: times, weekends, holidays, overlaps
src/bookings.js   validate, check for clashes, save, list and cancel bookings
src/store.js      read and write data/*.json
src/server.js     the HTTP API and static files
public/           the browser app
data/             rooms.json, holidays.json, bookings.json
test/             node:test tests
docs/             feature requests
```
