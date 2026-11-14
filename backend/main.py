from fastapi import FastAPI
from apify_client import ApifyClient
import traceback

app = FastAPI()

# Make sure your token is still being loaded correctly here!
client = ApifyClient("YOUR_APIFY_API_TOKEN")


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

        # --- THE FIX ---
        # Dynamically extract the dataset ID whether Apify returns a Pydantic object or a dictionary
        dataset_id = getattr(run, "default_dataset_id", None) or getattr(
            run, "defaultDatasetId", None
        )
        if not dataset_id and isinstance(run, dict):
            dataset_id = run.get("defaultDatasetId")

        # Use the safely extracted ID
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
