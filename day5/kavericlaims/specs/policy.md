# Kaveri Systems Expense Policy (v3, April 2025)

Owner: Finance Ops. This policy is the source of truth for how much of a claim is reimbursed.
If the KaveriClaims app and this policy disagree, **the policy is right** and the app has a bug.

## 1. Grades and categories

* Every employee has a grade: **G1** (Associate), **G2** (Senior), **G3** (Lead) or **G4** (Director).
* Every claim has one category: **MEAL**, **HOTEL**, **TRAVEL**, **INTERNET** or **OTHER**.
* Claimable meals are food and non-alcoholic drinks eaten during business travel or a client meeting.
  Groceries, gifts and food bought to take home are **not** claimable. When only some lines of a receipt are claimable,
  claim those lines plus their share of the tax on the receipt.

## 2. City tiers

* **Tier 1**: Bengaluru, Chennai, Delhi, Hyderabad, Kolkata, Mumbai, Pune.
* **Tier 2**: every other city in India.
* A claim in a **foreign currency** is an overseas claim and uses the **Tier 1** limits.

## 3. Currency

* Claims in USD, AED or SGD are converted to INR at the rate for the **claim's month** in `data/fx_rates.json`.
* The INR amount is rounded to 2 decimals (paise). All limits and thresholds below apply to the INR amount.

## 4. Limits

| Category | Limit |
|---|---|
| MEAL | Per employee **per day**, all meal claims of that day together (table A) |
| HOTEL | Per **night**: the nightly limit (table B) times the number of nights (`qty`) |
| TRAVEL | No limit |
| INTERNET | ₹1,000 per employee **per calendar month**, all internet claims of that month together |
| OTHER | ₹2,000 per claim |

**Table A: meal limit per day (INR)**

| Grade | Tier 1 | Tier 2 |
|---|---|---|
| G1 | 600 | 450 |
| G2 | 800 | 600 |
| G3 | 1,000 | 800 |
| G4 | 1,500 | 1,200 |

**Table B: hotel limit per night (INR)**

| Grade | Tier 1 | Tier 2 |
|---|---|---|
| G1 | 3,000 | 2,000 |
| G2 | 4,000 | 3,000 |
| G3 | 6,000 | 4,500 |
| G4 | 9,000 | 7,000 |

The reimbursable amount is the claimed INR amount, capped at what is left of the limit. If anything is cut, the claim gets the flag **OVER_LIMIT**.
When a limit is shared (meals per day, internet per month), claims use it up **in claim ID order**.

## 5. Receipts

* A claim of **₹500 or more** needs a receipt. Without one, nothing is reimbursed and the claim gets the flag **NO_RECEIPT**.
* A claim with no receipt and no reimbursement does not use up any shared limit.
* Claims under ₹500 don't need a receipt.

## 6. Claim status

* A claim is `submitted`, `approved` or `rejected`.
* **Rejected** claims are ignored completely: they are not reported and don't use up any limit.
* Only **approved** claims are paid through payroll.

## 7. Examples

All examples are in November 2026, have a receipt unless the table says otherwise, and are the employee's only claim unless the table says otherwise.

| # | Grade | City | Claim | Receipt | Reimbursable (INR) | Flags |
|---|---|---|---|---|---|---|
| 1 | G2 | Bengaluru | MEAL 650.00 | yes | 650.00 | |
| 2 | G2 | Mysuru | MEAL 650.00 | yes | 600.00 | OVER_LIMIT |
| 3 | G3 | Mysuru | MEAL 750.00 | yes | 750.00 | |
| 4 | G1 | Pune | MEAL 499.99 | no | 499.99 | |
| 5 | G1 | Pune | MEAL 500.00 | no | 0.00 | NO_RECEIPT |
| 6 | G2 | Bengaluru | Two MEAL claims on the same day: 450.00, then 500.00 | yes | 450.00, then 350.00 | second: OVER_LIMIT |
| 7 | G2 | Dubai | MEAL AED 100.00 (INR 2,293.00) | yes | 800.00 | OVER_LIMIT |
| 8 | G3 | Hyderabad | HOTEL 13,000.00 for 2 nights | yes | 12,000.00 | OVER_LIMIT |
| 9 | G1 | Mysuru | Two INTERNET claims in the month: 700.00, then 600.00 | yes | 700.00, then 300.00 | second: OVER_LIMIT |
| 10 | G2 | Mumbai | TRAVEL 4,800.00 | yes | 4,800.00 | |
| 11 | G1 | Mangaluru | TRAVEL 820.00 | no | 0.00 | NO_RECEIPT |
| 12 | G3 | Chennai | OTHER 2,450.00 | yes | 2,000.00 | OVER_LIMIT |
| 13 | G2 | Bengaluru | MEAL 300.00, status `rejected` | yes | not reported | |
