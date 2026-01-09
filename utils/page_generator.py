"""Page generator for creating new Domain Expert Agent pages."""

from pathlib import Path
from typing import Optional, Tuple, Dict, List
import re
import streamlit as st

from utils.helpers import sanitize_name
from utils.types import PageInfo


class PageGenerator:
    """Generates new Streamlit pages for expert agents."""

    def __init__(
        self,
        pages_dir: str = "pages",
        template_path: Optional[str] = None
    ):
        """Initialize the page generator.

        Args:
            pages_dir: Directory where pages are stored
            template_path: Path to template file (default: templates/template.py)
        """
        self.pages_dir = Path(pages_dir)
        self.pages_dir.mkdir(exist_ok=True)

        if template_path is None:
            template_path = "templates/template.py"

        self.template_path = Path(template_path)

    def get_next_page_number(self) -> int:
        """Get the next available page number without creating a file.

        This method scans existing pages to determine the next available page number,
        but does not create any files. Useful for determining page numbers before
        creating configs.

        Returns:
            Next available page number (e.g., 1001, 1002, etc.)

        Examples:
            >>> pg = PageGenerator()
            >>> pg.get_next_page_number()
            1001
        """
        existing_numbers = []

        for file in self.pages_dir.glob("*.py"):
            # Skip system pages
            if (file.name.startswith("_") or
                file.name == "template.py" or
                file.name == "1000_Home.py" or
                file.name == "9999_Settings.py"):
                continue

            try:
                # Extract number prefix (e.g., "1003_Coding_Expert.py" -> 1003)
                parts = file.name.split("_", 1)
                if parts[0].isdigit():
                    existing_numbers.append(int(parts[0]))
            except (IndexError, ValueError):
                continue

        # Get next number, starting from 1001 (Home is 1000, Settings is 9999)
        return max(existing_numbers, default=1000) + 1

    def generate_page(
        self,
        expert_id: str,
        expert_name: str,
        overwrite: bool = False
    ) -> Tuple[str, int]:
        """Generate a new page from the template.

        Args:
            expert_id: Unique ID of the expert
            expert_name: Display name for the expert
            overwrite: Whether to overwrite existing page

        Returns:
            Tuple of (page_path, page_number) for the generated page
        """
        # Generate safe filename with ordering prefix
        safe_name = sanitize_name(expert_name)
        page_filename = self._get_next_filename(f"{safe_name}.py")
        page_path = self.pages_dir / page_filename

        # Extract page number from filename
        page_number = int(page_filename.split("_")[0])

        # Check if page exists
        if page_path.exists() and not overwrite:
            raise FileExistsError(
                f"Page already exists: {page_filename}. "
                "Use overwrite=True to replace it."
            )

        # Read template
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        with open(self.template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Replace placeholders in template
        page_content = template_content.replace(
            "{{EXPERT_ID}}", expert_id
        ).replace(
            "{{EXPERT_NAME}}", expert_name
        )

        # Write new page
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(page_content)

        return str(page_path), page_number

    def _get_next_filename(self, base_filename: str) -> str:
        """Get the next available filename with proper ordering prefix.

        Args:
            base_filename: Base filename (e.g., "My_Expert.py")

        Returns:
            Filename with ordering prefix (e.g., "1003_My_Expert.py")
        """
        # Get existing page numbers
        existing_numbers = []
        for file in self.pages_dir.glob("*.py"):
            # Skip hidden files, template, Home page, and Settings page
            if (file.name.startswith("_") or
                file.name == "template.py" or
                file.name == "1000_Home.py" or
                file.name == "9999_Settings.py"):
                continue
            try:
                # Extract number prefix (e.g., "1003_Coding_Expert.py" -> 1003)
                parts = file.name.split("_", 1)
                if parts[0].isdigit():
                    existing_numbers.append(int(parts[0]))
            except (IndexError, ValueError):
                continue

        # Get next number, starting from 1001 (Home is 1000, Settings is 9999)
        next_number = max(existing_numbers, default=1000) + 1

        return f"{next_number}_{base_filename}"

    def delete_page(self, expert_id: str) -> bool:
        """Delete a page file.

        Note: This requires finding the page by reading its content to match expert_id.

        Args:
            expert_id: Unique ID of the expert

        Returns:
            True if deleted, False if not found
        """
        for page_file in self.pages_dir.glob("*.py"):
            if page_file.name.startswith("_") or page_file.name == "template.py":
                continue

            try:
                with open(page_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check if this page belongs to the expert
                if f'EXPERT_ID = "{expert_id}"' in content:
                    page_file.unlink()
                    return True
            except Exception:
                continue

        return False

    @st.cache_resource
    def _build_page_index(_self) -> Dict[str, PageInfo]:
        """Build an optimized index of pages without reading file contents.

        This is much faster than reading every file - it just parses filenames.

        Returns:
            Dict mapping page numbers to PageInfo objects
        """
        index = {}

        if not _self.pages_dir.exists():
            return index

        for page_file in _self.pages_dir.glob("*.py"):
            # Skip system pages
            if (page_file.name.startswith("_") or
                page_file.name == "template.py" or
                page_file.name in ["1000_Home.py", "9999_Settings.py"]):
                continue

            # Parse filename to extract page number and expert name
            # Format: NUMBER_SafeName.py (e.g., 1001_Python_Expert.py)
            match = re.match(r"(\d+)_(.+)\.py", page_file.name)

            if match:
                page_number = int(match.group(1))
                safe_name = match.group(2)

                # Convert safe_name to display name
                expert_name = safe_name.replace("_", " ").title()

                index[str(page_number)] = {
                    "filename": page_file.name,
                    "expert_name": expert_name,
                    "page_number": page_number
                }

        return index

    def list_pages(self) -> List[Dict]:
        """List all existing expert pages (optimized with indexing).

        Returns:
            List of page file information

        Note:
            This method is cached at the resource level for performance.
            The cache automatically invalidates when files change.
        """
        # Get the cached index
        page_index = self._build_page_index()

        # Convert index to list format (backward compatibility)
        pages = [
            {
                "filename": info["filename"],
                "expert_id": f"{page_num}_{info['expert_name'].lower().replace(' ', '_')}",
                "expert_name": info["expert_name"]
            }
            for page_num, info in sorted(page_index.items(), key=lambda x: int(x[0]))
        ]

        return pages
