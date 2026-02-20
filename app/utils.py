import tomllib
from functools import lru_cache
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


@lru_cache(maxsize=1)
def get_app_version() -> str:
    with PYPROJECT_PATH.open("rb") as f:
        pyproject = tomllib.load(f)

    return pyproject["project"]["version"]
