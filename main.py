# Using PRAW (Python Reddit API Wrapper) for proper API access
import praw
import pandas as pd
import time
from datetime import datetime
import os

# --- User Settings ---
SUBREDDIT = "golf"        # e.g. 'LocalLLaMA', 'technology', 'Python'
TIME_FILTER = "day"       # 'hour', 'day', 'week', 'month', 'year', 'all'
LIMIT = 50                # Number of posts (max 100 for non-API)
OUTPUT_CSV = f"reddit_{SUBREDDIT}_trends.csv"

# --- Step 1: Initialize Reddit API client ---
# These values should be set as GitHub repository secrets
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent='python:reddit-data-collector:v1.0 (by /u/kalmandmoss)'
)

print(f"Fetching top posts from r/{SUBREDDIT}")

# --- Step 2: Fetch posts ---
try:
    subreddit = reddit.subreddit(SUBREDDIT)
    posts = list(subreddit.top(time_filter=TIME_FILTER, limit=LIMIT))
    print(f"Successfully fetched {len(posts)} posts")

    # Get current timestamp
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # --- Step 3: Parse fields ---
    records = []
    for post in posts:
        records.append({
            "title": post.title,
            "upvotes": post.score,
            "comments": post.num_comments,
            "author": str(post.author),
            "permalink": f"https://www.reddit.com{post.permalink}",
            "created_utc": datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "scraped_at": current_time
        })

    # --- Step 4: Store in pandas DataFrame ---
    df = pd.DataFrame(records)

    # --- Step 5: Append to CSV ---
    try:
        # Try to read existing CSV
        existing_df = pd.read_csv(OUTPUT_CSV)
        # Append new data
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        # Remove any duplicate posts (based on permalink) keeping the most recent scrape
        combined_df = combined_df.sort_values('scraped_at').drop_duplicates(subset=['permalink'], keep='last')
    except FileNotFoundError:
        # If file doesn't exist, use the new DataFrame
        combined_df = df

    # Save the combined data
    combined_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} new posts to {OUTPUT_CSV}")
    print(f"Total posts in dataset: {len(combined_df)}")

except Exception as e:
    print(f"Error occurred: {str(e)}")
    raise 