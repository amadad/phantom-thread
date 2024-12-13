# Phantom Thread

A suite of tools to convert various content into well-structured markdown posts.

## Scripts

### 1. tweet.py
Twitter archiver - downloads tweets from a user's timeline and saves them as JSON.

### 2. 02-tweet2post.py
Converts JSON tweet archives into blog posts:
- Takes tweet JSON from /output
- Groups by day/week
- Generates structured blog post via GPT-4
- Saves as markdown to /output/{date}.md

### 3. 03-url2post.py
Converts web articles into essays:
- Takes a URL input
- Scrapes content (Spider API or BeautifulSoup)
- Generates structured essay via GPT-4
- Saves as markdown to /output/{date}_{domain}.md

## Setup

1. Environment variables needed:
```bash
OPENAI_API_KEY=your_key_here
SPIDER_API_KEY=your_key_here  # Optional, for better web scraping
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
# Archive tweets
python tweet.py

# Convert tweets to blog post
python 02-tweet2post.py

# Convert URL to essay
python 03-url2post.py
```

Output files are saved to /output directory in markdown format.
