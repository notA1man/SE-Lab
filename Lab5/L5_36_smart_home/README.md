# Lab 5: Static Code Analysis - Smart Home Device Controller

The supplied **Lab 5 Static Code Analysis Student Handout PDF** defines this submission's requirements.

The controller adds devices to rooms, toggles them, sets thermostat temperatures within 16-30 degrees, lists devices by room, reports power consumption and saves `home_state.json`.

## Run and analyse

Run these commands inside `Lab5/L5_36_smart_home` using the Windows Python launcher:

```powershell
py -m pip install pylint bandit flake8
py smart_home.py
py -m pylint smart_home.py > after/pylint_report.txt
py -m bandit -r smart_home.py > after/bandit_report.txt
py -m flake8 smart_home.py > after/flake8_report.txt
```

## Deliverables

- `smart_home.py`: cleaned controller with more than four documented issues addressed.
- `issues.md`: original issue locations, descriptions, fix approaches and verification results.
- `before/`: original reports from all three tools.
- `after/`: final reports, demo output and behavioural verification results.

The final Pylint score is **10.00/10**. Bandit reports no findings, and Flake8 reports no violations. An empty Flake8 report indicates success.

## Three phases

1. Bandit: remove the unused unsafe scene-execution helper and embedded password, use a localhost hub address, and preserve baseline reports and the issue table.
2. Pylint: fix naming, documentation, mutable defaults, return paths and file encoding; handle missing devices and guard the demo during import.
3. Flake8: finish formatting, regenerate all final reports, and record working demo and behavioural checks.

The PDF requests reflection generally but supplies no reflection questions. The four-question requirement appeared only in the starter README and is not treated as a PDF requirement.
