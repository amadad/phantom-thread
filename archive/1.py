import os
import asyncio
import json
from twikit import Client, Tweet
from datetime import datetime, timedelta, time as dt_time, timezone
from typing import NoReturn
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
EMAIL = os.getenv('X_EMAIL')
USERNAME = os.getenv('X_USERNAME')
PASSWORD = os.getenv('X_PASSWORD')

# Verify that these are not None
print(f"EMAIL: {EMAIL}")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {'*' * len(PASSWORD) if PASSWORD else None}")

async def main(date: datetime = None):
    if not all([EMAIL, USERNAME, PASSWORD]):
        print("Error: One or more required environment variables are not set.")
        print("Please set X_EMAIL, X_USERNAME, and X_PASSWORD environment variables.")
        return

    client = Client()
    try:
        await client.login(
            auth_info_1=EMAIL,
            auth_info_2=USERNAME,
            password=PASSWORD
        )
        
        user = await client.get_user_by_screen_name('syramadad')
        
        today = date.date() if date else datetime.now(timezone.utc).date()
        start_time = datetime.combine(today, dt_time.min).replace(tzinfo=timezone.utc)
        end_time = datetime.combine(today, dt_time.max).replace(tzinfo=timezone.utc)
        
        all_tweets = await user.get_tweets('Tweets', count=1000)  # Increase count as needed
        today_tweets = [tweet for tweet in all_tweets if start_time <= tweet.created_at_datetime.replace(tzinfo=timezone.utc) <= end_time]
        
        print(f"Fetched {len(today_tweets)} tweets for {today}")
        
        # Determine the current week's range
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_str = f"{week_start.strftime('%Y-%m-%d')}_to_{week_end.strftime('%Y-%m-%d')}"
        
        # Create the filename
        filename = f"output/{week_start.strftime('%m-%d-%y')}-madad.json"
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
        
        # Load or initialize weekly data
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                weekly_data = json.load(f)
        else:
            weekly_data = {
                "week": week_str,
                "author": "@syramadad",
                "tweets": []
            }
        
        # Append today's tweets to the correct date entry
        date_entry = next((entry for entry in weekly_data["tweets"] if entry["date"] == today.strftime('%Y-%m-%d')), None)
        
        if not date_entry:
            date_entry = {
                "date": today.strftime('%Y-%m-%d'),
                "tweets": []
            }
            weekly_data["tweets"].append(date_entry)
        
        # Add tweets to the correct date entry
        for tweet in today_tweets:
            date_entry["tweets"].append({
                "time": tweet.created_at_datetime.strftime('%I:%M %p'),
                "tweet": tweet.text,
                "url": tweet.url if hasattr(tweet, 'url') else "N/A"
            })
        
        # Save back to JSON
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(weekly_data, f, ensure_ascii=False, indent=4)
        
        print(f"Tweets appended to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def test_run():
    # Test run for the week 9/2-9
    start_date = datetime(2024, 9, 2)
    for i in range(7):
        test_date = start_date + timedelta(days=i)
        await main(test_date)
        await asyncio.sleep(1)  # Add a 1-second delay between each API hit

if __name__ == "__main__":
    # Uncomment the following line to perform the test run
    asyncio.run(test_run())

    # Schedule the script to run daily at​