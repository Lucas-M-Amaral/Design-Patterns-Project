"""
Run ``python merge_default_dotenvs_in_dotenv.py`` to generate a default .env file
"""

import os
from collections.abc import Sequence
from pathlib import Path


def merge(
    output_file: Path,
    files_to_merge: Sequence[Path],
) -> None:
    merged_content = ""
    for merge_file in files_to_merge:
        merged_content += merge_file.read_text()
        merged_content += os.linesep
    output_file.write_text(merged_content)


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.resolve()
    DOTENVS_DIR = BASE_DIR / ".envs"
    DOTENV_FILES = [
        DOTENVS_DIR / ".fastapi",
        DOTENVS_DIR / ".mysql",
    ]
    DOTENV_FILE = BASE_DIR / ".env"

    merge(DOTENV_FILE, DOTENV_FILES)
