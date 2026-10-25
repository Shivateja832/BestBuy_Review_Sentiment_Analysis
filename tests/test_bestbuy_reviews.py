from src.bestbuy_reviews import (
    _visible_review_html,
    parse_review_cards,
    validate_product_url,
)


def test_validate_product_url_accepts_direct_bestbuy_product():
    assert validate_product_url(
        "https://www.bestbuy.ca/en-ca/product/example/123456"
    ) == "https://www.bestbuy.ca/en-ca/product/example/123456"


def test_validate_product_url_rejects_disallowed_search_route():
    try:
        validate_product_url("https://www.bestbuy.ca/en-ca/search?search=tv")
    except ValueError as exc:
        assert "search routes are disallowed" in str(exc)
    else:
        raise AssertionError("Search route should be rejected.")


def test_parse_review_cards_extracts_required_public_fields():
    html = """
    <article class="review-item" data-review-id="R123">
      <h3>Great picture</h3><p class="review-text">Bright and easy to set up.</p>
      <time datetime="2025-03-14T10:00:00Z">March 14, 2025</time>
      <span aria-label="Rated 5 out of 5 stars"></span>
      <span class="reviewer">Taylor</span>
    </article>
    """
    reviews = parse_review_cards(html, "https://www.bestbuy.ca/en-ca/product/example/123")
    assert len(reviews) == 1
    assert reviews[0] == {
        "primary_key": "R123",
        "title": "Great picture",
        "review_text": "Bright and easy to set up.",
        "date": "2025-03-14",
        "rating": 5.0,
        "source": "Best Buy Canada",
        "reviewer_name": "Taylor",
    }


def test_visible_html_excludes_hidden_review_cards():
    class Element:
        def __init__(self, markup, visible):
            self.markup = markup
            self.visible = visible

        def is_displayed(self):
            return self.visible

        def get_attribute(self, attribute):
            assert attribute == "outerHTML"
            return self.markup

    class Driver:
        def find_elements(self, by, selector):
            assert selector == ".review-card"
            return [Element("<article>visible</article>", True), Element("<article>hidden</article>", False)]

    assert _visible_review_html(Driver(), ".review-card") == "<article>visible</article>"
