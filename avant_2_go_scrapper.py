import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import os

from apscheduler.schedulers.blocking import BlockingScheduler
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

# PostgreSQL connection details
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    "host": os.environ.get("DB_HOST"),
    "port": os.environ.get("DB_PORT"),
}


API_URL = "https://api.ontime.si/api/v1/avant2go/"

FILTER_IDS = {
    "573716b50e45977e09f30c52",
    "5d36ad205513d14fe239ab8d",
    "5d1a14ef5513d14fe22a94e5",
    "6411bbb42145880788f3dd3f",
    "5841ad6dc517f11e822951c2",
}

def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def filter_data(data):
    return [item for item in data["results"] if item["avant_id"] in FILTER_IDS]

def save_to_postgresql(data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        rows = [
            (
                item["avant_id"],
                item["status"],
                item["created_date"],
                item["location_name"],
                item["lat"],
                item["lng"],
                item["free_spaces"],
                item["reservable_cars"],
                item["reserved_cars"],
                item["trend"]
            )
            for item in data
        ]

        query = """
        INSERT INTO avant_parking (
            avant_id, status, created_date, location_name, lat, lng,
            free_spaces, reservable_cars, reserved_cars, trend
        ) VALUES %s
        """
        execute_values(cur, query, rows)
        conn.commit()
        cur.close()
        conn.close()

        print(f"Data saved at {datetime.now()}")
    except psycopg2.Error as e:
        print(f"Error saving data to PostgreSQL: {e}")

def scrape_data():
    data = fetch_data()
    if data:
        filtered_data = filter_data(data)
        if filtered_data:
            save_to_postgresql(filtered_data)

# Schedule the task
scheduler = BlockingScheduler()
scheduler.add_job(scrape_data, "interval", seconds=30)

if __name__ == "__main__":
    print("Starting scheduler...")
    scheduler.start()