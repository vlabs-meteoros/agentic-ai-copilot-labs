# Feature: payroll export

**Requested by:** Finance Ops. **Status:** ready to build.

Once a month Finance Ops uploads reimbursements to the payroll system as a CSV file.
Today someone copies the numbers from the report by hand. We want a command that writes the file.

## Command

```text
python -m kavericlaims payroll --month 2026-11                                 # print the CSV
python -m kavericlaims payroll --month 2026-11 --out payroll_2026-11.csv       # also write it to a file
```

## Requirements

1. Use the results of `claims.process()`, so every policy rule (limits, receipts, currency) is applied exactly as in the report.
2. Pay **approved** claims only. Submitted and rejected claims are not paid.
3. One row per employee whose approved claims add up to **more than 0.00** INR reimbursable.
4. Columns, in this order, with this header row: `emp_id,name,cost_centre,claims,amount`
   * `claims`: the number of the employee's approved claims
   * `amount`: the total reimbursable INR of those claims, with exactly 2 decimals and **no** thousands separator (for example `12380.00`)
5. Rows sorted by `emp_id`.
6. After the CSV, print one summary line: `Payroll 2026-11: 8 employees, 40,060.00 INR` (number of rows, total of `amount` with thousands separators).
   When `--out` is given, the file contains the CSV only, without the summary line.
7. Put the logic in a new module `kavericlaims/payroll.py` with a function `build_payroll(results, employees)` that returns the rows.
   The CLI only prints them or writes them.
8. Tests in `tests/test_payroll.py`:
   * submitted and rejected claims are not paid
   * an employee whose approved claims are all reimbursed 0.00 gets no row
   * amounts have 2 decimals and no thousands separator
   * the November 2026 file matches the expected output below

## Expected output for November 2026

```text
emp_id,name,cost_centre,claims,amount
E01,Ananya Rao,CC-ENG,2,800.00
E02,Rahul Menon,CC-ENG,3,1180.00
E05,Meera Kulkarni,CC-SALES,2,4350.00
E07,Nikhil Joshi,CC-OPS,2,12380.00
E08,Rekha Hegde,CC-OPS,1,450.00
E09,Vikram Desai,CC-ENG,2,10500.00
E10,Sneha Patil,CC-SALES,1,1500.00
E12,Deepa Krishnan,CC-EXEC,1,8900.00
Payroll 2026-11: 8 employees, 40,060.00 INR
```
