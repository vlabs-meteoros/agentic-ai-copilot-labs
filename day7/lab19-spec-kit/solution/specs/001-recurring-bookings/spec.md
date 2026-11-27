# Feature Specification: Recurring Weekly Bookings

**Feature Branch**: `001-recurring-bookings`

**Created**: 2026-11-23

**Status**: Ready for planning

**Input**: User description: "Implement the feature request in docs/FR-12-recurring-bookings.md"

> Reference example for Lab 19. Your spec will be worded differently: compare the **content** (stories, rules, edge cases, measurable outcomes), not the words.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Book the same room every week in one go (Priority: P1)

An organiser books a room for the same day and time every week for a number of weeks (2 to 12), instead of booking each week by hand.

**Why this priority**: This is the whole reason for the request: teams lose their regular room when they forget to re-book it.

**Independent Test**: Book a 6-week series for a free room and time; every week appears in the day view and in `GET /api/bookings` for its date.

**Acceptance Scenarios**:

1. **Given** Kabini is free on Fridays 10:00-11:00, **When** the organiser books it weekly for 6 weeks from 2026-12-04, **Then** the weeks without a holiday are booked, each with the same series id.
2. **Given** a series was booked, **When** anyone views one of its days, **Then** that booking is marked as part of a weekly series.

---

### User Story 2 - Skip the weeks that can't be booked, and say why (Priority: P1)

If a week falls on an office holiday or clashes with an existing booking, that week is skipped and the others are still booked.

**Why this priority**: Without it, one busy week would block the whole series (Facilities' main complaint about the alternatives).

**Independent Test**: Book a series that crosses 25 December, or one that overlaps B-1003; the response lists the booked weeks and the skipped weeks with a reason each.

**Acceptance Scenarios**:

1. **Given** 2026-12-25 is the Christmas holiday, **When** a Friday series includes that date, **Then** it is skipped with the reason `holiday: Christmas`.
2. **Given** B-1003 holds Hemavathi on 2026-12-15 14:00-15:00, **When** a Tuesday series asks for 14:30-15:30, **Then** 2026-12-15 is skipped with the reason `conflict with B-1003`, and the other Tuesdays are booked.
3. **Given** every week of a request is a holiday or a clash, **When** it is submitted, **Then** nothing is saved and the organiser is told no week could be booked (409).

---

### User Story 3 - Cancel a whole series (Priority: P2)

When a regular meeting ends, the organiser cancels every week of the series at once. One week can still be cancelled on its own.

**Why this priority**: Frees rooms for others; less urgent than booking, because single cancellation already works.

**Independent Test**: Book a series, cancel it by series id, and check none of its weeks remain; cancelling again reports "not found".

**Acceptance Scenarios**:

1. **Given** a series with 4 bookings, **When** the organiser cancels the series, **Then** all 4 are removed and the response says 4 were cancelled.
2. **Given** one week of a series was cancelled on its own, **When** the series is cancelled, **Then** the remaining 3 are removed.

---

### Edge Cases

- A series that crosses a month or a year end (2026-12-25 → 2027-01-01) still repeats every 7 days.
- `weeks` of 1, 13, or not a whole number is rejected (400); nothing is booked.
- A series starting on a Saturday or Sunday is rejected (400): every week would be a weekend.
- A request that breaks a single-booking rule (capacity, times, missing title) is rejected as a whole, even if only one week would be affected.
- A clash on one week does not shorten the series: the series still covers the same number of calendar weeks.
- Cancelling an unknown series id reports "not found" (404).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST let an organiser book a room weekly for 2 to 12 weeks, starting on a given date, at a fixed start and end time.
- **FR-002**: Every week MUST meet the same rules as a single booking (office hours, half-hour times, title, organiser, room capacity); if the request breaks one, nothing is booked.
- **FR-003**: The system MUST reject a series that starts on a Saturday or Sunday.
- **FR-004**: The system MUST skip a week on an office holiday, with the reason `holiday: <holiday name>`.
- **FR-005**: The system MUST skip a week that overlaps an existing booking in the same room, with the reason `conflict with <booking id>`.
- **FR-006**: The system MUST book all other weeks, and MUST NOT save anything if no week can be booked.
- **FR-007**: Each booking in a series MUST carry the series id; series ids are `S-1001`, `S-1002`, ...
- **FR-008**: The system MUST let an organiser cancel every booking of a series at once, and still allow single bookings of a series to be cancelled.
- **FR-009**: The day view MUST mark bookings that belong to a series.
- **FR-010**: The existing single-booking API MUST keep working unchanged (`POST`/`GET /api/bookings`, `DELETE /api/bookings/:id`).

### Key Entities

- **Booking**: one room, one date, start and end time, title, organiser, attendees; optionally the series it belongs to.
- **Series**: a group of bookings created by one request, identified by its series id. It exists only through its bookings (no separate record).
- **Skipped week**: a date from the request that was not booked, and the reason.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An organiser books a 12-week series in one request, instead of 12.
- **SC-002**: Every request either books what it can and lists each skipped week with a reason, or books nothing and says why: never a silent partial result.
- **SC-003**: All existing single-booking tests still pass unchanged.
- **SC-004**: Cancelling a series leaves none of its bookings behind.

## Assumptions

- Holidays come from `data/holidays.json`; there are no per-room closures.
- A series is not edited after booking (out of scope in FR-12); to change it, cancel it and book again.
- Series ids are worked out from the bookings saved so far, so if every booking of the newest series is cancelled, its id can be used again.
