from src.bestbuy_reviews import (
    _reject_optional_cookies,
    _raise_if_access_denied,
    _review_page_url,
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


def test_review_page_url_resolves_public_review_route():
    assert _review_page_url(
        "https://www.bestbuy.ca/en-ca/product/sample/123456"
    ) == "https://www.bestbuy.ca/en-ca/product/sample/123456/review"
    assert _review_page_url(
        "https://www.bestbuy.ca/en-ca/product/sample/123456/review"
    ) == "https://www.bestbuy.ca/en-ca/product/sample/123456/review"


def test_access_denied_response_stops_collection():
    class Body:
        text = "Access Denied. You do not have permission to access this server."

    class Driver:
        def find_element(self, by, selector):
            assert selector == "body"
            return Body()

    try:
        _raise_if_access_denied(Driver())
    except PermissionError as exc:
        assert "do not retry" in str(exc)
    else:
        raise AssertionError("Access denied page must stop collection.")


def test_cookie_overlay_uses_visible_reject_all_control():
    class Overlay:
        def __init__(self, driver):
            self.driver = driver

        def is_displayed(self):
            return self.driver.overlay_visible

    class RejectButton:
        text = "Reject All"

        def __init__(self, driver):
            self.driver = driver

        def is_displayed(self):
            return True

        def is_enabled(self):
            return True

        def get_attribute(self, name):
            return "onetrust-reject-all-handler" if name == "id" else None

        def click(self):
            self.driver.overlay_visible = False

    class Driver:
        overlay_visible = True

        def find_elements(self, by, selector):
            if selector == "#onetrust-pc-dark-filter":
                return [Overlay(self)]
            if selector == "#onetrust-reject-all-handler, #onetrust-banner-sdk button":
                return [RejectButton(self)]
            raise AssertionError(f"Unexpected selector: {selector}")

    driver = Driver()
    assert _reject_optional_cookies(driver, timeout=0.1) is True
    assert driver.overlay_visible is False


def test_cookie_overlay_without_reject_all_control_is_not_dismissed():
    class Overlay:
        def is_displayed(self):
            return True

    class Driver:
        def find_elements(self, by, selector):
            if selector == "#onetrust-pc-dark-filter":
                return [Overlay()]
            return []

    try:
        _reject_optional_cookies(Driver(), timeout=0)
    except RuntimeError as exc:
        assert "will not accept optional cookies" in str(exc)
    else:
        raise AssertionError("An unknown consent overlay must not be bypassed.")


def test_no_cookie_overlay_does_not_change_consent():
    class Overlay:
        def is_displayed(self):
            return False

    class Driver:
        def find_elements(self, by, selector):
            assert selector == "#onetrust-pc-dark-filter"
            return [Overlay()]

    assert _reject_optional_cookies(Driver(), timeout=0) is False


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


def test_parse_bestbuy_review_list_markup():
    html = """
    <ul>
      <li class="review_example" data-automation="review-list-item">
        <p class="sr-only">Customer rating: 4 out of 5 stars</p>
        <h3 class="reviewTitle_example">Quiet and effective</h3>
        <div class="reviewerInfo_example">
          <span class="author_example">Verified Buyer Reviewed by Jordan</span>
          <span class="locationAndTime_example">- March 14, 2025</span>
        </div>
        <div class="reviewContent_example">
          <p>The washer runs quietly and cleans well.</p>
        </div>
      </li>
    </ul>
    """
    reviews = parse_review_cards(
        html,
        "https://www.bestbuy.ca/en-ca/product/sample/123456",
        review_card_selector="[data-automation='review-list-item']",
    )
    assert len(reviews) == 1
    review = reviews[0]
    assert review["title"] == "Quiet and effective"
    assert review["review_text"] == "The washer runs quietly and cleans well."
    assert review["date"] == "2025-03-14"
    assert review["rating"] == 4.0
    assert review["reviewer_name"] == "Jordan"
    assert len(str(review["primary_key"])) == 64
