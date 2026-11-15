import os
import json
import requests
import re
import traceback
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

GIST_ID = os.getenv("GIST_ID")
GIST_TOKEN = os.getenv("GIST_TOKEN")


def update_gist(price_data):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {GIST_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"files": {"flight_price.json": {"content": json.dumps(price_data)}}}
    requests.patch(url, headers=headers, json=payload)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Emulate a standard Windows Chrome browser
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        # Apply stealth to bypass basic Cloudflare checks
        stealth_sync(page)

        origin, dest, date = "KUL", "KHI", "2027-02-27"

        try:
            # Trip.com's URL structure is very scraper-friendly
            url = f"https://my.trip.com/flights/{origin.lower()}-to-{dest.lower()}/tickets-{origin.lower()}-{dest.lower()}?FlightWay=OW&ddate={date}"

            # Go to the page and wait for the network to settle
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Trip.com uses both "MYR" and "RM". Wait for either to appear.
            page.wait_for_selector("text=/MYR|RM/", timeout=25000)

            # Scrape the entire page content to catch all prices
            content = page.content()

            # Find all numbers preceded by MYR or RM
            raw_prices = re.findall(r"(?:MYR|RM)\s?([0-9,.]+)", content)

            clean_prices = []
            for text in raw_prices:
                try:
                    num_str = "".join(c for c in text if c.isdigit() or c == ".")
                    num_str = num_str.rstrip(".")
                    if num_str and float(num_str) > 50:  # Ignore tiny add-on fees
                        clean_prices.append(float(num_str))
                except ValueError:
                    continue

            lowest_price = min(clean_prices) if clean_prices else "Hidden"
            price_str = (
                f"RM {lowest_price:g}"
                if isinstance(lowest_price, float)
                else lowest_price
            )

            output = {"route": f"{origin} -> {dest}", "lowest_price": price_str}

        except Exception as e:
            print("❌ SCRAPER CRASHED! Saving screenshot...")
            print(traceback.format_exc())
            page.screenshot(path="crash_screenshot.png", full_page=True)
            output = {"route": f"{origin} -> {dest}", "lowest_price": "Scraper Error"}

        browser.close()
        update_gist(output)


if __name__ == "__main__":
    run()
