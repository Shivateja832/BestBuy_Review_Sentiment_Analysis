"""Input helpers for authorized review datasets."""

from __future__ import annotations

from pathlib import Path
from typing import IO

import pandas as pd


def load_review_csv(source: str | Path | IO[bytes]) -> pd.DataFrame:
    """Load a CSV and translate common file-format failures into actionable errors."""
    try:
        return pd.read_csv(source)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "The selected CSV is empty; include a header row and review data."
        ) from exc
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise ValueError(f"The selected file is not a readable UTF-8 CSV: {exc}") from exc
