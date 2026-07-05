# TextRover

**Recursively search — and optionally replace — text or regex across your files.**

`textRover.py` walks a folder tree and finds matches for a plain-text or regex pattern in files of the extensions you choose, then can replace them in place. It previews matches, supports config-driven runs, and (being pure Python file I/O) runs anywhere Python does. CB9Lib is bundled.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Installation](#installation)
5. [Alias Setup — Run From Anywhere](#alias-setup--run-from-anywhere)
6. [Configuration](#configuration)
7. [Usage & Examples](#usage--examples)
8. [Troubleshooting](#troubleshooting)
9. [License / Copyright](#license--copyright)

---

## Overview

Need to rename a function across a project, fix a URL in every `.inc`, or just find every file mentioning a string? TextRover does recursive search-and-replace with an extension filter, so it touches only the file types you intend.

---

## Features

- **Recursive search** across a folder tree.
- **Text or regex** patterns.
- **In-place replace** with preview before committing.
- **Extension filter** — restrict to `.txt`, `.js`, `.sh`, `.inc`, `.php`, or your own list.
- **Config-driven or interactive** — save settings in JSON or answer prompts.
- **CB9-styled UI** with clear match reporting.

---

## Requirements

| Requirement | Notes |
|-------------|-------|
| **Python 3.8+** | Cross-platform (macOS, Linux, Windows). |
| **CB9Lib** | **Bundled** — no separate install. |

---

## Installation

```bash
git clone <REPOSITORY_URL> TextRover
cd TextRover
python3 textRover.py
```

---

## Alias Setup — Run From Anywhere

Launch from any directory by typing `textrover`.

### macOS / Linux (zsh or bash)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
alias textrover='python3 ~/path/to/TextRover/textRover.py'
```

Reload and run:

```bash
source ~/.zshrc
textrover
```

**Alternative — symlink onto your `PATH`:**

```bash
chmod +x ~/path/to/TextRover/textRover.py
ln -s ~/path/to/TextRover/textRover.py /usr/local/bin/textrover
```

### Windows (PowerShell)

Add to your PowerShell `$PROFILE`:

```powershell
function textrover { python "C:\path\to\TextRover\textRover.py" @args }
```

Open a new PowerShell window and run `textrover`.

---

## Configuration

Edit **`textRoverConfig.json`** (a `textRoverConfigSample.json` is included). Typical keys:

```json
{
  "interactiveMode": false,
  "searchFolder": "~/Documents/project",
  "searchPattern": "oldString",
  "replacePattern": "newString",
  "extensions": [".txt", ".js", ".sh", ".inc", ".php"],
  "useRegex": false
}
```

| Key | Description |
|-----|-------------|
| `searchFolder` | Root of the recursive search. |
| `searchPattern` / `replacePattern` | What to find / what to write. |
| `extensions[]` | File types to include (default: `.txt .js .sh .inc .php`). |
| `useRegex` | Treat `searchPattern` as a regular expression. |
| `interactiveMode` | Prompt for values instead of using the config. |

> **Back up important files** (or use version control) before a large replace.

---

## Usage & Examples

```bash
python3 textRover.py
```

1. Confirm the search folder, pattern, and extensions (from config or prompts).
2. Review the reported matches.
3. Confirm to replace in place, or exit after searching.

**Example — swap a domain across a site:** set `searchFolder` to the project, `searchPattern` to `http://old.example.com`, `replacePattern` to `https://new.example.com`, and limit `extensions` to `[".php", ".inc", ".js"]`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No matches found | Widen `extensions`, check the folder path, or toggle `useRegex`. |
| Too many matches replaced | Preview first; narrow the pattern or restrict `extensions`. |
| Regex not matching | Ensure `useRegex` is `true` and escape special characters properly. |
| Encoding errors on some files | Exclude binary types from `extensions`. |

---

## License / Copyright

---
**Version:** 1.0
**Author:** Cloud Box 9 Inc.
**Maintainer / Owner:** Cloud Box 9 Inc.
**Last Updated:** Jul 5, 2026

Copyright © 2026 Cloud Box 9 Inc. All rights reserved.
