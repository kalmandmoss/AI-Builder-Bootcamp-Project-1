# Simple Reddit scraper using direct JSON API
import requests
import pandas as pd
import time
from datetime import datetime

# --- User Settings ---
SUBREDDIT = "golf"        # e.g. 'LocalLLaMA', 'technology', 'Python'
TIME_FILTER = "day"       # 'hour', 'day', 'week', 'month', 'year', 'all'
LIMIT = 50                # Number of posts (max 100 for non-API)
OUTPUT_CSV = f"reddit_{SUBREDDIT}_trends.csv"

# --- Step 1: Build the endpoint URL ---
url = f"https://www.reddit.com/r/{SUBREDDIT}/top/.json?t={TIME_FILTER}&limit={LIMIT}"
print(f"Fetching data from: {url}")

# --- Step 2: Send GET request ---
headers = {'User-agent': 'Mozilla/5.0'}
print(f"Using headers: {headers}")

# Add a small delay to be respectful of rate limits
time.sleep(2)

response = requests.get(url, headers=headers)
print(f"Response status code: {response.status_code}")
print(f"Response headers: {dict(response.headers)}")

if response.status_code != 200:
    print(f"Response content: {response.text[:500]}")  # Print first 500 chars of error response
    raise Exception(f"Failed to fetch data: {response.status_code}")

# --- Step 3: Extract post data ---
data = response.json()
posts = data["data"]["children"]
print(f"Successfully fetched {len(posts)} posts")

# Get current timestamp
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# --- Step 4: Parse fields ---
records = []
for post in posts:
    post_data = post["data"]
    records.append({
        "title": post_data["title"],
        "upvotes": post_data["ups"],
        "comments": post_data["num_comments"],
        "author": post_data["author"],
        "permalink": f"https://www.reddit.com{post_data['permalink']}",
        "created_utc": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(post_data["created_utc"])),
        "scraped_at": current_time
    })

# --- Step 5: Store in pandas DataFrame ---
df = pd.DataFrame(records)
print(df.head())

# --- Step 6: Append to CSV ---
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