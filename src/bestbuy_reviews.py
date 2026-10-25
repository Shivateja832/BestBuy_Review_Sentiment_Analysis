"""Conservative scraper for review content displayed on Best Buy Canada product pages."""

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
        raw = _first_text(card, ["[class*='date']", "[data-testid*='date']"])
    if not raw:
        return ""
    parsed = pd.to_datetime(raw, errors="coerce", utc=True)
    return "" if pd.isna(parsed) else parsed.strftime("%Y-%m-%d")


def _rating_value(card: Tag) -> float | None:
    candidates: list[str] = []
    for node in card.select("[aria-label], [data-rating], [class*='rating']"):
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
                "[class*='reviewText']",
                "[class*='review-text']",
                "[class*='comment']",
                "p",
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
        reviewer_name = _first_text(
            card,
            [
                "[data-testid*='reviewer']",
                "[class*='reviewer']",
                "[class*='author']",
            ],
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
        primary_key = external_id or hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
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


def _click_show_more(driver: webdriver.Chrome) -> bool:
    candidates = driver.find_elements(
        By.XPATH,
        "//*[self::button or self::a or @role='button']",
    )
    for element in candidates:
        if element.is_displayed() and "show more" in element.text.strip().casefold():
            element.click()
            return True
    return False


def scrape_reviews(
    settings: ScrapeSettings,
    *,
    policy_confirmed: bool,
    headless: bool = True,
) -> pd.DataFrame:
    """Scrape visible review cards from each selected public sort view."""
    product_url = validate_product_url(settings.product_url)
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

    check_robots_permission(product_url)

    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,1000")
    options.add_argument(f"--user-agent={USER_AGENT}")
    chrome_binary = os.environ.get("CHROME_BIN")
    if chrome_binary:
        options.binary_location = chrome_binary
    # Selenium Manager/Chrome are not allowed to work around access controls.
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(settings.page_load_timeout)
    collected: dict[str, dict[str, object]] = {}
    try:
        for sort_label in settings.sort_options:
            driver.get(product_url)
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
