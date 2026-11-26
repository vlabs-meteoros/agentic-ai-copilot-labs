# KA-102: Warranty report

| | |
|---|---|
| **From** | Sneha Patil, People team (Bengaluru), for the yearly hardware budget |
| **Size** | Medium |

## Why

> "Every December we find out which laptops are out of warranty when they break. I want a list of warranties that have **ended**, and the ones that
> end **soon**, so we can extend them or plan replacements."

## Rules

1. A warranty ends `warranty_months` after the purchase date, on the same day of the month. If that day doesn't exist in the end month,
   it ends on the last day of that month: `2024-02-29` + 36 months = `2027-02-28`.
2. **Expired**: the warranty ended **before** today. **Expiring**: it ends from today up to and including today + N days (default N = 60).
   A warranty that ends today is *expiring*, not expired.
3. Retired assets are left out.
4. Each section is sorted by end date, then by asset id.
5. Where the asset is: `with <name> (<emp id>)` when assigned, `in stock (<city>)` when in stock, `in repair` when in repair.
6. Days: `today`, `in 1 day`, `in 9 days`, `1 day ago`, `21 days ago`.
7. An empty section prints `- none`. A negative `--within` is an error (exit code 1).

## Command

```text
python -m kaveriassets warranty [--within DAYS] [--today YYYY-MM-DD]
```

`--today` defaults to today's date. It's there so the report (and the tests) can be run for any date.

## Example

```text
> python -m kaveriassets warranty --today 2026-12-01
Warranty report on 2026-12-01

Expired (4)
- KA-L004 Apple MacBook Air M2: ended 2025-03-05 (636 days ago), in repair
- KA-M004 Dell P2423D: ended 2026-06-30 (154 days ago), in stock (Bengaluru)
- KA-L003 Lenovo ThinkPad T14 Gen 3: ended 2026-11-10 (21 days ago), with Arjun Menon (E04)
- KA-P001 Samsung Galaxy A55: ended 2026-11-20 (11 days ago), with Farhan Sheikh (E06)

Expiring in the next 60 days (8)
- KA-H001 Jabra Evolve2 65: ends 2026-12-01 (today), with Rahul Verma (E02)
- KA-H002 Jabra Evolve2 65: ends 2026-12-01 (today), in stock (Mysuru)
- KA-L010 Apple MacBook Pro 14 M3: ends 2026-12-10 (in 9 days), with Kavya Shetty (E05)
- KA-L001 Lenovo ThinkPad T14 Gen 3: ends 2026-12-15 (in 14 days), with Ananya Iyer (E01)
- KA-M001 Dell P2423D: ends 2026-12-31 (in 30 days), with Ananya Iyer (E01)
- KA-P003 Samsung Galaxy A55: ends 2027-01-05 (in 35 days), with Ravi Kumar (E09)
- KA-P002 Apple iPhone 15: ends 2027-01-10 (in 40 days), in stock (Bengaluru)
- KA-L002 Dell Latitude 5440: ends 2027-01-20 (in 50 days), with Rahul Verma (E02)
```

With `--within 10`, the second heading is `Expiring in the next 10 days (3)` and lists only KA-H001, KA-H002 and KA-L010.

## Done when

* The example prints exactly that (a test compares the whole text).
* The end-date rule has its own tests, including 29 February and a year end.
