from fastapi import FastAPI
from apify_client import ApifyClient
import traceback
import os

app = FastAPI()

# Safely pull the token from Render's Environment Variables
apify_token = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(apify_token)


@app.get("/get_price")
def get_price(origin: str, dest: str, date: str):
    try:
        run_input = {
            "origin": origin,
            "destination": dest,
            "departureDate": date,
            "cabinClass": "economy",
            "currency": "MYR",
            "adults": 1,
            "maxResults": 10,
        }

        run = client.actor("automation-lab/google-flights-scraper").call(
            run_input=run_input
        )

        # Dynamically extract the dataset ID
        dataset_id = getattr(run, "default_dataset_id", None) or getattr(
            run, "defaultDatasetId", None
        )
        if not dataset_id and isinstance(run, dict):
            dataset_id = run.get("defaultDatasetId")

        dataset_items = client.dataset(dataset_id).list_items().items

        if not dataset_items:
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        direct_flights = [f for f in dataset_items if f.get("stops") == 0]

        if not direct_flights:
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

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
