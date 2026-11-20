from datetime import datetime, time, timedelta

O = time(9, 0)
C = time(18, 0)


def _wd(d, h):
    return d.weekday() < 5 and d not in h


def _nxt(t, h):
    while True:
        if not _wd(t.date(), h) or t.time() >= C:
            t = datetime.combine(t.date() + timedelta(days=1), O)
            continue
        if t.time() < O:
            return datetime.combine(t.date(), O)
        return t


def add_bh(t, hrs, h=()):
    h = set(h)
    t = _nxt(t, h)
    left = timedelta(hours=hrs)
    while True:
        end = datetime.combine(t.date(), C)
        if t + left <= end:
            return t + left
        left -= end - t
        t = _nxt(end, h)


def bh_between(a, b, h=()):
    if b <= a:
        return 0.0
    h = set(h)
    tot = timedelta()
    t = _nxt(a, h)
    while t < b:
        end = min(datetime.combine(t.date(), C), b)
        tot += end - t
        t = _nxt(datetime.combine(t.date(), C), h)
    return round(tot.total_seconds() / 3600, 2)
