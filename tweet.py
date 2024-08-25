import os
import asyncio
from twikit import Client, Tweet
from datetime import datetime
from typing import NoReturn

os.environ['X_EMAIL'] = 'traderfractal@gmail.com'
os.environ['X_USERNAME'] = 'traderfractal'
os.environ['X_PASSWORD'] = '059nin7t'

EMAIL = os.getenv('X_EMAIL')
USERNAME = os.getenv('X_USERNAME')
PASSWORD = os.getenv('X_PASSWORD')

# Verify that these are not None
print(f"EMAIL: {EMAIL}")
print(f"USERNAME: {USERNAME}")
print(f"PASSWORD: {'*' * len(PASSWORD) if PASSWORD else None}")

async def main():
    if not all([EMAIL, USERNAME, PASSWORD]):
        print("Error: One or more required environment variables are not set.")
        print("Please set X_EMAIL, X_USERNAME, and X_PASSWORD environment variables.")
        print("\nYou can set them using the following commands in your terminal:")
        print(f"export X_EMAIL='your_email@example.com'")
        print(f"export X_USERNAME='your_username'")
        print(f"export X_PASSWORD='your_password'")
        print("\nOr you can set them in your Python script like this:")
        print("import os")
        print("os.environ['X_EMAIL'] = 'your_email@example.com'")
        print("os.environ['X_USERNAME'] = 'your_username'")
        print("os.environ['X_PASSWORD'] = 'your_password'")
        return

    client = Client()
    try:
        await client.login(
            auth_info_1=EMAIL,
            auth_info_2=USERNAME,
            password=PASSWORD
        )
        
        user = await client.get_user_by_screen_name('syramadad')
        tweets = await user.get_tweets('Tweets', count=10)  # Adjust limit as needed
        
        today = datetime.now().date()
        today_tweets = [tweet for tweet in tweets if tweet.created_at_datetime.date() == today]
        
        filename = f"output/syramadad_{today.strftime('%Y-%m-%d')}.md"
        
        os.makedirs('output', exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Tweets by @syramadad on {today.strftime('%Y-%m-%d')}\n\n")
            for tweet in today_tweets:
                f.write(f"- {tweet.text}\n\n")
        
        print(f"Tweets saved to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())