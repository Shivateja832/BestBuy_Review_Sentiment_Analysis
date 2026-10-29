from src.bestbuy_reviews import (
    _click_show_more,
    _additional_reviews_loaded,
    _reject_optional_cookies,
    _raise_if_access_denied,
    MAX_SAVED_REVIEW_PAGE_BYTES,
    _review_page_url,
    _visible_review_html,
    parse_review_cards,
    parse_saved_review_pages,
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
            if selector == ".onetrust-pc-dark-filter":
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
            if selector == ".onetrust-pc-dark-filter":
                return [Overlay()]
            return []

    try:
        _reject_optional_cookies(Driver(), timeout=0)
    except RuntimeError as exc:
        assert "without making a consent choice" in str(exc)
    else:
        raise AssertionError("An unknown consent overlay must not be bypassed.")


def test_no_cookie_overlay_does_not_change_consent():
    class Overlay:
        def is_displayed(self):
            return False

    class Driver:
        def find_elements(self, by, selector):
            assert selector == ".onetrust-pc-dark-filter"
            return [Overlay()]

    assert _reject_optional_cookies(Driver(), timeout=0) is False


def test_show_more_retries_after_visible_reject_optional_cookies():
    from selenium.common.exceptions import ElementClickInterceptedException

    class ShowMore:
        text = "Show More"

        def __init__(self, driver):
            self.driver = driver

        def is_displayed(self):
            return True

        def click(self):
            self.driver.show_more_clicks += 1
            if self.driver.show_more_clicks == 1:
                raise ElementClickInterceptedException("cookie consent overlay")

    class Overlay:
        def __init__(self, driver):
            self.driver = driver

        def is_displayed(self):
            return self.driver.overlay_visible

    class RejectAll:
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
        show_more_clicks = 0

        def __init__(self):
            self.show_more = ShowMore(self)

        def find_elements(self, by, selector):
            if selector == ".onetrust-pc-dark-filter":
                return [Overlay(self)]
            if selector == "#onetrust-reject-all-handler, #onetrust-banner-sdk button":
                return [RejectAll(self)]
            return [self.show_more]

        def execute_script(self, script, element):
            assert element is self.show_more

    driver = Driver()
    assert _click_show_more(driver) is True
    assert driver.overlay_visible is False
    assert driver.show_more_clicks == 2


def test_show_more_reports_when_interceptor_is_not_consent_overlay():
    from selenium.common.exceptions import ElementClickInterceptedException

    class ShowMore:
        text = "Show More"

        def is_displayed(self):
            return True

        def click(self):
            raise ElementClickInterceptedException("other overlay")

    class Overlay:
        def is_displayed(self):
            return False

    class Driver:
        def find_elements(self, by, selector):
            if selector == ".onetrust-pc-dark-filter":
                return [Overlay()]
            if selector == "#onetrust-reject-all-handler, #onetrust-banner-sdk button":
                return []
            return [ShowMore()]

        def execute_script(self, script, element):
            return None

    try:
        _click_show_more(Driver())
    except PermissionError as exc:
        assert ".onetrust-pc-dark-filter" in str(exc)
        assert "not visible" in str(exc)
    else:
        raise AssertionError("A non-consent page overlay must be reported explicitly.")


def test_show_more_visibility_detects_a_remaining_visible_page():
    from src.bestbuy_reviews import _show_more_is_visible

    class Button:
        text = "Show More"

        def is_displayed(self):
            return True

    class Driver:
        def find_elements(self, by, selector):
            assert by == "xpath"
            return [Button()]

    assert _show_more_is_visible(Driver())


def test_show_more_visibility_ignores_hidden_pagination_control():
    from src.bestbuy_reviews import _show_more_is_visible

    class Button:
        text = "Show More"

        def is_displayed(self):
            return False

    class Driver:
        def find_elements(self, by, selector):
            return [Button()]

    assert not _show_more_is_visible(Driver())


def test_pagination_limit_with_more_reviews_is_an_explicit_failure():
    from src.bestbuy_reviews import _raise_if_pagination_truncated

    class Button:
        text = "Show More"

        def is_displayed(self):
            return True

    class Driver:
        def find_elements(self, by, selector):
            return [Button()]

    try:
        _raise_if_pagination_truncated(
            Driver(),
            sort_label="Newest",
            max_pages=1,
        )
    except RuntimeError as exc:
        assert "Newest" in str(exc)
        assert "incomplete collection" in str(exc)
    else:
        raise AssertionError("A capped, incomplete scrape must not report success.")


def test_visible_review_snapshot_requeries_after_stale_dom_element():
    from selenium.common.exceptions import StaleElementReferenceException

    class Card:
        def __init__(self, markup, stale=False):
            self.markup = markup
            self.stale = stale

        def is_displayed(self):
            return True

        def get_attribute(self, name):
            assert name == "outerHTML"
            if self.stale:
                raise StaleElementReferenceException("DOM updated")
            return self.markup

    class Driver:
        calls = 0

        def find_elements(self, by, selector):
            self.calls += 1
            if self.calls == 1:
                return [Card("<article>old</article>", stale=True)]
            return [Card("<article>new</article>")]

    driver = Driver()
    assert _visible_review_html(driver, ".review-card") == "<article>new</article>"
    assert driver.calls == 2


def test_additional_reviews_wait_ignores_transient_stale_snapshot():
    from selenium.common.exceptions import StaleElementReferenceException

    class Card:
        def is_displayed(self):
            return True

        def get_attribute(self, name):
            raise StaleElementReferenceException("DOM update in progress")

    class Driver:
        def find_elements(self, by, selector):
            return [Card()]

    assert not _additional_reviews_loaded(
        Driver(),
        ".review-card",
        "<article>previous snapshot</article>",
    )


def test_show_more_stale_click_waits_for_visible_content_change():
    from selenium.common.exceptions import StaleElementReferenceException

    class ShowMore:
        text = "Show More"

        def is_displayed(self):
            return True

        def click(self):
            raise StaleElementReferenceException("button replaced after activation")

    class Driver:
        def find_elements(self, by, selector):
            return [ShowMore()]

        def execute_script(self, script, element):
            return None

    assert _click_show_more(Driver()) is True


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
        "title_source": "source",
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
    assert review["title_source"] == "source"
    assert review["review_text"] == "The washer runs quietly and cleans well."
    assert review["date"] == "2025-03-14"
    assert review["rating"] == 4.0
    assert review["reviewer_name"] == "Jordan"
    assert len(str(review["primary_key"])) == 64


def test_saved_visible_review_pages_extract_and_deduplicate_records():
    html = b"""
    <ul>
      <li class="review_abc" data-automation="review-list-item">
        <p class="sr-only">Customer rating: 5 out of 5 stars</p>
        <h3 class="reviewTitle_abc">Great value</h3>
        <div class="reviewerInfo_abc">Reviewed by Jordan - May 2, 2026</div>
        <time datetime="2026-05-02T10:00:00Z"></time>
        <div class="reviewContent_abc">Fast and reliable laptop.</div>
      </li>
    </ul>
    """
    product_url = "https://www.bestbuy.ca/en-ca/product/example/123456"

    reviews = parse_saved_review_pages(
        [("helpful.html", html), ("newest.html", html)],
        product_url,
    )

    assert len(reviews) == 1
    review = reviews.iloc[0]
    assert review["title"] == "Great value"
    assert review["review_text"] == "Fast and reliable laptop."
    assert review["reviewer_name"] == "Jordan"
    assert review["date"] == "2026-05-02"
    assert review["rating"] == 5
    assert review["source"] == product_url
    assert len(review["primary_key"]) == 64


def test_saved_review_page_rejects_missing_required_fields():
    html = b"""
    <article data-review-id="review-1">
      <h3>Good screen</h3>
      <p class="review-text">The screen is bright.</p>
      <time datetime="2026-05-02"></time>
      <p class="sr-only">Customer rating: 4 out of 5 stars</p>
    </article>
    """

    try:
        parse_saved_review_pages(
            [("incomplete.html", html)],
            "https://www.bestbuy.ca/en-ca/product/example/123456",
        )
    except ValueError as exc:
        assert "reviewer_name" in str(exc)
    else:
        raise AssertionError("A saved record with missing required fields must fail.")


def test_saved_review_page_requires_supported_review_cards():
    try:
        parse_saved_review_pages(
            [("empty.html", b"<html><body>No review cards</body></html>")],
            "https://www.bestbuy.ca/en-ca/product/example/123456",
        )
    except ValueError as exc:
        assert "No supported visible review cards" in str(exc)
    else:
        raise AssertionError("An HTML page without review cards must fail.")


def test_saved_review_page_enforces_upload_size_limit():
    oversized_page = b"x" * (MAX_SAVED_REVIEW_PAGE_BYTES + 1)

    try:
        parse_saved_review_pages(
            [("oversized.html", oversized_page)],
            "https://www.bestbuy.ca/en-ca/product/example/123456",
        )
    except ValueError as exc:
        assert "20 MB per-page limit" in str(exc)
    else:
        raise AssertionError("An oversized saved review page must be rejected.")


def test_repeated_data_testid_does_not_collapse_distinct_reviews():
    html = """
    <article id="review-card" data-testid="review-card">
      <h3>Quiet operation</h3><p class="review-text">Runs quietly.</p>
    </article>
    <article id="review-card" data-testid="review-card">
      <h3>Easy setup</h3><p class="review-text">Simple to install.</p>
    </article>
    """
    reviews = parse_review_cards(
        html,
        "https://www.bestbuy.ca/en-ca/product/example/123",
        review_card_selector="[data-testid='review-card']",
    )
    assert len(reviews) == 2
    assert len({review["primary_key"] for review in reviews}) == 2


def test_missing_source_title_gets_transparent_text_derived_title():
    html = """
    <article class="review-item" data-review-id="R456">
      <p class="review-text">[This review was collected as part of a promotion.]
        We've only been using this item for a couple of weeks, but so far so good.
        Nothing fancy, but affordable and user friendly.</p>
      <time datetime="2025-03-14T10:00:00Z">March 14, 2025</time>
      <span aria-label="Rated 5 out of 5 stars"></span>
      <span class="reviewer">Taylor</span>
    </article>
    """

    review = parse_review_cards(
        html,
        "https://www.bestbuy.ca/en-ca/product/example/123",
    )[0]

    assert review["title"] == (
        "We've only been using this item for a couple of weeks, but so far so good."
    )
    assert review["title_source"] == "generated_from_review_text"
