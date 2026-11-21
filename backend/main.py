import os
import json
import requests
from datetime import datetime, timezone, timedelta
from apify_client import ApifyClient

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

GIST_ID = os.getenv("GIST_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GIST_TOKEN")
APIFY_TOKEN = os.getenv("APIFY_API_TOKEN")

ACTOR_ID = "p8tZlhUqCGtzZXHzj"
OUTBOUND_DATE = "2027-02-27"  # KUL -> KHI (OD135)
RETURN_DATE = "2027-03-13"  # KHI -> KUL (OD136)


def update_gist(price_data):
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "files": {"flight_price.json": {"content": json.dumps(price_data, indent=2)}}
    }
    res = requests.patch(url, headers=headers, json=payload)
    res.raise_for_status()


def fetch_leg(client, origin, destination, date_str):
    run_input = {
        "origin": origin,
        "destination": destination,
        "site": "kayak",
        "departureDate": date_str,
        "adults": 1,
        "children": 0,
        "cabinClass": "economy",
        "sortBy": "best",
        "maxResults": 10,  # Capped to 10 rows (~$0.01/leg)
        "maxStops": "any",
        "currency": "MYR",
        "allProviders": False,  # Keeps row count low
        "routes": [],
        "proxyConfiguration": {"useApifyProxy": True},
    }

    actor_run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = (
        getattr(actor_run, "default_dataset_id", None) or actor_run["defaultDatasetId"]
    )
    items = client.dataset(dataset_id).list_items().items

    valid_flights = [f for f in items if f.get("price") is not None]
    direct_flights = [f for f in valid_flights if f.get("stops") == 0]

    if direct_flights:
        best_direct = min(direct_flights, key=lambda x: float(x["price"]))
        direct_price = f"RM {round(float(best_direct['price'])):,}"
        airline = best_direct.get("airline", "Direct")
    else:
        direct_price = "N/A"
        airline = "No Direct"

    if valid_flights:
        best_any = min(valid_flights, key=lambda x: float(x["price"]))
        cheapest_any = (
            f"RM {round(float(best_any['price'])):,} ({best_any.get('airline', '')})"
        )
    else:
        cheapest_any = "N/A"

    return {
        "route": f"{origin} -> {destination}",
        "date": date_str,
        "airline": airline,
        "lowest_price": direct_price,
        "cheapest_any": cheapest_any,
    }


def run():
    client = ApifyClient(APIFY_TOKEN)
    myt = timezone(timedelta(hours=8))
    updated_at = datetime.now(myt).strftime("%d %b, %I:%M %p")

    output = {"updated_at": updated_at}

    for key, orig, dest, date_str in [
        ("outbound", "KUL", "KHI", OUTBOUND_DATE),
        ("inbound", "KHI", "KUL", RETURN_DATE),
    ]:
        try:
            output[key] = fetch_leg(client, orig, dest, date_str)
        except Exception as e:
            print(f"Error fetching {orig}->{dest}: {e}")
            output[key] = {
                "route": f"{orig} -> {dest}",
                "date": date_str,
                "lowest_price": "Error",
            }

    update_gist(output)
    print("Updated Gist:", json.dumps(output, indent=2))


if __name__ == "__main__":
    run()
