from fastapi import FastAPI
from fast_flights import FlightQuery, create_query, get_flights
import traceback

app = FastAPI()


@app.get("/get_price")
def get_price(origin: str, dest: str, date: str):
    try:
        # Using only supported v3.1.0 parameters.
        # max_stops=0 natively enforces non-stop flights!
        flight = FlightQuery(
            date=date, from_airport=origin, to_airport=dest, max_stops=0
        )

        # create_query usually handles global modifiers like currency
        query = create_query(flights=[flight], currency="MYR")
        result = get_flights(query)

        if not result or not getattr(result, "flights", None):
            return {"error": "No non-stop flights found."}

        cheapest = result.flights[0]
        return {"route": f"{origin} -> {dest}", "lowest_price": f"RM {cheapest.price}"}
    except Exception as e:
        return {
            "error_type": type(e).__name__,
            "error_detail": str(e),
            "traceback": traceback.format_exc(),
        }
