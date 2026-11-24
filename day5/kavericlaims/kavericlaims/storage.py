# storage.py - read the data files
# written 2015 (Python 2), ported to Python 3 in 2019
import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_employees(data_dir=None):
    if data_dir == None:
        data_dir = DATA_DIR
    f = open(os.path.join(data_dir, "employees.csv"))
    lines = f.readlines()
    f.close()
    emps = {}
    i = 0
    for line in lines:
        i = i + 1
        if i == 1:
            continue
        line = line.strip()
        if line == "":
            continue
        p = line.split(",")
        # id -> [name, grade, city, manager, cost centre]
        emps[p[0]] = [p[1], p[2], p[3], p[4], p[5]]
    return emps


def load_claims(month, data_dir=None):
    if data_dir == None:
        data_dir = DATA_DIR
    fn = os.path.join(data_dir, "claims_%s.csv" % month)
    if not os.path.exists(fn):
        print("No claims file for " + month)
        return []
    f = open(fn)
    lines = f.readlines()
    f.close()
    claims = []
    for j in range(1, len(lines)):
        line = lines[j].strip()
        if line == "":
            continue
        p = line.split(",")
        # 0 id, 1 emp, 2 date, 3 category, 4 city, 5 amount, 6 currency, 7 qty, 8 receipt, 9 status, 10 description
        c = [p[0], p[1], p[2], p[3].upper(), p[4], float(p[5]), p[6].upper(), int(p[7]), p[8], p[9].lower(), p[10]]
        claims.append(c)
    return claims


def load_rates(data_dir=None):
    if data_dir == None:
        data_dir = DATA_DIR
    try:
        f = open(os.path.join(data_dir, "fx_rates.json"))
        r = json.load(f)
        f.close()
    except:
        print("WARNING: could not read fx_rates.json")
        r = {}
    return r
