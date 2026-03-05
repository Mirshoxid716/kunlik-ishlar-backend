import random
import requests

data = {
    "title": "ntntntyj",
    "wage": "25832473",
    "working_hours": "2828",
    "address": "jhcgmgumgum",
    "service_fee": "2822",
    "client_phone": "28\\2\\2\\2",
    "required_workers": "5",
    "unical_id": str(random.randint(10000, 99999)),
    "description": "gfkdutmgxh",
    "transport": "",
    "location_url": ""
}

try:
    resp = requests.post("http://localhost:8000/api/jobs/jobs/", json=data)
    print("Status Code:", resp.status_code)
    try:
        print("Response JSON:", resp.json())
    except Exception:
        print("Response Text:", resp.text[:500])
except Exception as e:
    print("Request failed:", e)
