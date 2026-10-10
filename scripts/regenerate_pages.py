#!/usr/bin/env python3
"""Regenerate all expert pages from templates/template.py.

Run this after changing the template. Each page keeps its filename, expert ID
and name, so configs and chat history are untouched (unlike
reset_application.py, which deletes all data).

    uv run python scripts/regenerate_pages.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lib.shared.page_generator import PageGenerator


def main():
    """Regenerate all expert pages and list them."""
    generator = PageGenerator(
        pages_dir=str(project_root / "pages"),
        template_path=str(project_root / "templates" / "template.py"),
    )
    pages = generator.regenerate_pages()
    for page in pages:
        print(f"✅ {page}")
    print(f"Regenerated {len(pages)} expert page(s).")


if __name__ == "__main__":
    main()
