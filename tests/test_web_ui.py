"""Playwright UI tests for md2reqif web interface.

Run in interactive/headed mode:
    pytest tests/test_web_ui.py --headed

Run with inspector (step through):
    PWDEBUG=1 pytest tests/test_web_ui.py

Run headless (CI):
    pytest tests/test_web_ui.py
"""
import io
import threading
import time
import pytest
from pathlib import Path
from playwright.sync_api import Page, expect
from md2reqif.web import app as flask_app

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def live_server():
    """Start Flask test server in a background thread."""
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False

    server_thread = threading.Thread(
        target=lambda: flask_app.run(host="127.0.0.1", port=15555, use_reloader=False),
        daemon=True,
    )
    server_thread.start()
    time.sleep(0.5)  # Wait for server to start
    yield "http://127.0.0.1:15555"


@pytest.fixture
def base_url(live_server):
    return live_server


def test_homepage_loads(page: Page, base_url: str):
    """Test that the homepage loads correctly."""
    page.goto(base_url)
    expect(page).to_have_title("md2reqif — Markdown ↔ ReqIF Converter")


def test_homepage_has_two_cards(page: Page, base_url: str):
    """Test that both conversion cards are present."""
    page.goto(base_url)
    expect(page.locator("#md-to-reqif")).to_be_visible()
    expect(page.locator("#reqif-to-md")).to_be_visible()


def test_homepage_has_format_info(page: Page, base_url: str):
    """Test that format info section is visible."""
    page.goto(base_url)
    expect(page.locator(".format-info")).to_be_visible()
    expect(page.locator(".format-info pre")).to_contain_text("REQ-001")


def test_md_to_reqif_upload_shows_filename(page: Page, base_url: str):
    """Test that selecting a file shows its name."""
    page.goto(base_url)
    # Create a temporary markdown file
    md_content = b"""# Test Requirements

## Section One

### REQ-001: First requirement
- Status: Draft

The system SHALL do something.
"""
    # Use file chooser to upload
    with page.expect_file_chooser() as fc_info:
        page.locator("#drop-md").click()
    file_chooser = fc_info.value
    file_chooser.set_files({
        "name": "test.md",
        "mimeType": "text/markdown",
        "buffer": md_content,
    })
    # The filename should appear
    expect(page.locator("#name-md")).to_contain_text("test.md")


def test_md_to_reqif_conversion_downloads_file(page: Page, base_url: str):
    """Test full MD → ReqIF conversion returns a download."""
    page.goto(base_url)
    md_content = b"""# Project Requirements

## Authentication

### REQ-AUTH-001: User Login
- Status: Approved
- Priority: High

The system SHALL authenticate users.
"""
    with page.expect_download() as download_info:
        with page.expect_file_chooser() as fc_info:
            page.locator("#drop-md").click()
        file_chooser = fc_info.value
        file_chooser.set_files({
            "name": "requirements.md",
            "mimeType": "text/markdown",
            "buffer": md_content,
        })
        page.locator("#form-md button[type=submit]").click()

    download = download_info.value
    assert download.suggested_filename == "requirements.reqif"

    # Verify the downloaded content is valid XML
    content = Path(download.path()).read_text()
    assert "REQ-IF" in content
    assert "REQ-AUTH-001" in content


def test_reqif_to_md_conversion_downloads_file(page: Page, base_url: str):
    """Test full ReqIF → MD conversion returns a download."""
    from md2reqif.md_parser import parse as parse_markdown
    from md2reqif.reqif_writer import write as write_reqif

    # Create a ReqIF file from known markdown
    md_source = """# Test Module

## Section

### REQ-001: Test requirement
- Status: Draft

The system SHALL work.
"""
    doc = parse_markdown(md_source)
    reqif_str = write_reqif(doc)
    reqif_bytes = reqif_str.encode("utf-8") if isinstance(reqif_str, str) else reqif_str

    page.goto(base_url)
    with page.expect_download() as download_info:
        with page.expect_file_chooser() as fc_info:
            page.locator("#drop-reqif").click()
        file_chooser = fc_info.value
        file_chooser.set_files({
            "name": "requirements.reqif",
            "mimeType": "application/xml",
            "buffer": reqif_bytes,
        })
        page.locator("#form-reqif button[type=submit]").click()

    download = download_info.value
    assert download.suggested_filename == "requirements.md"
    content = Path(download.path()).read_text()
    assert "REQ-001" in content


def test_invalid_file_type_shows_error(page: Page, base_url: str):
    """Test that uploading wrong file type shows error flash."""
    page.goto(base_url)
    with page.expect_file_chooser() as fc_info:
        page.locator("#drop-md").click()
    file_chooser = fc_info.value
    file_chooser.set_files({
        "name": "notmarkdown.txt",
        "mimeType": "text/plain",
        "buffer": b"just text",
    })
    page.locator("#form-md button[type=submit]").click()
    # Should show error flash
    expect(page.locator(".flash.error")).to_be_visible()
    expect(page.locator(".flash.error")).to_contain_text("Markdown")
