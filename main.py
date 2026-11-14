from fastapi import FastAPI
from fast_flights import FlightQuery, create_query, get_flights

app = FastAPI()


@app.get("/get_price")
def get_price(origin: str, dest: str, date: str):
    flight = FlightQuery(
        date=date, from_airport=origin, to_airport=dest, seat="economy", trip="one-way"
    )
    query = create_query(flights=[flight], currency="MYR")
    result = get_flights(query)

    # Enforce non-stop requirement
    direct_flights = [f for f in result.flights if f.is_direct]
    if not direct_flights:
        return {"error": "No non-stop flights found"}

    cheapest = direct_flights[0]
    return {"route": f"{origin} -> {dest}", "lowest_price": f"RM {cheapest.price}"}
