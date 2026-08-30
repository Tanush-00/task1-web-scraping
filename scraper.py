from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
START_URL = urljoin(BASE_URL, "catalogue/page-1.html")
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "data" / "books.csv"


def fetch_page(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def parse_books(soup: BeautifulSoup, page_url: str, scraped_at: str) -> list[dict[str, str | float | int]]:
    rows: list[dict[str, str | float | int]] = []

    for book in soup.select("article.product_pod"):
        title_link = book.select_one("h3 a")
        price_node = book.select_one(".price_color")
        availability_node = book.select_one(".availability")
        if not all((title_link, price_node, availability_node)):
            continue

        title = title_link.get("title", "").strip()
        price_text = price_node.get_text(" ", strip=True).replace("£", "")
        availability = availability_node.get_text(" ", strip=True)
        rows.append(
            {
                "title": title,
                "price_gbp": float(price_text),
                "availability": availability,
                "source_page": page_url,
                "scraped_at_utc": scraped_at,
            }
        )

    return rows


def get_next_page(soup: BeautifulSoup, current_url: str) -> str | None:
    next_link = soup.select_one("li.next a")
    if not next_link:
        return None
    return urljoin(current_url, next_link.get("href", ""))


def scrape(max_pages: int | None = None, delay_seconds: float = 0.2) -> list[dict[str, str | float | int]]:
    session = requests.Session()
    session.headers.update({"User-Agent": "Task1-WebScraper/1.0 (educational project)"})

    rows: list[dict[str, str | float | int]] = []
    current_url: str | None = START_URL
    scraped_at = datetime.now(timezone.utc).isoformat()
    page_count = 0

    while current_url and (max_pages is None or page_count < max_pages):
        soup = fetch_page(session, current_url)
        rows.extend(parse_books(soup, current_url, scraped_at))
        page_count += 1
        current_url = get_next_page(soup, current_url)
        if current_url:
            time.sleep(delay_seconds)

    return rows


def save_csv(rows: list[dict[str, str | float | int]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "title",
        "price_gbp",
        "availability",
        "source_page",
        "scraped_at_utc",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape book listings from Books to Scrape.")
    parser.add_argument("--max-pages", type=int, default=None, help="Maximum pages to scrape; default is all available pages.")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between page requests in seconds.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH, help="CSV output path.")
    args = parser.parse_args()

    rows = scrape(max_pages=args.max_pages, delay_seconds=args.delay)
    save_csv(rows, args.output)
    print(f"Saved {len(rows)} records to {args.output}")


if __name__ == "__main__":
    main()
