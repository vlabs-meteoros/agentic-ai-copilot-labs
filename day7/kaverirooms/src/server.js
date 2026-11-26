'use strict';
// The KaveriRooms web server: a JSON API under /api and the browser app from public/. Node.js only, no packages.
//
//   node src/server.js             -> http://localhost:3000
//   $env:PORT=3100; node src/server.js

const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { createStore } = require('./store');
const bookings = require('./bookings');

const DEFAULT_DATA_DIR = path.join(__dirname, '..', 'data');
const PUBLIC_DIR = path.join(__dirname, '..', 'public');
const MAX_BODY_BYTES = 10 * 1024;
const CONTENT_TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8' };

/** Send a JSON response. */
function sendJson(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(body === undefined ? '' : JSON.stringify(body));
}

/** Read the request body and parse it as JSON. Rejects with a 400 BookingError if it isn't JSON. */
function readJsonBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (chunk) => {
      size += chunk.length;
      if (size > MAX_BODY_BYTES) {
        reject(new bookings.BookingError(400, 'Request body is too large'));
        req.destroy();
        return;
      }
      chunks.push(chunk);
    });
    req.on('end', () => {
      try {
        resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}'));
      } catch {
        reject(new bookings.BookingError(400, 'Request body must be JSON'));
      }
    });
    req.on('error', reject);
  });
}

/** Serve a file from public/, or 404. Never serves anything outside public/. */
function serveStatic(res, urlPath) {
  const relative = urlPath === '/' ? 'index.html' : decodeURIComponent(urlPath).replace(/^\/+/, '');
  const file = path.resolve(PUBLIC_DIR, relative);
  if (!file.startsWith(PUBLIC_DIR + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    sendJson(res, 404, { error: 'Not found' });
    return;
  }
  res.writeHead(200, { 'Content-Type': CONTENT_TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
}

/** Create the HTTP server. Pass dataDir to use another data folder (the tests use a temporary copy). */
function createServer({ dataDir = DEFAULT_DATA_DIR } = {}) {
  const store = createStore(dataDir);

  async function handle(req, res) {
    const url = new URL(req.url, 'http://localhost');
    const route = `${req.method} ${url.pathname}`;

    if (route === 'GET /api/rooms') return sendJson(res, 200, store.load().rooms);
    if (route === 'GET /api/holidays') return sendJson(res, 200, store.load().holidays);
    if (route === 'GET /api/bookings') {
      const date = url.searchParams.get('date') || undefined;
      const roomId = url.searchParams.get('roomId') || undefined;
      return sendJson(res, 200, bookings.listBookings(store, { date, roomId }));
    }
    if (route === 'POST /api/bookings') {
      const input = await readJsonBody(req);
      return sendJson(res, 201, bookings.createBooking(store, input));
    }
    const cancel = /^\/api\/bookings\/([A-Za-z0-9-]+)$/.exec(url.pathname);
    if (req.method === 'DELETE' && cancel) {
      bookings.cancelBooking(store, cancel[1]);
      return sendJson(res, 204);
    }
    if (url.pathname.startsWith('/api/')) return sendJson(res, 404, { error: `No route ${route}` });
    if (req.method === 'GET') return serveStatic(res, url.pathname);
    return sendJson(res, 405, { error: 'Method not allowed' });
  }

  return http.createServer((req, res) => {
    handle(req, res).catch((error) => {
      if (error instanceof bookings.BookingError) {
        sendJson(res, error.status, { error: error.message, ...error.details });
      } else {
        console.error(error);
        sendJson(res, 500, { error: 'Something went wrong on the server' });
      }
    });
  });
}

if (require.main === module) {
  const port = Number(process.env.PORT) || 3000;
  createServer().listen(port, () => {
    console.log(`KaveriRooms is running at http://localhost:${port}  (Ctrl+C to stop)`);
  });
}

module.exports = { createServer };
