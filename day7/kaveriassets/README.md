# KaveriAssets

The IT asset register of Kaveri Systems: every laptop, monitor, phone and headset in the Mysuru and Bengaluru offices, who has it, and what happened to it.

```powershell
python -m kaveriassets list [--type laptop] [--status in_stock]
python -m kaveriassets show KA-L001
python -m kaveriassets assign KA-L006 E07 [--today 2026-12-01]
python -m kaveriassets return KA-L006 [--today 2026-12-01]
python -m kaveriassets summary
python -m pytest
```

Python 3.10 or later, standard library only. Commands that change data write to `data/`; `--data DIR` uses another folder.

## Rules

* An asset can be assigned only if it's **in stock**, to an employee in the **same city**, who doesn't already hold an asset of that **type**.
* Returning an asset puts it back in stock. Every assignment and return is added to `data/history.csv`.

## Files

```
kaveriassets/models.py    Employee, Asset, AssetError
kaveriassets/store.py     read and write data/*.csv
kaveriassets/service.py   AssetService: find, list, assign, return, summary
kaveriassets/cli.py       the command line
kaveriassets/llm.py       get_llm_client(): the shared Azure OpenAI deployment
backlog/                  feature tickets
tests/                    pytest tests (fixtures/ is a copy of the original data)
```
