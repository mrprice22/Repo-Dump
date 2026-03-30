# Repo Dump Scripts

Utilities for dumping a repository's structure and file contents into a single text file. Built to aid communication with **AI assistants and LLMs** — paste the output directly into a chat to give the model full context of your codebase without manually copying files one by one.

Two versions are provided: a Python script and a PowerShell script. Both respect `.gitignore` (via `git check-ignore`) and let you filter which file types to include.

---

## Scripts

### `repo_dump.py` — Python (Markdown output)

Produces a well-formatted **Markdown** file with:
- A rendered directory tree
- Fenced code blocks for each included file (with syntax highlighting hints)

Runs from the directory where the script lives by default, so you can drop it into any project root and run it with no `--root` argument.

**Requirements:** Python 3.7+, `git` on PATH.

#### Usage

```bash
python repo_dump.py --extensions .py .json .yml
```

```bash
python repo_dump.py \
  --root /path/to/your/project \
  --extensions .py .ts .json .md \
  --output MyProjectDump.md
```

```bash
# Ignore specific files or patterns even if they match --extensions
python repo_dump.py \
  --extensions .py .json \
  --ignore secrets.json 'tests/*' config/local.py
```

#### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `--root` | No | Script's directory | Root directory to scan |
| `--extensions` | **Yes** | — | Space-separated list of extensions to include (e.g. `.py .json`) |
| `--output` | No | `RepoDump.md` | Output file path |
| `--ignore` | No | — | Files or glob patterns to exclude, even if they match `--extensions` and are not in `.gitignore` (see below) |

#### `--ignore` patterns

Patterns are matched against each file's **relative path from root** and support globs. There are two matching modes:

- **Bare filename** (no path separators) — matches that filename anywhere in the tree. Useful when you don't know or care where the file lives.
- **Relative path or glob** — matched against the full path from root, so you can target specific locations or use wildcards.

Quote glob patterns to prevent your shell from expanding them early.

```bash
# Ignore a file by name, wherever it appears
--ignore secrets.json

# Ignore a file at a specific relative path
--ignore config/local.py

# Ignore all files in a directory
--ignore 'tests/*'

# Ignore by glob pattern
--ignore '**/*_test.py'

# Mix and match
--ignore secrets.json 'tests/*' config/local.py '**/*_test.py'
```

Skipped files are printed to stdout so you can confirm your patterns are matching as expected.

---

### `Dump-RepoWithContent.ps1` — PowerShell (plaintext output)

Produces a **plain text** file with:
- Every file and folder path listed
- File contents wrapped in `BEGIN FILE` / `END FILE` markers

All three parameters are mandatory — paths must be provided explicitly.

**Requirements:** PowerShell 5+, `git` on PATH.

#### Usage

```powershell
.\Dump-RepoWithContent.ps1 `
  -RootPath "C:\Projects\MyApp" `
  -Extensions ".cs", ".json", ".csproj" `
  -OutputFile "C:\Temp\MyAppDump.txt"
```

```powershell
# From inside the project directory
.\Dump-RepoWithContent.ps1 `
  -RootPath "." `
  -Extensions ".ps1", ".json", ".yml" `
  -OutputFile ".\dump.txt"
```

#### Parameters

| Parameter | Required | Description |
|---|---|---|
| `-RootPath` | **Yes** | Root directory to scan |
| `-Extensions` | **Yes** | Array of extensions to include (e.g. `".py", ".json"`) |
| `-OutputFile` | **Yes** | Output file path |

---

## Comparison

| Feature | Python (`repo_dump.py`) | PowerShell (`Dump-RepoWithContent.ps1`) |
|---|---|---|
| Output format | Markdown (fenced code blocks) | Plain text |
| Directory tree | ✅ Rendered with icons | ✅ Flat list of all paths |
| File delimiters | ` ```language ``` ` blocks | `BEGIN FILE` / `END FILE` markers |
| Root default | Script's own directory | Must be specified |
| Manual ignore list | ✅ `--ignore` (filenames & globs) | ❌ Not supported |
| Best for | Pasting into AI chats (renders nicely) | Quick dumps, scripting pipelines |

---

## Tips for AI / LLM Use

- **Prefer the Python version** when pasting into a chat UI — the Markdown formatting helps the model distinguish structure from content.
- **Filter aggressively** with `--extensions` / `-Extensions`. Only include files the model needs to understand your problem; omitting build artifacts, lock files, and generated code keeps the context smaller and more useful.
- Use `--ignore` to exclude sensitive files (e.g. `secrets.json`, `.env.local`) or noisy ones (e.g. test fixtures, generated files) that your `.gitignore` doesn't cover.
- Both scripts **skip `.gitignore`d files automatically**, so things like `node_modules`, `.env`, and build output are excluded as long as your `.gitignore` is set up correctly.
- If your dump is very large, consider pointing `--root` at a specific subdirectory rather than the whole repo.
