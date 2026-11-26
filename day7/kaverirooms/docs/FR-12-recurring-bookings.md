# FR-12: Recurring weekly bookings

| | |
|---|---|
| **Requested by** | Meera Hegde, Facilities (Mysuru office) |
| **Product owner** | Deepa Rao |
| **Priority** | High: teams are re-booking the same room by hand every week, and losing it to whoever books first |

## What Facilities asked for

> "Most of our bookings are the same meeting every week: stand-ups, 1:1s, the Thursday design review. People book them one at a time,
> forget a week, and lose the room. We want to book a room **every week, same day, same time, for a number of weeks**, in one go.
> If one of the weeks can't be booked, that shouldn't stop the others: book what you can and tell me which weeks were skipped and why.
> When the meeting ends early (a project finishes), the organiser should be able to cancel the whole series at once."

## Rules agreed with Facilities

1. A series repeats **every 7 days** from the first date, at the same start and end time, in the same room.
2. The number of weeks is **from 2 to 12**, including the first week.
3. Every occurrence follows the same rules as a single booking today (office hours, half-hour times, title, organiser, room capacity).
   If the request breaks one of these rules, **nothing is booked**.
4. A series can't start on a Saturday or Sunday (the office is closed, so every week would be closed).
5. A week that falls on an **office holiday** is skipped. The reason says which holiday, for example `holiday: Christmas`.
6. A week where the room is **already booked** at an overlapping time is skipped. The reason names the booking it clashes with, for example `conflict with B-1003`.
7. The other weeks are still booked. If **no** week can be booked, nothing is saved and the request fails.
8. Cancelling a series cancels **every** booking in it. Single bookings in the series can still be cancelled one at a time, as today.
9. In the day view, a booking that belongs to a series is marked so people can tell it repeats.

## Technical notes (from the tech lead)

The front end and the bots that book rooms both use the JSON API, so the API is fixed:

* `POST /api/series` with the same fields as `POST /api/bookings` plus `weeks` (a whole number):

  ```json
  { "roomId": "kabini", "date": "2026-12-04", "start": "10:00", "end": "11:00",
    "title": "Design review", "organiser": "Ananya Iyer", "attendees": 4, "weeks": 6 }
  ```

  * **201** when at least one week was booked:

    ```json
    { "seriesId": "S-1001",
      "booked":  [ { "id": "B-1010", "roomId": "kabini", "date": "2026-12-04", "start": "10:00", "end": "11:00", "title": "Design review",
                     "organiser": "Ananya Iyer", "attendees": 4, "seriesId": "S-1001" } ],
      "skipped": [ { "date": "2026-12-25", "reason": "holiday: Christmas" } ] }
    ```

  * **400** `{ "error": "..." }` when the request breaks a rule (3 or 4, or `weeks` outside 2-12). Nothing is booked.
  * **409** `{ "error": "...", "skipped": [ ... ] }` when no week could be booked. Nothing is booked.
* `DELETE /api/series/:seriesId` cancels every booking in the series: **200** `{ "cancelled": 4 }`, or **404** if there's no such series.
* Series ids are `S-1001`, `S-1002`, ... Booking ids carry on from the single bookings (`B-1010`, `B-1011`, ...).
* Each booking in a series is stored in `data/bookings.json` like any other booking, with an extra `seriesId` field. No new data file.
* `POST /api/bookings`, `GET /api/bookings` and `DELETE /api/bookings/:id` must keep working exactly as they do now.
* `src/server.js` must keep exporting `createServer({ dataDir })`: the tests start the server with a temporary data folder.

## Out of scope

Daily or monthly repeats, editing a series after it's booked, e-mail invitations.
