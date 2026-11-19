# leave report
import datetime


def f(d):
    r = []
    for x in d:
        a = 21
        if x[2] > 10:
            c = 10
        else:
            c = x[2]
        t = a + c
        u = 0
        for y in x[3]:
            u = u + y
        l = t - u
        if l < 3:
            s = "LOW"
        else:
            s = "OK"
        r.append((x[0], x[1], t, u, l, s))
    print("Leave report generated on", datetime.date.today())
    print("-" * 50)
    for z in r:
        print(z[0].ljust(6), z[1].ljust(18), str(z[2]).rjust(4), str(z[3]).rjust(4), str(z[4]).rjust(4), z[5])
    n = 0
    for z in r:
        if z[5] == "LOW":
            n += 1
    print("-" * 50)
    print(n, "employees have less than 3 days left")
    return r


data = [
    ("E101", "Asha Kulkarni", 4, [2, 1, 5]),
    ("E102", "Rahul Menon", 12, [10, 9, 6]),
    ("E103", "Fatima Sheikh", 0, [3, 3, 3, 3, 3, 3, 2]),
    ("E104", "Vikram Gowda", 7, []),
    ("E105", "Meera Iyer", 10, [5, 5, 5, 5, 5, 4]),
]
f(data)
