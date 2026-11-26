# KA-101: `list --free` and `--city`

| | |
|---|---|
| **From** | Meera Hegde, Facilities (Mysuru) |
| **Size** | Small |

## Why

> "When a new joiner starts in Mysuru I want to see what's free **here**, not the whole company's list. `--status in_stock` is a lot to type, too."

## What

Two new options for `list`. They combine with each other and with `--type`.

* `--city CITY`: only assets in that city. Any case: `mysuru`, `Mysuru` and `MYSURU` all work. An unknown city just matches nothing.
* `--free`: only assets in stock. It means exactly the same as `--status in_stock`, so `--free` and `--status` can't be used together
  (argparse prints a usage error and the exit code is 2).

The output format doesn't change.

## Examples

```text
> python -m kaveriassets list --free --city mysuru
KA-H002  headset  Jabra Evolve2 65            Mysuru     in_stock
KA-L005  laptop   Dell Latitude 5450          Mysuru     in_stock
KA-L006  laptop   Lenovo ThinkPad T14 Gen 5   Mysuru     in_stock
KA-L007  laptop   Lenovo ThinkPad T14 Gen 5   Mysuru     in_stock
KA-M002  monitor  Dell P2423D                 Mysuru     in_stock
5 asset(s)

> python -m kaveriassets list --type laptop --free --city Bengaluru
KA-L008  laptop   Dell Latitude 5450          Bengaluru  in_stock
1 asset(s)

> python -m kaveriassets list --city Pune
No assets match.
```

## Done when

* The examples above print exactly that.
* `AssetService.list_assets` takes an optional `city` too (the CLI isn't the only caller).
* There are tests for both options, together and on their own.
