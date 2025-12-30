"""Page generator for creating new Domain Expert Agent pages."""

import os
from pathlib import Path
from typing import Optional


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

    def generate_page(
        self,
        expert_id: str,
        expert_name: str,
        overwrite: bool = False
    ) -> str:
        """Generate a new page from the template.

        Args:
            expert_id: Unique ID of the expert
            expert_name: Display name for the expert
            overwrite: Whether to overwrite existing page

        Returns:
            Path to the generated page file
        """
        # Generate safe filename with ordering prefix
        safe_name = expert_name.replace(" ", "_").replace("-", "_")
        page_filename = self._get_next_filename(f"{safe_name}.py")
        page_path = self.pages_dir / page_filename

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

        return str(page_path)

    def _get_next_filename(self, base_filename: str) -> str:
        """Get the next available filename with proper ordering prefix.

        Args:
            base_filename: Base filename (e.g., "My_Expert.py")

        Returns:
            Filename with ordering prefix (e.g., "3_My_Expert.py")
        """
        # Get existing page numbers
        existing_numbers = []
        for file in self.pages_dir.glob("*.py"):
            if file.name.startswith("_") or file.name == "template.py":
                continue
            try:
                # Extract number prefix (e.g., "1_Coding_Expert.py" -> 1)
                parts = file.name.split("_", 1)
                if parts[0].isdigit():
                    existing_numbers.append(int(parts[0]))
            except (IndexError, ValueError):
                continue

        # Get next number
        next_number = max(existing_numbers, default=0) + 1

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

    def list_pages(self) -> list:
        """List all existing expert pages.

        Returns:
            List of page file information
        """
        pages = []

        for page_file in sorted(self.pages_dir.glob("*.py")):
            if page_file.name.startswith("_") or page_file.name == "template.py":
                continue

            try:
                with open(page_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract expert info from page
                expert_id = None
                expert_name = None

                for line in content.split("\n"):
                    if line.startswith("EXPERT_ID = "):
                        expert_id = line.split("=")[1].strip().strip('"\'')
                    elif line.startswith("EXPERT_NAME = "):
                        expert_name = line.split("=")[1].strip().strip('"\'')

                if expert_id:
                    pages.append({
                        "filename": page_file.name,
                        "expert_id": expert_id,
                        "expert_name": expert_name or "Unknown",
                    })
            except Exception:
                continue

        return pages
