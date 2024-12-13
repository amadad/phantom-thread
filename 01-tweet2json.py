import os
import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from twikit import Client

# Environment variables
EMAIL = os.getenv('X_EMAIL')
USERNAME = os.getenv('X_USERNAME')
PASSWORD = os.getenv('X_PASSWORD')

class TweetEntity(BaseModel):
    """Tweet entity information"""
    type: str = Field(description="Type of entity (hashtag, mention, url, etc)")
    text: str = Field(description="Text of the entity")
    url: Optional[str] = Field(None, description="URL if entity is a link")
    indices: Optional[tuple[int, int]] = Field(None, description="Start and end indices in the tweet text")
    expanded_url: Optional[str] = Field(None, description="Expanded URL if different from display URL")
    display_url: Optional[str] = Field(None, description="Display version of the URL")
    media_url: Optional[str] = Field(None, description="URL of media content if present")
    screen_name: Optional[str] = Field(None, description="Screen name for user mentions")
    name: Optional[str] = Field(None, description="Full name for user mentions")

class Tweet(BaseModel):
    """Individual tweet data"""
    time: str = Field(description="Time of tweet in HH:MM AM/PM format")
    text: str = Field(description="Full tweet text")
    url: str = Field(description="URL of the tweet")
    entities: List[TweetEntity] = Field(default_factory=list, description="Entities in the tweet")
    retweet_count: int = Field(default=0, description="Number of retweets")
    favorite_count: int = Field(default=0, description="Number of likes")
    reply_count: int = Field(default=0, description="Number of replies")
    quote_count: int = Field(default=0, description="Number of quote tweets")
    source: str = Field(default="Unknown", description="Source of the tweet")

class DailyTweets(BaseModel):
    """Collection of tweets for a single day"""
    date: str = Field(description="Date in YYYY-MM-DD format")
    tweets: List[Tweet] = Field(default_factory=list, description="List of tweets for this day")

class WeeklyTweets(BaseModel):
    """Weekly collection of tweets"""
    week: str = Field(description="Week range in YYYY-MM-DD_to_YYYY-MM-DD format")
    author: str = Field(description="Twitter username")
    tweets: List[DailyTweets] = Field(default_factory=list, description="List of daily tweet collections")

