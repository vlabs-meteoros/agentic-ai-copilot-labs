Feature: Possible duplicate claims
  Finance Ops wants to see claims that might be the same expense claimed twice,
  so that a person checks them before the month is paid.

  Background:
    Given these claims by employee E01
      | claim | category | amount | currency | date       | status   |
      | C-1   | TRAVEL   | 380.00 | INR      | 2026-09-08 | approved |

  Scenario: The same taxi claimed again two days later
    When E01 also claims "C-2" for TRAVEL 380.00 INR on 2026-09-10
    Then Finance Ops sees the pair "C-1" and "C-2"

  Scenario: Four days apart is not a duplicate
    When E01 also claims "C-2" for TRAVEL 380.00 INR on 2026-09-12
    Then Finance Ops sees no pairs

  Scenario: A rejected claim is never part of a pair
    Given claim "C-1" was rejected
    When E01 also claims "C-2" for TRAVEL 380.00 INR on 2026-09-09
    Then Finance Ops sees no pairs
