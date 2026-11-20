# Feature: SLA escalation (KAV-212)

**Requested by:** Service Desk managers  **Status:** ready for development

## Why

Team leads find out about breached tickets too late, usually from an angry email. Once a day, someone
should be able to run one command that hands every ticket in trouble to the team's lead.

## Requirements

1. Add a new command: `python -m kaveridesk escalate`, with an optional `--dry-run` flag.
2. A ticket **needs escalation** when all of these are true:
   * it isn't resolved
   * its SLA state is `AT RISK` or `BREACHED` (the same states the `list` command shows)
   * it hasn't been escalated before
3. Escalating a ticket:
   * assigns it to the **lead** of the ticket's team (the agent with `"lead": true` in `data/agents.json`),
     even if the lead already has `max_open` tickets. If the lead already has the ticket, keep it with them.
   * sets the status to `in_progress`
   * adds this note: `Escalated on <YYYY-MM-DD HH:MM> (SLA <state>, <percent>% used); was assigned to <old agent id or nobody>`
   * marks the ticket as escalated, so it's never escalated twice. Store this in a new ticket field `escalated` (`true` / `false`).
4. Existing `tickets.json` files don't have the `escalated` field. They must still load: a missing field means `false`.
5. With `--dry-run`, print what would happen and **don't save anything**.
6. Output: one line per ticket, sorted by due date, for example:

   ```text
   INC-1003  BREACHED  A05 -> A05
   INC-1009  BREACHED  A02 -> A01
   ```

   then `4 ticket(s) escalated` (or `4 ticket(s) would be escalated` with `--dry-run`).
   If no ticket needs escalation, print `Nothing to escalate.`
7. The `show` command prints `Escalated: yes` for an escalated ticket.
8. Don't change how due dates or SLA states are calculated.

## Tests

Add `tests/test_escalation.py` (same style as `tests/test_service.py`) that checks:

* which tickets get escalated at `2026-11-20 11:00`, and who they're assigned to afterwards
* a dry run saves nothing
* running escalation twice escalates nothing the second time
* a `tickets.json` without the `escalated` field still loads
