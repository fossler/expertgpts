"""Help page for ExpertGPTs application - displays documentation from docs/."""

import os
from pathlib import Path
import streamlit as st
from lib.shared.session_state import initialize_shared_session_state
from lib.shared.helpers import render_git_branch_footer


def read_markdown_file(file_path: Path) -> str:
    """Read a markdown file and return its content.

    Args:
        file_path: Path to the markdown file

    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# Error\n\nCould not read file: {e}"


def get_docs_structure() -> dict:
    """Get the documentation structure organized by category.

    Returns:
        Dictionary with categories as keys and lists of files as values
    """
    docs_dir = Path(__file__).parent.parent / "docs"

    structure = {
        "Getting Started": [],
        "User Guide": [],
        "Configuration": [],
        "Architecture": [],
        "Development": [],
        "Reference": [],
        "API": [],
        "Internationalization": [],
        "Other": []
    }

    # Map directory names to structure keys
    dir_mapping = {
        "getting-started": "Getting Started",
        "user-guide": "User Guide",
        "configuration": "Configuration",
        "architecture": "Architecture",
        "development": "Development",
        "reference": "Reference",
        "api": "API",
        "internationalization": "Internationalization"
    }

    # Get all markdown files
    for md_file in docs_dir.rglob("*.md"):
        rel_path = md_file.relative_to(docs_dir)
        parts = rel_path.parts

        # Determine category based on directory
        category = "Other"
        for i, part in enumerate(parts):
            if part in dir_mapping:
                category = dir_mapping[part]
                break

        # Add to structure
        structure[category].append((rel_path, md_file))

    return structure


def render_doc_toc():
    """Render the documentation table of contents in the sidebar."""
    from lib.i18n import i18n

    docs_dir = Path(__file__).parent.parent / "docs"

    # Quick links to main docs
    st.markdown(f"**{i18n.t('help.quick_links', default='Quick Links')}**")
    
    st.markdown("---")

    quick_links = {
        "README.md": "📖 Documentation Home",
        "getting-started/quickstart.md": "⚡ Quick Start",
        "getting-started/installation.md": "📥 Installation",
        "user-guide/basics.md": "📖 User Guide",
        "user-guide/creating-experts.md": "➕ Creating Experts",
        "reference/troubleshooting.md": "🔧 Troubleshooting",
    }

    for file_path, label in quick_links.items():
        full_path = docs_dir / file_path
        if full_path.exists():
            if st.button(label, key=f"toc_{file_path.replace('/', '_')}", use_container_width=True):
                st.session_state.selected_doc = file_path
                st.rerun()

    st.markdown("---")

    # Documentation by category
    st.markdown(f"**{i18n.t('help.by_category', default='By Category')}**")

    structure = get_docs_structure()

    # Display each category
    for category, files in structure.items():
        if not files:
            continue

        with st.expander(f"**{category}**", expanded=False):
            for rel_path, file_path in sorted(files):
                # Get filename without extension for display
                display_name = rel_path.stem.replace('_', ' ').title()
                # Add parent directory if needed
                if rel_path.parent != Path('.'):
                    display_name = f"{rel_path.parent.name} / {display_name}"

                if st.button(display_name, key=f"doc_{rel_path.as_posix().replace('/', '_')}", use_container_width=True):
                    st.session_state.selected_doc = str(rel_path)
                    st.rerun()


def render_breadcrumbs(rel_path: str):
    """Render breadcrumb navigation for the current doc.

    Args:
        rel_path: Relative path to the current doc from docs/
    """
    parts = Path(rel_path).parts
    breadcrumbs = []

    # Build breadcrumb path
    current_path = ""
    for i, part in enumerate(parts):
        if i == 0:
            current_path = part
        else:
            current_path = f"{current_path}/{part}"

        # Don't make the current page clickable
        if i == len(parts) - 1:
            # Last item - current page
            breadcrumbs.append(f"**{part}**")
        else:
            # Parent directory - clickable
            breadcrumbs.append(f"[{part}](javascript:void(0))")

    st.markdown(" / ".join(breadcrumbs))


def render_markdown_content(content: str, rel_path: str):
    """Render markdown content with proper link handling.

    Args:
        content: Markdown content
        rel_path: Relative path to the current doc
    """
    # Convert relative markdown links to work in Streamlit
    # This handles links like [](../getting-started/installation.md)
    lines = content.split('\n')
    processed_lines = []

    for line in lines:
        # Skip lines that are just navigation
        line_lower = line.lower().strip()
        if (line_lower.startswith('back to:') or
            'documentation home' in line_lower and '|' in line_lower):
            continue

        # Handle relative markdown links
        # Pattern: [text](../other-file.md) or [text](./file.md)
        import re

        # Replace all internal links with plain text (remove link formatting)
        def replace_relative_link(match):
            text = match.group(1)
            link_target = match.group(2)

            # Keep external links and anchors
            if link_target.startswith('http') or link_target.startswith('#'):
                return match.group(0)

            # For internal links, just return the text
            return text

        # Replace markdown links
        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_relative_link, line)
        processed_lines.append(line)

    # Join and display
    processed_content = '\n'.join(processed_lines)

    # Display the markdown
    st.markdown(processed_content)


def main():
    """Main help page entry point."""
    # Initialize shared session state
    initialize_shared_session_state()

    from lib.i18n import i18n

    # Page config
    st.set_page_config(
        page_title="Help",
        page_icon=":material/help:",
        layout="wide"
    )

    # Initialize selected doc if not set
    if "selected_doc" not in st.session_state:
        st.session_state.selected_doc = "README.md"

    st.title(f"📚 {i18n.t('help.title', default='Help & Documentation')}")

    # Two-column layout
    col1, col2 = st.columns([1, 3])

    with col1:
        # Sidebar with TOC
        render_doc_toc()

    with col2:
        # Main content area
        docs_dir = Path(__file__).parent.parent / "docs"
        selected_doc = st.session_state.selected_doc

        # Resolve full path
        full_path = docs_dir / selected_doc

        if full_path.exists():
            # Breadcrumbs
            render_breadcrumbs(selected_doc)

            st.divider()

            # Read and display content
            content = read_markdown_file(full_path)

            # Render with link handling
            render_markdown_content(content, selected_doc)
        else:
            st.error(f"❌ {i18n.t('help.doc_not_found', default='Documentation not found')}")
            st.markdown(f"**File**: `{selected_doc}`")

            # Provide option to go back to home
            if st.button(f"📖 {i18n.t('help.go_home', default='Go to Documentation Home')}", key="go_home"):
                st.session_state.selected_doc = "README.md"
                st.rerun()

    # Footer
    st.divider()
    st.caption(f"💡 {i18n.t('help.tip', default='Tip: Use the sidebar on the left to browse documentation')}")

    # Git branch footer in sidebar (at very bottom)
    render_git_branch_footer()


if __name__ == "__main__":
    main()
