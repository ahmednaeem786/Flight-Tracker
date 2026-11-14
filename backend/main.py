from fastapi import FastAPI
from apify_client import ApifyClient
from dotenv import load_dotenv
import os
from pathlib import Path
import traceback

app = FastAPI()

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
apify_token = os.getenv("APIFY_API_TOKEN")

if not apify_token:
    raise RuntimeError("APIFY_API_TOKEN is missing from the .env file")

client = ApifyClient(apify_token)


@app.get("/get_price")
def get_price(origin: str, dest: str, date: str):
    try:
        # Prepare the input for the Apify Google Flights Scraper Actor
        run_input = {
            "origin": origin,
            "destination": dest,
            "departureDate": date,  # Already in YYYY-MM-DD format
            "cabinClass": "economy",
            "currency": "MYR",
            "adults": 1,
            "maxResults": 10,  # Keep low to speed up the scrape
        }

        # Start the Actor and wait for it to finish (this takes 10-25 seconds)
        run = client.actor("automation-lab/google-flights-scraper").call(
            run_input=run_input
        )

        # Fetch the results from the Actor's dataset
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items

        if not dataset_items:
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        # Filter for non-stop flights manually just in case
        direct_flights = [f for f in dataset_items if f.get("stops") == 0]

        if not direct_flights:
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        # The actor usually returns them sorted by price, but let's be safe
        cheapest_flight = min(
            direct_flights, key=lambda x: x.get("price", float("inf"))
        )

        return {
            "route": f"{origin} -> {dest}",
            "lowest_price": f"RM {cheapest_flight['price']}",
        }

    except Exception as e:
        return {
            "error_type": type(e).__name__,
            "error_detail": str(e),
            "traceback": traceback.format_exc(),
        }
