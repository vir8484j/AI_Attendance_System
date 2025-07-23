import json
from supabase import create_client, Client
from datetime import datetime

with open("serviceAccountKey.json", "r") as f:
    config = json.load(f)

SUPABASE_URL = config["SUPABASE_URL"]
SUPABASE_KEY = config["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

data = {
    "115": {
        "id": "115",
        "name": "Virag Jain",
        "course":"MCA",
        "major": "AI",
        "starting_year": 2024,
        "total_attendance": 8,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-03-23 00:44:48"
    },
    "116": {
        "id": "116",
        "name": "Rohit Sharma",
        "course":"BTech",
        "major": "Blockchain",
        "starting_year": 2024,
        "total_attendance": 4,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-03-23 00:44:48"
    },
    "117": {
        "id": "117",
        "name": "Virat Kohli",
        "course":"MCA",
        "major": "Data Science",
        "starting_year": 2024,
        "total_attendance": 7,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-03-23 00:44:48"
    },
    "118": {
        "id": "118",
        "name": "Gautam Adani",
        "course":"MCA",
        "major": "Cyber Security",
        "starting_year": 2024,
        "total_attendance": 18,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2025-03-23 00:44:48"
    },
    "119": {
        "id": "119",
        "name": "Atul Chatter",
        "course":"BTech",
        "major": "AI",
        "starting_year": 2018,
        "total_attendance": 8,
        "standing": "G",
        "year": 4,
        "last_attendance_time": "2025-04-06 00:44:48"
    }
}

# Insert or upsert into Supabase
for key, value in data.items():
    # Convert timestamp to ISO format
    value['last_attendance_time'] = datetime.strptime(
        value['last_attendance_time'], "%Y-%m-%d %H:%M:%S"
    ).isoformat()

    try:
        # Use native upsert method
        response = supabase.table("students").upsert(value).execute()

        # Correctly handle the response
        if response.data:
            print(f"Inserted/Updated {key}: {response.data}")
        else:
            print(f"Error inserting {key}: {response}")

    except Exception as e:
        print(f"Exception during upsert for {key}: {e}")
