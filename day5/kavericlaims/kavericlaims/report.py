# report.py - the monthly claims report for Finance Ops


def commas(x):
    # 1234567.5 -> "1,234,567.50"
    s = "%.2f" % x
    whole = s.split(".")[0]
    frac = s.split(".")[1]
    neg = False
    if whole.startswith("-"):
        neg = True
        whole = whole[1:]
    out = ""
    i = 0
    for ch in reversed(whole):
        if i > 0 and i % 3 == 0:
            out = "," + out
        out = ch + out
        i = i + 1
    if neg:
        out = "-" + out
    return out + "." + frac


def build_report(res, emps, month):
    s = ""
    s = s + "KAVERI SYSTEMS - EXPENSE CLAIMS REPORT - " + month + "\n"
    s = s + "=" * 78 + "\n"
    s = s + "%-7s %-4s %-16s %-9s %12s %12s  %s\n" % ("CLAIM", "EMP", "NAME", "CATEGORY", "CLAIMED", "REIMBURSE", "FLAGS")
    for r in res:
        name = ""
        for k in emps.keys():
            if k == r["emp"]:
                name = emps[k][0]
        flags = ""
        for f in r["flags"]:
            if flags != "":
                flags = flags + " "
            flags = flags + f
        line = "%-7s %-4s %-16s %-9s %12s %12s  %s" % (r["id"], r["emp"], name, r["cat"], commas(r["claimed"]), commas(r["reimb"]), flags)
        s = s + line.rstrip() + "\n"
    s = s + "-" * 78 + "\n"
    s = s + "TOTALS BY EMPLOYEE (highest reimbursement first)\n"
    rows = []
    for k in emps.keys():
        tc = 0.0
        tr = 0.0
        n = 0
        for r in res:
            if r["emp"] == k:
                tc = tc + r["claimed"]
                tr = tr + r["reimb"]
                n = n + 1
        if n > 0:
            rows.append([k, emps[k][0], n, tc, tr])
    # sort: highest reimbursable first, then by employee id (selection sort)
    for i in range(len(rows)):
        m = i
        for j in range(i + 1, len(rows)):
            if rows[j][4] > rows[m][4] or (rows[j][4] == rows[m][4] and rows[j][0] < rows[m][0]):
                m = j
        tmp = rows[i]
        rows[i] = rows[m]
        rows[m] = tmp
    for row in rows:
        s = s + "%-4s %-16s %3d claim(s)  claimed %12s  reimbursable %12s\n" % (row[0], row[1], row[2], commas(row[3]), commas(row[4]))
    s = s + "-" * 78 + "\n"
    total_c = 0.0
    total_r = 0.0
    for r in res:
        total_c = total_c + r["claimed"]
        total_r = total_r + r["reimb"]
    flagged = 0
    for r in res:
        if len(r["flags"]) > 0:
            flagged = flagged + 1
    s = s + "Claims: %d   Flagged: %d\n" % (len(res), flagged)
    s = s + "Claimed: %s   Reimbursable: %s   Not reimbursed: %s\n" % (commas(total_c), commas(total_r), commas(total_c - total_r))
    return s
