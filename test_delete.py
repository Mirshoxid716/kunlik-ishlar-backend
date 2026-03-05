import requests

BASE_URL = 'http://localhost:8000/api/jobs'

# 1. Fetch admins
response = requests.get(f"{BASE_URL}/users/")
print("GET /users/:", response.status_code)
admins = response.json()
print("Admins:", admins)

# 2. Try to find a non-superuser admin or create one
target_id = None
for admin in admins:
    if admin['username'] != 'admin':
        target_id = admin['id']
        break

if not target_id:
    print("Creating a test subadmin...")
    create_resp = requests.post(f"{BASE_URL}/users/", json={
        "username": "testdelete",
        "password": "password",
        "is_superuser": False
    })
    print("Create status:", create_resp.status_code)
    target_id = create_resp.json().get('id')

# 3. Try deleting the target admin
if target_id:
    print(f"Trying to delete admin with ID {target_id}...")
    del_resp = requests.delete(f"{BASE_URL}/users/{target_id}/")
    print("Delete status:", del_resp.status_code)
    print("Delete response:", del_resp.text)
else:
    print("Failed to find or create a target admin to delete.")
