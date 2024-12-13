import os
import asyncio
import json
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.status import Status

# API keys
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

class Tweet(BaseModel):
    """Individual tweet data"""
    time: str
    text: str
    url: str
    entities: List[Dict] = Field(default_factory=list)
    retweet_count: int = 0
    favorite_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    source: str = "Unknown"

class DailyTweets(BaseModel):
    """Collection of tweets for a single day"""
    date: str
    tweets: List[Tweet]

class WeeklyTweets(BaseModel):
    """Weekly collection of tweets"""
    week: str
    author: str
    tweets: List[DailyTweets]

class BlogPost(BaseModel):
    """Blog post structure"""
    title: str = Field(description="The title of the blog post")
    content: str = Field(description="The main content of the blog post")
    key_themes: List[str] = Field(description="List of key themes identified in the tweets")
    summary: str = Field(description="A brief summary of the blog post")
    tweet_count: int = Field(description="Total number of tweets analyzed")
    date_range: str = Field(description="Date range of the tweets analyzed")
    author: str = Field(description="Twitter handle of the author")

    def to_markdown(self) -> str:
        """Convert blog post to markdown format"""
        themes_md = "\n".join([f"- {theme}" for theme in self.key_themes])
        return "\n\n".join([
            f"# {self.title}",
            f"**Author**: {self.author}",
            f"**Date Range**: {self.date_range}",
            f"**Tweets Analyzed**: {self.tweet_count}",
            "\n## Key Themes",
            themes_md,
            "\n## Content",
            self.content,
            "\n## Summary",
            self.summary
        ])

class BlogAgent:
    """Agent for analyzing tweets and generating blog posts"""
    def __init__(self):
        self.agent = Agent[str, str](
            model="openai:gpt-4o-mini",
            system_prompt="""You are an expert content analyst and writer. Your task is to analyze tweets and generate a well-structured blog post in markdown format that:
1. Identifies key themes and patterns in the tweets
2. Provides insightful analysis of the content
3. Creates a coherent narrative from the tweet collection
4. Highlights important discussions and trends
5. Maintains the author's voice and expertise

Your response must be in this markdown format:

# [Title of the Blog Post]

**Author**: [Twitter Handle]
**Date Range**: [Date Range Analyzed]
**Tweets Analyzed**: [Total Tweet Count]

## Key Themes
- Theme 1
- Theme 2
- etc.

## Content
[Main content of the blog post, analyzing the tweets and creating a coherent narrative]

## Summary
[Brief summary of the key points and insights]

Focus on creating a professional, engaging blog post that captures the essence of the tweet collection."""
        )

    def _format_input(self, tweets_data: WeeklyTweets) -> str:
        """Format tweet data for analysis"""
        tweet_texts = []
        total_tweets = 0
        for day in tweets_data.tweets:
            for tweet in day.tweets:
                tweet_texts.append(f"[{day.date} {tweet.time}] {tweet.text}")
                total_tweets += 1
        
        return "\n\n".join([
            f"Author: {tweets_data.author}",
            f"Date Range: {tweets_data.week}",
            f"Total Tweets: {total_tweets}",
            "Tweets:",
            "\n".join(tweet_texts)
        ])

    async def analyze_and_generate(self, tweets_data: WeeklyTweets) -> str:
        """Analyze tweets and generate a blog post"""
        formatted_input = self._format_input(tweets_data)
        result = await self.agent.run(formatted_input)
        return result.data

async def process_tweets(input_file: str) -> None:
    """Process tweets and generate blog post"""
    console = Console()
    console.print(Panel.fit("[bold green]Tweet Analyzer and Blog Generator[/bold green]", border_style="green"))
    
    try:
        # Initialize progress
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
            transient=False
        )
        
        with progress:
            # Load tweet data
            task_id = progress.add_task("[cyan]Loading tweet data...", total=None)
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tweets_data = WeeklyTweets(**data)
            
            # Create blog agent
            progress.update(task_id, description="[cyan]Analyzing tweets...")
            blog_agent = BlogAgent()
            
            # Generate blog post
            markdown_content = await blog_agent.analyze_and_generate(tweets_data)
            
            # Print results
            progress.stop()
            console.print("\n[bold green]✨ Blog Post Generated Successfully! ✨[/bold green]")
            
            # Parse markdown sections for display
            sections = markdown_content.split('\n\n')
            title = sections[0].replace('# ', '').strip()
            
            with Status("[bold blue]Formatting output...", console=console):
                console.print("\n[bold blue]Title:[/bold blue]")
                console.print(Panel.fit(title, border_style="blue"))
                
                console.print("\n[bold green]Content Preview:[/bold green]")
                console.print(markdown_content)
            
            # Save the blog post
            with Status("[bold yellow]Saving blog post...", console=console):
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                
                # Create filename from date
                filename = f"blog_{datetime.now().strftime('%Y-%m-%d')}"
                output_path = output_dir / f"{filename}.md"
                
                # Save markdown output
                output_path.write_text(markdown_content)
                console.print(f"\n[bold green]✅ Blog post saved to: {output_path}[/bold green]")
    
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        import traceback
        traceback.print_exc()

async def main():
    await process_tweets("output/12-13-24-madad.json")

if __name__ == "__main__":
    asyncio.run(main())