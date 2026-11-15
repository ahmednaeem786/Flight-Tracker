import os
import json
import requests
from playwright.sync_api import sync_playwright

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
        # GitHub Actions has 7GB RAM, so Chromium runs flawlessly here
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        origin, dest, date = "KUL", "KHI", "2027-02-27"

        try:
            # Point this directly at Batik Air, Skyscanner, or Kayak
            # You can inject your specific Batik Air DOM clicking logic here
            page.goto(
                f"https://www.skyscanner.com.my/transport/flights/kul/khi/270227/?adultsv2=1&cabinclass=economy&rtn=0&preferdirects=true",
                wait_until="networkidle",
            )

            # Extract the raw text containing RM
            page.wait_for_selector("text=/RM[0-9,]+/", timeout=20000)
            price_texts = page.locator("text=/RM[0-9,]+/").all_inner_texts()

            clean_prices = []
            for text in price_texts:
                try:
                    num_str = "".join(c for c in text if c.isdigit() or c == ".")
                    if num_str and float(num_str) > 50:
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
            # THIS IS THE FIX: Print the exact error to the GitHub Actions console
            import traceback

            print("❌ SCRAPER CRASHED! Here is the exact error:")
            print(traceback.format_exc())

            output = {"route": f"{origin} -> {dest}", "lowest_price": "Scraper Error"}

        browser.close()
        update_gist(output)


if __name__ == "__main__":
    run()
