"""Conservative scraper for review content displayed on Best Buy Canada product pages."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

REVIEW_COLUMNS = [
    "primary_key",
    "title",
    "review_text",
    "date",
    "rating",
    "source",
    "reviewer_name",
]
SORT_OPTIONS = (
    "Most Helpful",
    "Newest",
    "Highest Rating",
    "Lowest Rating",
    "Most Relevant",
)
DEFAULT_REVIEW_CARD_SELECTORS = (
    "[data-automation='review-list-item']",
    "li[class*='review_']",
    "[data-testid*='review-card']",
    "[data-review-id]",
    "article[class*='review']",
    "[class*='reviewCard']",
    "[class*='review-item']",
)
USER_AGENT = "BestBuyReviewSentimentAnalysis/1.0 (user-initiated public-page review export)"


@dataclass(frozen=True)
class ScrapeSettings:
    product_url: str
    sort_options: tuple[str, ...] = ("Most Helpful",)
    max_pages_per_sort: int = 10
    pause_seconds: float = 1.5
    review_card_selector: str = ", ".join(DEFAULT_REVIEW_CARD_SELECTORS)
    page_load_timeout: int = 30


def validate_product_url(url: str) -> str:
    """Accept only direct Best Buy Canada product URLs, not search or other routes."""
    parsed = urlparse(url.strip())
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or hostname not in {"bestbuy.ca", "www.bestbuy.ca"}:
        raise ValueError("Use an HTTPS product URL hosted on bestbuy.ca.")
    if not parsed.path.lower().startswith("/en-ca/product/"):
        raise ValueError(
            "Use a direct /en-ca/product/ URL. Best Buy search routes are disallowed by robots.txt."
        )
    if parsed.query:
        raise ValueError("Remove query parameters and tracking codes from the product URL.")
    return parsed._replace(fragment="").geturl()


def check_robots_permission(url: str, user_agent: str = USER_AGENT) -> None:
    """Fail closed when robots.txt cannot be retrieved or disallows the product URL."""
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    clean_url = validate_product_url(url)
    robots_url = "https://www.bestbuy.ca/robots.txt"
    request = Request(robots_url, headers={"User-Agent": user_agent})
    try:
        with urlopen(request, timeout=15) as response:
            robots_text = response.read().decode("utf-8", errors="replace")
    except (URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(
            "Could not verify Best Buy robots.txt. Scraping was stopped (fail closed)."
        ) from exc

    parser = RobotFileParser(robots_url)
    parser.parse(robots_text.splitlines())
    if not parser.can_fetch(user_agent, clean_url):
        raise PermissionError(
            "Best Buy robots.txt disallows this product URL for this user agent."
        )


def _text(node: Tag | None) -> str:
    return " ".join(node.stripped_strings) if node else ""


def _first_text(card: Tag, selectors: Iterable[str]) -> str:
    for selector in selectors:
        node = card.select_one(selector)
        value = _text(node)
        if value:
            return value
    return ""


def _date_value(card: Tag) -> str:
    time_node = card.select_one("time[datetime], time")
    raw = (time_node.get("datetime") or _text(time_node)) if time_node else ""
    if not raw:
        raw = _first_text(
            card,
            [
                "[class*='locationAndTime']",
                "[class*='date']",
                "[data-testid*='date']",
            ],
        )
    raw = re.sub(r"^[-–]\s*", "", raw)
    if not raw:
        return ""
    parsed = pd.to_datetime(raw, errors="coerce", utc=True)
    return "" if pd.isna(parsed) else parsed.strftime("%Y-%m-%d")


def _rating_value(card: Tag) -> float | None:
    candidates: list[str] = []
    for node in card.select(
        "[aria-label], [data-rating], [class*='rating'], p[class*='sr-only']"
    ):
        for attribute in ("aria-label", "data-rating", "title"):
            value = node.get(attribute)
            if value:
                candidates.append(str(value))
        candidates.append(_text(node))

    for candidate in candidates:
        match = re.search(r"(?<!\d)([1-5](?:\.\d+)?)\s*(?:out of 5|/5|stars?)", candidate, re.I)
        if not match:
            match = re.search(r"(?:rated|rating)\s*[:\-]?\s*([1-5](?:\.\d+)?)", candidate, re.I)
        if match:
            value = float(match.group(1))
            if 1 <= value <= 5:
                return value
    return None


def _visible_review_html(driver: webdriver.Chrome, selector: str) -> str:
    """Serialize only review cards Selenium reports as visible in the browser."""
    visible_cards = (
        element.get_attribute("outerHTML")
        for element in driver.find_elements(By.CSS_SELECTOR, selector)
        if element.is_displayed()
    )
    return "\n".join(markup for markup in visible_cards if markup)


def parse_review_cards(
    html: str,
    product_url: str,
    source: str = "Best Buy Canada",
    review_card_selector: str | None = None,
) -> list[dict[str, object]]:
    """Extract review fields from visible review-card markup."""
    soup = BeautifulSoup(html, "html.parser")
    cards: list[Tag] = []
    seen_cards: set[int] = set()
    selectors = [review_card_selector] if review_card_selector else DEFAULT_REVIEW_CARD_SELECTORS
    for selector in selectors:
        for card in soup.select(selector):
            marker = id(card)
            if marker not in seen_cards:
                cards.append(card)
                seen_cards.add(marker)

    records: list[dict[str, object]] = []
    for card in cards:
        review_text = _first_text(
            card,
            [
                "[data-testid*='review-text']",
                "[class*='reviewContent']",
                "[class*='reviewText']",
                "[class*='review-text']",
                "[class*='comment']",
            ],
        )
        if not review_text:
            continue

        title = _first_text(
            card,
            [
                "[data-testid*='review-title']",
                "[class*='reviewTitle']",
                "[class*='review-title']",
                "h3",
                "h2",
            ],
        )
        reviewer_text = _first_text(
            card,
            [
                "[data-testid*='reviewer']",
                "[class*='author']",
                "[class*='reviewerInfo']",
                "[class*='reviewer']",
            ],
        )
        reviewer_match = re.search(
            r"\bReviewed by\s+(.+?)(?:\s+[-–]\s*|$)", reviewer_text, re.I
        )
        reviewer_name = (
            reviewer_match.group(1).strip()
            if reviewer_match
            else reviewer_text.removeprefix("Verified Buyer").strip()
        )
        date_value = _date_value(card)
        rating = _rating_value(card)

        external_id = next(
            (
                str(card.get(attr))
                for attr in ("data-review-id", "data-testid", "id")
                if card.get(attr)
            ),
            "",
        )
        identity = external_id or "|".join(
            (product_url, date_value, title, review_text, reviewer_name)
        )
        primary_key = external_id or hashlib.sha256(identity.encode("utf-8")).hexdigest()
        records.append(
            {
                "primary_key": primary_key,
                "title": title,
                "review_text": review_text,
                "date": date_value,
                "rating": rating,
                "source": source,
                "reviewer_name": reviewer_name,
            }
        )
    return records


def _select_sort(driver: webdriver.Chrome, label: str, timeout: int) -> None:
    """Use only visible page controls; never call private endpoints."""
    wait = WebDriverWait(driver, timeout)
    try:
        select_element = wait.until(
            conditions.presence_of_element_located((By.CSS_SELECTOR, "select"))
        )
        select = Select(select_element)
        match = next(
            (
                option
                for option in select.options
                if option.text.strip().casefold() == label.casefold()
            ),
            None,
        )
        if match:
            select.select_by_visible_text(match.text)
            return
    except TimeoutException:
        pass

    matches = driver.find_elements(
        By.XPATH,
        "//*[self::button or self::a or @role='button' or @role='option']",
    )
    exact = [
        element
        for element in matches
        if element.is_displayed() and element.text.strip().casefold() == label.casefold()
    ]
    if exact:
        exact[0].click()
        return
    raise RuntimeError(
        f"Could not find a visible sort control for '{label}'. "
        "The page may have changed; stop rather than guessing or using hidden endpoints."
    )


def _click_show_more(
    driver: webdriver.Chrome, *, consent_retry: bool = False
) -> bool:
    candidates = driver.find_elements(
        By.XPATH,
        "//*[self::button or self::a or @role='button']",
    )
    for element in candidates:
        if element.is_displayed() and "show more" in element.text.strip().casefold():
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
                element,
            )
            time.sleep(0.25)
            try:
                element.click()
            except ElementClickInterceptedException as exc:
                if not consent_retry and _reject_optional_cookies(driver):
                    return _click_show_more(driver, consent_retry=True)
                raise PermissionError(
                    "The visible Show More control is blocked by a page overlay or consent "
                    "dialog. Resolve it using the site's visible controls and retry; the scraper "
                    "will not dismiss or bypass it."
                ) from exc
            return True
    return False


def _visible_consent_overlay(driver: webdriver.Chrome) -> bool:
    overlays = driver.find_elements(By.CSS_SELECTOR, "#onetrust-pc-dark-filter")
    return any(overlay.is_displayed() for overlay in overlays)


def _reject_optional_cookies(driver: webdriver.Chrome, timeout: float = 5.0) -> bool:
    """Use Best Buy's visible reject-all control when its OneTrust overlay is active."""
    deadline = time.monotonic() + timeout
    overlay_visible = _visible_consent_overlay(driver)
    while overlay_visible:
        candidates = driver.find_elements(
            By.CSS_SELECTOR,
            "#onetrust-reject-all-handler, #onetrust-banner-sdk button",
        )
        reject_button = next(
            (
                element
                for element in candidates
                if element.is_displayed()
                and element.is_enabled()
                and (
                    element.get_attribute("id") == "onetrust-reject-all-handler"
                    or re.fullmatch(
                        r"reject all(?: optional)?(?: cookies)?",
                        " ".join(element.text.split()).casefold(),
                    )
                    is not None
                )
            ),
            None,
        )
        if reject_button:
            reject_button.click()
            while time.monotonic() < deadline:
                if not _visible_consent_overlay(driver):
                    return True
                time.sleep(0.1)
            if not _visible_consent_overlay(driver):
                return True
            raise RuntimeError(
                "Best Buy's visible reject-optional-cookies control did not dismiss the "
                "consent overlay. No collection was performed."
            )
        if time.monotonic() >= deadline:
            break
        time.sleep(0.1)
        overlay_visible = _visible_consent_overlay(driver)

    if overlay_visible:
        raise RuntimeError(
            "Best Buy is showing a cookie-consent overlay without a visible Reject All "
            "control. Select the site's consent preference manually and retry; the scraper "
            "will not accept optional cookies or dismiss the overlay."
        )
    return False


