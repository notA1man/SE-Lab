# Smart Home Controller Issues

The table documents the original `smart_home.py` using the Pylint, Bandit and Flake8 reports and a review of the source. Security severities follow Bandit's report; other priorities are assessed from the program's behaviour. Line numbers refer to the original file before fixes.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Shell command injection (B602) | Security - High | 49-51 | `runScene` concatenates `sceneScript` into a command executed with `shell=True`. A malicious value could execute additional shell commands. The demo does not call this helper. | Removed the unused `runScene` helper, eliminating the shell command execution path. The device-controller demo remains functional. |
| All-interface hub address (B104) | Security - Medium | 4, 45-46 | `HUB_HOST` is `0.0.0.0`, which would expose a server on all network interfaces if used for binding. This file only prints the address; it does not start a server. | Changed the default hub address to `127.0.0.1`. This program only prints the address and does not start a network server. |
| Shared mutable default settings (W0102) | Functional - Medium | 11-13, 28, 55-58, 62, 67 | The default `settings={}` dictionary is shared by devices created without settings. Setting the thermostat temperature therefore also gives the light, fan and TV a temperature setting. | Use `settings=None` and create a fresh dictionary for each device; copy supplied settings to avoid sharing the caller's dictionary. |
| Missing-device lookup can crash | Functional - Medium | 23-24 | `setTemperature` directly indexes `devices[deviceName]`. An unknown device raises `KeyError` instead of being handled like the missing device in `toggleDevice`. This issue comes from source review, not the saved tool reports. | Check whether the device exists before accessing it and return a documented failure result. |
| Hardcoded password (B105) | Security - Low | 7 | The source contains the password-like literal `smarthome-demo`. It is currently unused, but embedding a credential in source is unsafe if later used for authentication. | Removed the unused password constant. No authentication feature uses it. |
| Subprocess import warning (B404) | Security review - Low | 2, 51 | Bandit flags the `subprocess` import for review. Importing it alone is not a demonstrated vulnerability; the unsafe shell call is documented above. | Removed the subprocess import along with the unused scene helper. No Bandit suppressions were added. |
| Inconsistent return paths (R1710) | Code quality | 16-20 | `toggleDevice` returns a Boolean for an existing device but implicitly returns `None` for an unknown device. The return contract is unclear. | Explicitly return `None` for a missing device and document the Boolean-or-None contract, or raise a documented exception. |
| Unspecified file encoding (W1514) | Portability | 40-42 | `saveState` opens the JSON file without an encoding, so the encoding depends on the platform. | Specify `encoding="utf-8"` when opening the state file. |
| Nonstandard names (C0103) | Style | 11, 16, 23, 32, 36, 40, 45, 49 | Function and parameter names such as `addDevice`, `deviceName` and `fileName` do not follow Python's snake_case convention. | Rename functions and parameters to snake_case and update every call site. |
| Missing docstrings (C0114, C0116) | Documentation | 1, 11, 16, 23, 32, 36, 40, 45, 49, 54 | The module and all functions lack docstrings explaining their purpose and behaviour. | Add a module docstring and concise function docstrings, including return values and failure behaviour where relevant. |
| Whitespace and line length violations (E203, E302, E261, E501) | Style | 6, 40, 66, 68 | Flake8 reports a space before a colon, insufficient blank lines before a function, insufficient spacing before an inline comment and a line exceeding 79 characters. | Remove the extra colon spacing, use two blank lines between top-level functions, add two spaces before the comment and wrap the long expression. |
| Demo runs during import | Code quality | 72 | The unconditional `main()` call runs the demo and writes `home_state.json` when another module imports this file. This issue comes from source review, not the saved tool reports. | Put the call inside an `if __name__ == "__main__":` guard so importing the module does not run the demo. |

## Implemented fixes and verification

All twelve rows above were addressed. The naming, docstring, encoding, return-path, formatting and import-guard changes are implemented in the cleaned file. Device settings now use a fresh dictionary (or a shallow copy of supplied settings), and missing devices are handled before accessing them. Original line numbers remain unchanged in this table so they can be compared with the baseline reports.

The PDF handout is the authority for this submission: fix at least four issues, handle all Bandit findings, score above 9.5 in Pylint, fix all Flake8 findings, and provide three commits with before/after reports. Neither supplied PDF contains the four reflection questions mentioned in the starter README, so no substitute questions are presented as handout requirements.

| Check | Before | After |
|-------|--------|-------|
| Pylint | 4.80/10 | 10.00/10 |
| Bandit | 1 high, 1 medium, 2 low findings | No findings; no suppressed checks |
| Flake8 | 4 violations | No violations (empty report is expected) |
| Demo light settings | `{'temperature': 30}` | `{}` |

Reports are stored in `before/` and `after/`. Final checks all exited with code 0. `after/demo_output.txt` records the working demo, and `after/verification_report.txt` records successful checks of independent settings, copying supplied settings, both temperature bounds, missing devices, toggling, room filtering, power totals and JSON saving. Scene execution was removed rather than tested because the lab-only helper was unused and no scene scripts are supplied.

Commands used from this folder:

```powershell
py smart_home.py > after/demo_output.txt
py -m pylint smart_home.py > after/pylint_report.txt
py -m bandit -r smart_home.py > after/bandit_report.txt
py -m flake8 smart_home.py > after/flake8_report.txt
```

Pylint's cache was redirected to a writable temporary location using `PYLINTHOME`; no analysis rules were disabled.
