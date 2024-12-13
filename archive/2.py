import os
import asyncio
import json
import tweepy
from datetime import datetime, timedelta

bearer_token = os.getenv('BEARER_TOKEN')

# Verify that the bearer token is not None
if not bearer_token:
    raise ValueError("Error: BEARER_TOKEN environment variable is not set.")

client = tweepy.Client(bearer_token)

async def main(date: datetime = None):
    user_id = "2244994945"  # Replace with the user ID you want to fetch tweets for
    today = date.date() if date else datetime.now().date()
    
    # Fetch tweets from the user timeline
    response = client.get_users_tweets(user_id, max_results=100)
    tweets = response.data
    
    today_tweets = [tweet for tweet in tweets if datetime.strptime(tweet.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').date() == today]
    
    # Debug print to check fetched tweets
    print(f"Fetched {len(today_tweets)} tweets for {today}")
    for tweet in today_tweets:
        print(f"Tweet on {datetime.strptime(tweet.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').date()}: {tweet.text}")
    
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    week_str = f"{week_start.strftime('%Y-%m-%d')}_to_{week_end.strftime('%Y-%m-%d')}"
    
    filename = f"output/{week_start.strftime('%m-%d-%y')}-madad.json"
    
    os.makedirs('output', exist_ok=True)
    
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            weekly_data = json.load(f)
    else:
        weekly_data = {
            "week": week_str,
            "author": "@syramadad",
            "tweets": []
        }
    
    # Check if the date already exists in the JSON
    date_exists = any(entry["date"] == today.strftime('%Y-%m-%d') for entry in weekly_data["tweets"])
    
    if not date_exists:
        today_tweet_data = {
            "date": today.strftime('%Y-%m-%d'),
            "tweets": [
                {
                    "time": datetime.strptime(tweet.created_at, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%I:%M %p'),
                    "tweet": tweet.text,
                    "url": f"https://twitter.com/{user_id}/status/{tweet.id}"
                } for tweet in today_tweets
            ]
        }
        weekly_data["tweets"].append(today_tweet_data)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=4)
    
    print(f"Tweets appended to {filename}")

async def test_run():
    # Test run for the week 8/12-18
    start_date = datetime(2024, 8, 12)
    for i in range(7):
        test_date = start_date + timedelta(days=i)
        await main(test_date)
        await asyncio.sleep(1)  # Add a 1-second delay between each API hit

if __name__ == "__main__":
    # Uncomment the following line to perform the test run
    asyncio.run(test_run())

    # Schedule the script to run daily at 11:59 PM EST
    # import schedule
    # import time

    # schedule.every().day.at("23:59").do(lambda: asyncio.run(main()))

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
