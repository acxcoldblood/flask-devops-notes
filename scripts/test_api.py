import urllib.request
import urllib.error
import json
import sys

# Configuration
BASE_URL = "http://localhost/api"

def test_api(token):
    headers = {
        "X-API-Token": token,
        "Content-Type": "application/json"
    }

    print(f"Testing API with Token: {token[:5]}...")

    # 1. Test GET /api/notes
    print("\n[1] Testing GET /api/notes...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/notes", headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"SUCCESS: Found {data.get('count', 0)} notes.")
    except urllib.error.HTTPError as e:
        print(f"FAILED: {e.code} - {e.reason}")
        print(e.read().decode())
        return

    # 2. Test POST /api/notes
    print("\n[2] Testing POST /api/notes...")
    new_note = {
        "command": "echo 'Hello API'",
        "description": "Created via API Test Script",
        "category": "API Test",
        "tags": "test, api"
    }
    
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/notes", 
            data=json.dumps(new_note).encode(), 
            headers=headers, 
            method="POST"
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"SUCCESS: Note created. ID: {data.get('id')}")
            note_id = data.get('id')
    except urllib.error.HTTPError as e:
        print(f"FAILED: {e.code} - {e.reason}")
        print(e.read().decode())
        note_id = None

    # 3. Test GET /api/categories
    print("\n[3] Testing GET /api/categories...")
    try:
        req = urllib.request.Request(f"{BASE_URL}/categories", headers=headers)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print(f"SUCCESS: Categories: {data.get('categories')}")
    except urllib.error.HTTPError as e:
        print(f"FAILED: {e.code} - {e.reason}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <YOUR_API_TOKEN>")
        print("You can find your API Token in the Application Settings.")
        sys.exit(1)
        
    token = sys.argv[1]
    test_api(token)
