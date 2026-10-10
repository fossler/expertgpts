"""Tests for regenerating expert pages from the template."""

import pytest

from lib.shared.page_generator import PageGenerator


@pytest.mark.unit
def test_regenerate_pages_keeps_identity_and_skips_other_pages(tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()
    template = tmp_path / "template.py"
    template.write_text(
        'EXPERT_ID = "{{EXPERT_ID}}"\nEXPERT_NAME = "{{EXPERT_NAME}}"\n# v1\n'
    )
    generator = PageGenerator(pages_dir=str(pages_dir), template_path=str(template))
    page_path, _ = generator.generate_page("1001_python_expert", "Python Expert")

    # System and non-template pages must stay untouched
    (pages_dir / "1000_Home.py").write_text("home")
    (pages_dir / "_debug.py").write_text("debug")

    template.write_text(template.read_text().replace("# v1", "# v2"))
    assert generator.regenerate_pages() == ["1001_python_expert.py"]

    source = (pages_dir / "1001_python_expert.py").read_text()
    assert 'EXPERT_ID = "1001_python_expert"' in source
    assert 'EXPERT_NAME = "Python Expert"' in source
    assert "# v2" in source
    assert (pages_dir / "1000_Home.py").read_text() == "home"
    assert (pages_dir / "_debug.py").read_text() == "debug"
