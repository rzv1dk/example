#!/usr/bin/env python3
"""Fails (non-zero exit) if any entry is missing required frontmatter fields."""
import glob
import sys

from content_parser import parse_document

REQUIRED = ["title", "common_name", "scientific_name", "category", "severity",
            "mechanism_of_toxicity", "treatment", "sources"]

def load_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        return None
    fields, _ = parse_document(text)
    return fields

def main():
    failed = False
    for path in glob.glob("entries/**/*.md", recursive=True):
        fm = load_frontmatter(path)
        if fm is None:
            print(f"FAIL {path}: no frontmatter found")
            failed = True
            continue
        for field in REQUIRED:
            val = fm.get(field)
            if val in (None, "", [], ["" ]):
                print(f"FAIL {path}: missing required field '{field}'")
                failed = True
    if failed:
        sys.exit(1)
    print("All entries valid.")

if __name__ == "__main__":
    main()
