import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app


@pytest.fixture()
def client(tmp_path):
    original = ROOT / "base_conocimiento"
    copia = tmp_path / "base_conocimiento"
    shutil.copytree(original, copia)
    app = create_app({"TESTING": True, "BASE_CONOCIMIENTO": str(copia)})
    return app.test_client()
