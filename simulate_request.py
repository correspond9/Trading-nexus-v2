import requests

url = "http://72.62.228.112:8000/api/v2/admin/backdate-position"
headers = {
    "Authorization": "Bearer 1|GQq5Q1JESHaawnDJ5kvW0lFevUgU4o2abzcH27y2b3b38466",
    "Content-Type": "application/json"
}

payload = {
    "user_id": "1234567890",  # Replace with a valid user ID
    "symbol": "LENSKART",
    "qty": 380,
    "price": 514.70,
    "trade_date": "19-02-2026",
    "trade_time": "09:30",
    "instrument_type": "EQ",
    "exchange": "NSE",
    "product_type": "MIS"
}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.json())