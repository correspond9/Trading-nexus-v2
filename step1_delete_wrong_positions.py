import requests
import json

# Login as admin
login_response = requests.post(
    "https://tradingnexus.pro/api/v2/auth/login",
    json={"mobile": "9999999999", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

user_id = "6785692d-8f36-4183-addb-16c96ea95a88"

# Delete the 3 wrong duplicate closed positions
wrong_positions = [
    "6618f140-f4f6-4c70-9888-2d7d7fc23ff3",  # Smartworks CLOSED qty=0
    "4db6c512-a392-4a89-860c-393a7b2dc422",  # FIVE STAR CLOSED qty=0
    "0f688f3e-d59a-47f6-a92b-4f00a51f2a98",  # DILIP BUILDCON CLOSED qty=0
]

print("Deleting 3 wrong closed positions...")
response = requests.post(
    f"https://tradingnexus.pro/api/v2/admin/users/{user_id}/positions/delete-specific",
    headers=headers,
    json={"position_ids": wrong_positions}
)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