def _raise_if_access_denied(driver: webdriver.Chrome) -> None:
    """Stop when visible page text indicates blocking or an access challenge."""
    body_text = driver.find_element(By.TAG_NAME, "body").text.casefold()
    markers = (
        "access denied",
        "you don't have permission to access",
        "you do not have permission to access",
        "unusual traffic",
        "verify you are human",
        "complete the captcha",
    )
    if any(marker in body_text for marker in markers):
        raise PermissionError(
            "Best Buy displayed an access-denied or challenge page. Collection stopped; "
            "do not retry through proxies, CAPTCHA workarounds, or other evasion."
        )


def _chromium_binary() -> str | None:
    binary = os.environ.get("CHROME_BIN")
    if binary:
        return binary
    for candidate in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        binary = shutil.which(candidate)
        if binary:
            return binary
    return None


def _review_page_url(product_url: str) -> str:
    """Resolve the public review page linked from a product page."""
    parsed = urlparse(product_url)
    path = parsed.path.rstrip("/")
    if not path.lower().endswith("/review"):
        path = f"{path}/review"
    return parsed._replace(path=path, fragment="").geturl()


def scrape_reviews(
    settings: ScrapeSettings,
    *,
    policy_confirmed: bool,
    headless: bool = True,
) -> pd.DataFrame:
    """Scrape visible review cards from each selected public sort view."""
    product_url = validate_product_url(settings.product_url)
    review_page_url = validate_product_url(_review_page_url(product_url))
    if not policy_confirmed:
        raise PermissionError(
            "Confirm that your use complies with Best Buy's current terms and applicable law."
        )
    if not settings.sort_options or any(option not in SORT_OPTIONS for option in settings.sort_options):
        raise ValueError(f"Choose one or more supported sorts: {', '.join(SORT_OPTIONS)}.")
    if not 1 <= settings.max_pages_per_sort <= 100:
        raise ValueError("max_pages_per_sort must be between 1 and 100.")
    if not 1 <= settings.pause_seconds <= 30:
        raise ValueError("pause_seconds must be between 1 and 30.")

    check_robots_permission(review_page_url)

    options = ChromeOptions()
    options.page_load_strategy = "eager"
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1000")
    options.add_argument(f"--user-agent={USER_AGENT}")
    chrome_binary = _chromium_binary()
    if chrome_binary:
        options.binary_location = chrome_binary
    # Selenium Manager/Chrome are not allowed to work around access controls.
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.page_load_timeout)
    collected: dict[str, dict[str, object]] = {}
    try:
        for sort_label in settings.sort_options:
            driver.get(review_page_url)
            _raise_if_access_denied(driver)
            _reject_optional_cookies(driver)
            try:
                WebDriverWait(driver, settings.page_load_timeout).until(
                    lambda browser: bool(
                        _visible_review_html(browser, settings.review_card_selector)
                    )
                )
            except TimeoutException as exc:
                raise RuntimeError(
                    "No visible review cards appeared. The page may require manual review, "
                    "or its markup may have changed; no hidden API or bypass was attempted."
                ) from exc

            _select_sort(driver, sort_label, settings.page_load_timeout)
            time.sleep(settings.pause_seconds)

            for page_number in range(settings.max_pages_per_sort):
                _raise_if_access_denied(driver)
                _reject_optional_cookies(driver)
                html = _visible_review_html(driver, settings.review_card_selector)
                if not html:
                    raise RuntimeError(
                        "No visible review cards remain. Collection stopped to avoid reading "
                        "hidden or unavailable review content."
                    )
                for review in parse_review_cards(
                    html,
                    product_url,
                    review_card_selector=settings.review_card_selector,
                ):
                    collected.setdefault(str(review["primary_key"]), review)
                if page_number + 1 >= settings.max_pages_per_sort:
                    break
                if not _click_show_more(driver):
                    break
                try:
                    WebDriverWait(driver, settings.page_load_timeout).until(
                        lambda browser: _visible_review_html(
                            browser, settings.review_card_selector
                        )
                        != html
                    )
                except TimeoutException as exc:
                    _raise_if_access_denied(driver)
                    raise RuntimeError(
                        "The visible 'Show More' control did not load additional page content. "
                        "Collection stopped to avoid reporting an incomplete page as complete."
                    ) from exc
                time.sleep(settings.pause_seconds)

        frame = pd.DataFrame(collected.values(), columns=REVIEW_COLUMNS)
        if frame.empty:
            raise RuntimeError(
                "No review text was extracted. Verify the public page and review-card selector."
            )
        frame["date"] = frame["date"].astype("string")
        return frame.sort_values(["date", "primary_key"], ascending=[False, True]).reset_index(
            drop=True
        )
    finally:
        driver.quit()
