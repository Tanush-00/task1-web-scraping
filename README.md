# Task 1: Web Scraping

**Name:** Tanush Agarwal  
**Task:** Web Scraping  
**Language:** Python  
**Libraries:** Requests, BeautifulSoup

## Objective

Extract a structured dataset from a public web page by parsing HTML and navigating paginated results.

## Source

[Books to Scrape](https://books.toscrape.com/)

This is a public demonstration website created for web-scraping practice. The site currently presents 1,000 book results across 50 pages.

## Data collected

The scraper extracts these fields from each book listing:

- `title` — book title
- `price_gbp` — listed price in GBP
- `availability` — availability text
- `source_page` — paginated listing page where the record was collected
- `scraped_at_utc` — UTC timestamp for the scrape run

## Web navigation and HTML handling

The script:

1. Requests the first catalogue page.
2. Parses each `article.product_pod` block with BeautifulSoup.
3. Extracts the title, price, availability, from the HTML structure.
4. Follows the site's `next` pagination link.
5. Repeats until there are no more pages or `--max-pages` is reached.
6. Saves the final structured dataset as a CSV file.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run all available pages:

```bash
python src/scraper.py
```

For a smaller scrape while testing:

```bash
python src/scraper.py --max-pages 2
```

The output is written to `data/books.csv` by default.

## Included dataset

`data/books.csv` is a small collected snapshot from the public source pages used for this project. Running the scraper regenerates the CSV from the live site.
