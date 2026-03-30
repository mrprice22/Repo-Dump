import os
import subprocess
import argparse
from pathlib import Path
from datetime import datetime


def is_git_ignored(root_path: Path, file_path: Path) -> bool:
    """
    Returns True if file is ignored by git.
    """
    try:
        relative_path = file_path.relative_to(root_path)
        result = subprocess.run(
            ["git", "-C", str(root_path), "check-ignore", str(relative_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def is_manually_ignored(root_path: Path, file_path: Path, ignore_patterns: list) -> bool:
    """
    Returns True if the file matches any of the user-supplied ignore patterns.
    Patterns are matched against the relative path from root and support globs.
    """
    relative_path = file_path.relative_to(root_path)
    for pattern in ignore_patterns:
        # Match against relative path string (e.g. "config/local.py")
        if relative_path.match(pattern):
            return True
        # Also allow matching by filename only (e.g. "secrets.json")
        if Path(pattern).name == relative_path.name and "/" not in pattern and "\\" not in pattern:
            return True
    return False


def generate_tree(root_path: Path):
    """
    Yields all directories and files recursively.
    """
    for path in sorted(root_path.rglob("*")):
        yield path


def main():
    parser = argparse.ArgumentParser(description="Dump repo structure and selected file contents to Markdown.")
    parser.add_argument(
        "--root",
        type=str,
        default=str(Path(__file__).parent.resolve()),
        help="Root directory to scan (default: script location)",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        required=True,
        help="File extensions to include content for (example: .py .json .yml)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="RepoDump.md",
        help='Output markdown file (default: "RepoDump.md")',
    )
    parser.add_argument(
        "--ignore",
        nargs="+",
        default=[],
        help=(
            "Specific files or glob patterns to ignore, even if they match --extensions "
            "and are not in .gitignore. Matched against the relative path from root. "
            "Examples: secrets.json  config/local.py  '**/*_test.py'  'tests/*'"
        ),
    )

    args = parser.parse_args()

    root_path = Path(args.root).resolve()
    output_path = Path(args.output).resolve()
    print("Resolved output path:", output_path)
    print(f"Scanning: {root_path}")
    print(f"Writing: {output_path}")
    if args.ignore:
        print(f"Ignoring patterns: {args.ignore}")

    with open(output_path, "w", encoding="utf-8") as out:
        out.write(f"# Repository Dump\n\n")
        out.write(f"**Root:** `{root_path}`  \n")
        out.write(f"**Generated:** {datetime.utcnow().isoformat()} UTC\n\n")
        out.write("---\n\n")

        out.write("## 📁 Directory Structure\n\n")
        for path in generate_tree(root_path):
            relative = path.relative_to(root_path)
            indent = "  " * (len(relative.parts) - 1)

            if path.is_dir():
                out.write(f"{indent}- 📂 `{relative}/`\n")
            else:
                out.write(f"{indent}- 📄 `{relative}`\n")

        out.write("\n---\n\n")
        out.write("## 📄 File Contents\n\n")

        for path in generate_tree(root_path):
            if not path.is_file():
                continue

            if path.suffix not in args.extensions:
                continue

            if is_git_ignored(root_path, path):
                continue

            if is_manually_ignored(root_path, path, args.ignore):
                print(f"  Skipping (--ignore): {path.relative_to(root_path)}")
                continue

            relative = path.relative_to(root_path)

            out.write(f"### `{relative}`\n\n")

            language = path.suffix.lstrip(".")
            out.write(f"```{language}\n")

            try:
                content = path.read_text(encoding="utf-8")
                out.write(content)
            except Exception:
                out.write("[Error reading file]")

            out.write("\n```\n\n")

    print("Done.")


if __name__ == "__main__":
    main()
