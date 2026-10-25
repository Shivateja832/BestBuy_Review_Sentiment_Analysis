from io import BytesIO

import pandas as pd
import pytest

from src.data_io import load_review_csv


def test_load_review_csv_reads_valid_csv():
    reviews = load_review_csv(BytesIO(b"review_text,rating\nWorks well,5\n"))
    assert reviews.to_dict(orient="records") == [
        {"review_text": "Works well", "rating": 5}
    ]


def test_load_review_csv_reports_empty_file():
    with pytest.raises(ValueError, match="CSV is empty"):
        load_review_csv(BytesIO(b""))


def test_load_review_csv_reports_malformed_file():
    with pytest.raises(ValueError, match="not a readable UTF-8 CSV"):
        load_review_csv(BytesIO(b'review_text,rating\n"unfinished,5'))


def test_load_review_csv_reports_invalid_utf8():
    with pytest.raises(ValueError, match="not a readable UTF-8 CSV"):
        load_review_csv(BytesIO(b"review_text\n\xff"))
