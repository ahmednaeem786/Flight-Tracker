from fastapi import FastAPI
from fast_flights import FlightQuery, create_query, get_flights

app = FastAPI()


@app.get("/get_price")
def get_price(origin: str, dest: str, date: str):
    try:
        flight = FlightQuery(date=date, from_airport=origin, to_airport=dest)
        query = create_query(flights=[flight], currency="MYR")

        # The library will crash right here if Google hides the price array
        result = get_flights(query)

        if not result or not getattr(result, "flights", None):
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        # Filter for non-stop flights manually
        direct_flights = [f for f in result.flights if getattr(f, "is_direct", False)]

        if not direct_flights:
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        cheapest = direct_flights[0]
        return {"route": f"{origin} -> {dest}", "lowest_price": f"RM {cheapest.price}"}

    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__

        # Patch 1: Batik Air / Budget airline missing price array
        if "list index out of range" in error_msg or error_type == "IndexError":
            return {"route": f"{origin} -> {dest}", "lowest_price": "Hidden"}

        # Patch 2: Google block or completely empty results page
        elif (
            "'NoneType' object is not subscriptable" in error_msg
            or error_type == "TypeError"
        ):
            return {"route": f"{origin} -> {dest}", "lowest_price": "N/A"}

        # Fallback for any other unexpected crashes
        return {"route": f"{origin} -> {dest}", "lowest_price": "Error"}
