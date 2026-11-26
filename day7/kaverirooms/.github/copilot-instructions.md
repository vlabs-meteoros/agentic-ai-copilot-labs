# KaveriRooms: instructions for GitHub Copilot

## About the project
- KaveriRooms is the meeting-room booking app for the Kaveri Systems office in Mysuru: a Node.js JSON API plus a small browser app.
- `src/rules.js` holds the office rules (opening hours, half-hour times, weekends, holidays, overlaps). `src/bookings.js` validates,
  checks for clashes and saves single bookings. `src/store.js` reads and writes the JSON files in `data/`. `src/server.js` is the HTTP API.
- `public/` is the browser app (plain HTML, CSS and JavaScript, no framework, no build step).
- Feature requests are in `docs/`. Spec Kit feature specs, plans and tasks are in `specs/`.

## Running things (Windows, PowerShell)
- Run the tests: `node --test`. Run them after every change, and fix failures before you finish.
- Start the app: `node src/server.js`, then open http://localhost:3000. Stop it with Ctrl+C before you run it again.

## Rules for code
- Node.js 18 or later, CommonJS modules (`require` and `module.exports`, not `import`/`export`), `'use strict';` at the top of each file.
- No npm packages, in the server or in the browser. Use Node's built-in modules (`node:http`, `node:fs`, `node:test`, `node:assert/strict`).
- Tests use `node:test` and live in `test/` as `*.test.js`. Tests never touch `data/`: they copy `test/fixtures/` (the original data)
  to a temporary folder first (see `tempStore()` in `test/bookings.test.js` and `startServer()` in `test/server.test.js`).
- API errors are `BookingError(status, message, details)` from `src/bookings.js`; the server turns them into `{ "error": "..." }` responses.
- Keep the existing API (`/api/rooms`, `/api/holidays`, `/api/bookings`) and its responses unchanged unless a spec says otherwise.
- Never edit `data/rooms.json` or `data/holidays.json`. Give every new function a one-line JSDoc comment.
