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
        "name": "",
        "course":"",
        "major": "",
        "starting_year": ,
        "total_attendance": ,
        "standing": "",
        "year": ,
        "last_attendance_time": ""
    },
    "116": {
        "id": "116",
        "name": "",
        "course":"",
        "major": "",
        "starting_year": ,
        "total_attendance": ,
        "standing": "",
        "year": ,
        "last_attendance_time": ""
    },
    "117": {
        "id": "117",
        "name": "",
        "course":"",
        "major": "",
        "starting_year": ,
        "total_attendance": ,
        "standing": "",
        "year": ,
        "last_attendance_time": ""
    },
    "118": {
        "id": "118",
        "name": "",
        "course":"",
        "major": "",
        "starting_year": ,
        "total_attendance": ,
        "standing": "",
        "year": ,
        "last_attendance_time": ""
    },
    "119": {
        "id": "119",
        "name": "",
        "course":"",
        "major": "",
        "starting_year": ,
        "total_attendance": ,
        "standing": "",
        "year": ,
        "last_attendance_time": ""
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
