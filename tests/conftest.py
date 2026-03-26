from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def simple_md() -> str:
    return (FIXTURES / "simple.md").read_text()

@pytest.fixture
def full_md() -> str:
    return (FIXTURES / "full.md").read_text()
