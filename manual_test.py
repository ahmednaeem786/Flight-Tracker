from backend.main import get_price

origin = "KUL"
dest = "KHI"
date = "2027-02-27"

print(f"Querying flights for {origin} -> {dest} on {date}...")
result = get_price(origin=origin, dest=dest, date=date)
print(result)
