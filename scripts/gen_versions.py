#!/usr/bin/env python3
"""Generate versions.json from the skills in this repo.

The manifest lists every skill with its scope, version, path and a sha256 per file. After a version
bump it also keeps the file hashes of the most recent previous versions (HISTORY_LIMIT), taken
from the existing versions.json.

  python3 scripts/gen_versions.py           recompute file sha256 hashes and write versions.json
  python3 scripts/gen_versions.py --check   exit 1 if versions.json is out of date
  python3 scripts/gen_versions.py --base REF   treat REF's versions.json as what is released (CI)

--base is used by CI to compare against what is already released (main). Without it, a PR that
bumps twice leaks the unreleased version into history.

When a skill directory is deleted, its entry stays in versions.json with "removed": true and its
last file hashes. Servers use those hashes to delete only copies the customer has not edited.

Version and name are read from each skill's SKILL.md frontmatter, which stays the source of truth.
Standard library only. Python 3.7 or later.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = ROOT / "skills"
MANIFEST = ROOT / "versions.json"
SCOPES = ("portable", "openclaw", "hermes")
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
HISTORY_LIMIT = 10

EXCLUDED_NAMES = {}
EXCLUDED_DIRS = {"__pycache__"}


def frontmatter_field(text: str, field: str, source: Path) -> str:
    if not text.startswith("---\n"):
        raise SystemExit("{}: no frontmatter".format(source))
    end = text.find("\n---", 4)
    if end == -1:
        raise SystemExit("{}: unterminated frontmatter".format(source))
    match = re.search(r"^{}:\s*(.+?)\s*$".format(field), text[4:end], re.MULTILINE)
    if not match:
        raise SystemExit("{}: missing top-level '{}:' in frontmatter".format(source, field))
    return match.group(1).strip("\"'")


def skill_files(skill_dir: Path) -> dict:
    files = {}
    for path in skill_dir.rglob("*"):
        rel = path.relative_to(skill_dir)
        if not path.is_file() or path.name in EXCLUDED_NAMES or EXCLUDED_DIRS & set(rel.parts):
            continue
        files[rel.as_posix()] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def existing_skills() -> dict:
    if not MANIFEST.is_file():
        return {}
    return json.loads(MANIFEST.read_text(encoding="utf-8")).get("skills", {})


def base_skills(ref: str) -> dict:
    git = ["git", "-C", str(ROOT)]
    if subprocess.run(git + ["rev-parse", "--verify", "--quiet", ref + "^{commit}"],
                      capture_output=True).returncode != 0:
        raise SystemExit("unknown git ref '{}'".format(ref))
    shown = subprocess.run(git + ["show", ref + ":versions.json"], capture_output=True, text=True)
    if shown.returncode != 0:
        return {}
    return json.loads(shown.stdout).get("skills", {})


def version_tuple(version: str) -> tuple:
    return tuple(int(part) for part in version.split("."))


def check_against_base(name: str, version: str, files: dict, released: dict) -> None:
    if version_tuple(version) < version_tuple(released["version"]):
        raise SystemExit("{}: version {} is lower than {} on the base branch".format(
            name, version, released["version"]))
    if version == released["version"] and files != released["files"]:
        raise SystemExit("{}: files changed but version is still {}. Bump version in SKILL.md".format(
            name, version))


def build(base=None) -> dict:
    skills = {}
    existing = existing_skills() if base is None else base
    for scope in SCOPES:
        scope_dir = SKILLS_ROOT / scope
        if not scope_dir.is_dir():
            continue
        for skill_dir in sorted(p for p in scope_dir.iterdir() if p.is_dir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                raise SystemExit("{}: missing SKILL.md".format(skill_dir))
            text = skill_md.read_text(encoding="utf-8")
            name = frontmatter_field(text, "name", skill_md)
            version = frontmatter_field(text, "version", skill_md)
            if name != skill_dir.name:
                raise SystemExit("{}: frontmatter name '{}' does not match directory".format(skill_md, name))
            if not SEMVER.match(version):
                raise SystemExit("{}: version '{}' is not X.Y.Z".format(skill_md, version))
            if name in skills:
                raise SystemExit("duplicate skill name '{}' in {} and {}".format(
                    name, skills[name]["path"], skill_dir.relative_to(ROOT).as_posix()))
            entry = {
                "scope": scope,
                "version": version,
                "path": skill_dir.relative_to(ROOT).as_posix(),
                "files": skill_files(skill_dir),
            }
            old = existing.get(name)
            if old and base is not None:
                check_against_base(name, version, entry["files"], old)
            if old:
                history = old.get("history", [])
                if old["version"] != version:
                    history = [{"version": old["version"], "files": old["files"]}] + history
                if history:
                    entry["history"] = history[:HISTORY_LIMIT]
            skills[name] = entry
    for name, old in existing.items():
        if name not in skills:
            gone = {k: old[k] for k in ("scope", "version", "path", "files")}
            gone["removed"] = True
            if old.get("history"):
                gone["history"] = old["history"]
            skills[name] = gone
    return {"schema": 1, "skills": skills}


def render(manifest: dict) -> str:
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate versions.json")
    parser.add_argument("--check", action="store_true", help="fail if versions.json is out of date")
    parser.add_argument("--base", metavar="REF", help="git ref whose versions.json counts as released")
    args = parser.parse_args()

    expected = render(build(base_skills(args.base) if args.base else None))
    if args.check:
        current = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
        if current != expected:
            print("versions.json is out of date. Run: python3 scripts/gen_versions.py", file=sys.stderr)
            sys.exit(1)
        print("versions.json is up to date")
        return
    MANIFEST.write_text(expected, encoding="utf-8")
    print("wrote {}".format(MANIFEST.relative_to(ROOT)))


if __name__ == "__main__":
    main()
