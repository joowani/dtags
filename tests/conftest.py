import shutil
import sys
from pathlib import Path

import pytest

from dtags import style

TEST_ROOT = Path.cwd() / "dtags-test"
SUB_DIR1 = "dir1"
SUB_DIR2 = "dir2"
SUB_DIR3 = "dir3"


def pytest_unconfigure(*_):
    shutil.rmtree(TEST_ROOT, ignore_errors=True)


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setattr(style, "TTY", False)
    monkeypatch.setattr(sys, "exit", lambda code: None)
    monkeypatch.setattr(Path, "home", lambda: TEST_ROOT)

    shutil.rmtree(TEST_ROOT, ignore_errors=True)

    (TEST_ROOT / SUB_DIR1).mkdir(parents=True, exist_ok=True)
    (TEST_ROOT / SUB_DIR2).mkdir(parents=True, exist_ok=True)
    (TEST_ROOT / SUB_DIR3).mkdir(parents=True, exist_ok=True)


@pytest.fixture(autouse=False)
def dir1(setup):
    return TEST_ROOT / SUB_DIR1


@pytest.fixture(autouse=False)
def dir2(setup):
    return TEST_ROOT / SUB_DIR2


@pytest.fixture(autouse=False)
def dir3(setup):
    return TEST_ROOT / SUB_DIR3
