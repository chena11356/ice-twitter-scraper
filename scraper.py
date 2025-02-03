import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level

# List of keywords to exclude, make this a substring search so include anything that is like this
exclude_keywords = ["flood", "snow", "cold", "freezing", "flooded", "illegal","false","@realDonaldTrump","@DonaldJTrumpJr","@elonmusk","illegals"] 

# Build the query by excluding each keyword and including 'ice' or 'DHS'
def build_query():
    q = "ice OR DHS OR Migra OR CPB sighting since:2025-01-20 until:2025-01-31"
    for keyword in exclude_keywords:
        q += f" -{keyword}" # Exclude keyword by adding `-`
    return q

def format_tweet(tweet):
    # Check if tweet has media and contains photos
    if tweet.media is None or not tweet.media.photos:
        return None # Skip tweets that do not contain a photo

    tweet_info = {
        'id': tweet.id,
        'username': tweet.user.username,
        'raw_content': tweet.rawContent,
        'location': tweet.place.name if tweet.place else "Unknown", # If location exists, otherwise "Unknown"
        'media': tweet.media.photos # Include photos in the tweet info
    }
    return tweet_info



async def main():
    api = API()

    q = build_query() # Generate query with exclusions
    async for tweet in api.search(q, limit=1):
        tweet_info = format_tweet(tweet) # Format tweet to include only the needed information
        print(f"Tweet ID: {tweet_info['id']}")
        print(f"Username: {tweet_info['username']}")
        print(f"Content: {tweet_info['raw_content']}")
        print(f"Location: {tweet_info['location']}")
        print("\n") # Add a blank line between posts

if __name__ == "__main__":
    asyncio.run(main())