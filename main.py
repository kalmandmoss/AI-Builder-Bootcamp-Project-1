import requests
import pandas as pd
import time

# --- User Settings ---
SUBREDDIT = "golf"        # e.g. 'LocalLLaMA', 'technology', 'Python'
TIME_FILTER = "day"             # 'hour', 'day', 'week', 'month', 'year', 'all'
LIMIT = 50                      # Number of posts (max 100 for non-API)
OUTPUT_CSV = f"reddit_{SUBREDDIT}_trends.csv"

# --- Step 1: Build the endpoint URL ---
url = f"https://www.reddit.com/r/{SUBREDDIT}/top/.json?t={TIME_FILTER}&limit={LIMIT}"

# --- Step 2: Send GET request ---
headers = {'User-agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Failed to fetch data: {response.status_code}")

# --- Step 3: Extract post data ---
data = response.json()
posts = data["data"]["children"]

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
        "created_utc": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(post_data["created_utc"]))
    })

# --- Step 5: Store in pandas DataFrame ---
df = pd.DataFrame(records)
print(df.head())

# --- Step 6: Save to CSV ---
df.to_csv(OUTPUT_CSV, index=False)
print(f"Saved {len(df)} posts to {OUTPUT_CSV}") 