class TweetAgent:
    """Agent for collecting and organizing tweets"""
    def __init__(self):
        self.client = Client(language="en-US")
        
    async def login(self):
        """Login to Twitter"""
        if not all([EMAIL, USERNAME, PASSWORD]):
            raise ValueError("Missing environment variables. Please set X_EMAIL, X_USERNAME, and X_PASSWORD.")
            
        print("Attempting login...")
        await self.client.login(
            auth_info_1=EMAIL,
            auth_info_2=USERNAME,
            password=PASSWORD
        )
        print("Login successful")
        
    async def get_user_tweets(self, username: str, target_date: datetime) -> List[Tweet]:
        """Get tweets for a specific user and date"""
        print(f"Fetching tweets for {username} on {target_date.date()}...")
        
        try:
            # First get the user ID
            user = await self.client.get_user_by_screen_name(username)
            if not user:
                raise ValueError(f"Could not find user @{username}")
            
            user_id = user.id
            print(f"Found user ID: {user_id}")
            
            # Get user tweets using the user object's get_tweets method
            print("Fetching tweets...")
            result = await user.get_tweets(tweet_type="tweets")
            if not result:
                raise ValueError(f"Could not get tweets for @{username}")
            
            # Convert Result object to list
            all_tweets = list(result)  # Result object is directly iterable
            print(f"Total tweets fetched: {len(all_tweets)}")
            
            # Filter tweets for target date
            start_time = datetime.combine(target_date.date(), datetime.min.time()).replace(tzinfo=timezone.utc)
            end_time = datetime.combine(target_date.date(), datetime.max.time()).replace(tzinfo=timezone.utc)
            
            print(f"\nLooking for tweets between:")
            print(f"Start: {start_time} ({start_time.timestamp()})")
            print(f"End: {end_time} ({end_time.timestamp()})")
            
            filtered_tweets = []
            for tweet in all_tweets:
                # Parse created_at string to datetime
                if not hasattr(tweet, 'created_at'):
                    continue
                
                # Parse the tweet's created_at string
                try:
                    # Example format: 'Thu Dec 12 02:47:52 +0000 2024'
                    tweet_time = datetime.strptime(tweet.created_at, '%a %b %d %H:%M:%S %z %Y')
                    print(f"Tweet ID: {tweet.id}, Created at: {tweet_time} ({tweet_time.timestamp()})")
                    
                    # Check if tweet is from target date
                    if start_time <= tweet_time <= end_time:
                        print(f"Found matching tweet: {tweet.id}")
                        
                        # Convert entities to our model
                        entities = []
                        if hasattr(tweet, 'entities'):
                            print(f"\nProcessing entities for tweet {tweet.id}:")
                            for entity_type, entity_list in tweet.entities.items():
                                print(f"Entity type: {entity_type}")
                                print(f"Entities: {entity_list}")
                                
                                for entity in entity_list:
                                    entity_data = {
                                        'type': entity_type,
                                        'text': entity.get('text', ''),
                                        'indices': tuple(entity.get('indices', [0, 0])),
                                        'url': entity.get('url'),
                                        'expanded_url': entity.get('expanded_url'),
                                        'display_url': entity.get('display_url'),
                                        'media_url': entity.get('media_url_https'),
                                        'screen_name': entity.get('screen_name'),
                                        'name': entity.get('name')
                                    }
                                    entities.append(TweetEntity(**entity_data))
                                    print(f"Added entity: {entity_data}")
                        
                        # Get full text, handling retweets properly
                        if hasattr(tweet, 'retweeted_tweet') and tweet.retweeted_tweet:
                            tweet_text = f"RT @{tweet.retweeted_tweet.user.screen_name}: {tweet.retweeted_tweet.full_text}"
                        else:
                            tweet_text = getattr(tweet, 'full_text', getattr(tweet, 'text', ''))
                        
                        # Create Tweet model
                        tweet_data = Tweet(
                            time=tweet_time.strftime('%I:%M %p'),
                            text=tweet_text,
                            url=f"https://twitter.com/{username}/status/{tweet.id}",
                            entities=entities,
                            retweet_count=getattr(tweet, 'retweet_count', 0),
                            favorite_count=getattr(tweet, 'favorite_count', 0),
                            reply_count=getattr(tweet, 'reply_count', 0),
                            quote_count=getattr(tweet, 'quote_count', 0),
                            source=getattr(tweet, 'source', "Unknown")
                        )
                        filtered_tweets.append(tweet_data)
                except ValueError as e:
                    print(f"Error parsing date for tweet {tweet.id}: {e}")
                    continue
            
            print(f"Found {len(filtered_tweets)} tweets for {target_date.date()}")
            return filtered_tweets
            
        except Exception as e:
            print(f"Error fetching tweets: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return []

    async def collect_weekly_tweets(self, username: str, start_date: datetime) -> WeeklyTweets:
        """Collect a week of tweets starting from start_date"""
        await self.login()
        
        week_start = start_date - timedelta(days=start_date.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_data = WeeklyTweets(
            week=f"{week_start.strftime('%Y-%m-%d')}_to_{week_end.strftime('%Y-%m-%d')}",
            author=f"@{username}",
            tweets=[]
        )
        
        for i in range(7):
            target_date = week_start + timedelta(days=i)
            print(f"\nProcessing {target_date.date()}")
            
            tweets = await self.get_user_tweets(username, target_date)
            if tweets:
                daily_tweets = DailyTweets(
                    date=target_date.strftime('%Y-%m-%d'),
                    tweets=tweets
                )
                weekly_data.tweets.append(daily_tweets)
            
            await asyncio.sleep(1)  # Rate limiting
            
        return weekly_data

async def main():
    """Main function to collect tweets"""
    agent = TweetAgent()
    
    # Get current date in UTC
    today = datetime.now(timezone.utc)
    print(f"\nCurrent UTC time: {today}")
    
    # Calculate start date (last week)
    start_date = today - timedelta(days=7)
    print(f"Date minus 7 days: {start_date}")
    
    # Align to start of week (Monday)
    start_date = start_date - timedelta(days=start_date.weekday())
    print(f"Aligned to Monday: {start_date}")
    
    print(f"\nCollecting tweets from {start_date.date()} to {(start_date + timedelta(days=6)).date()}")
    
    try:
        weekly_tweets = await agent.collect_weekly_tweets('syramadad', start_date)
        
        # Save to file
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filename = output_dir / f"{today.strftime('%m-%d-%y')}-madad.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(weekly_tweets.model_dump(), f, ensure_ascii=False, indent=4)
            
        print(f"\nTweets saved to {filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())