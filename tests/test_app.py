from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.bestbuy_reviews import REVIEW_COLUMNS


def test_dashboard_analyzes_reviews_and_renders_exports_with_dataset_note():
    reviews = pd.DataFrame(
        [
            {
                "primary_key": f"sample-{index}",
                "title": f"Review {index}",
                "title_source": (
                    "generated_from_review_text" if index == 0 else "source"
                ),
                "review_text": "Excellent screen and easy setup."
                if index < 45
                else "Broken screen and disappointing quality.",
                "date": "2026-01-01",
                "rating": 5 if index < 45 else 1,
                "source": "synthetic integration fixture",
                "reviewer_name": "",
                "data_quality_note": "Treat as a test sample.",
            }
            for index in range(50)
        ],
        columns=REVIEW_COLUMNS + ["data_quality_note"],
    )

    app_path = str(Path(__file__).resolve().parents[1] / "app.py")
    app = AppTest.from_file(app_path).run(timeout=120)
    app.session_state["reviews"] = reviews
    app.run(timeout=120)

    assert not app.exception
    assert [metric.label for metric in app.metric] == [
        "Reviews analyzed",
        "Average rating",
        "Positive",
        "Negative",
    ]
    assert any("Treat as a test sample." in warning.value for warning in app.warning)
    assert any("1 display title(s) were derived" in item.value for item in app.info)
    assert len(app.get("download_button")) == 2
    assert any("meets the minimum 50-review threshold" in item.value for item in app.success)


def test_removing_uploaded_csv_clears_its_previous_analysis():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(
        timeout=120
    )
    app.session_state["reviews"] = pd.DataFrame(
        [{"review_text": "Previously uploaded review"}],
        columns=["review_text"],
    )
    app.session_state["uploaded_file_name"] = "reviews.csv"
    app.run(timeout=120)

    assert not app.exception
    assert app.session_state["reviews"].empty
    assert app.session_state["uploaded_file_name"] is None
    assert any("Upload a review CSV" in message.value for message in app.info)


def test_dashboard_renders_saved_html_review_upload_option():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(
        timeout=120
    )

    assert not app.exception
    upload_labels = [uploader.label for uploader in app.get("file_uploader")]
    assert "Upload an existing review CSV" in upload_labels
    assert "Or upload browser-saved Best Buy review pages" in upload_labels
