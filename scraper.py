import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
from datetime import datetime, timezone, timedelta

# List of keywords to exclude, TODO: make this a substring search instead of token
EXCLUDE_KEYWORDS = [
    "flood",
    "snow",
    "cold",
    "freezing",
    "flooded",
    "illegal",
    "false",
    "@realDonaldTrump",
    "@DonaldJTrumpJr",
    "@elonmusk",
    "illegals"
] 

# Build the query by excluding each keyword and including 'ice' or 'DHS'
def build_query():
    q = "ice OR DHS OR Migra OR CPB sighting since:2025-01-20 until:2025-01-21 filter:media"
    for KEYWORD in EXCLUDE_KEYWORDS:
        q += f" -{KEYWORD}" # Exclude keyword by adding `-`
    return q

def is_bot(user):
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)

    return (
        user.followers_count < 10 or user.following_count > 1000 or  # Suspicious follower ratio
        user.created_at >= one_month_ago or  # New account
        not user.profile_image_url or user.username.isdigit()  # Default profile or numeric username
    )

def is_valid_ice_sighting(tweet):
    # make sure tweet has media (filter:media already in search query)
    # make sure account is not a bot
    if not tweet.user or is_bot(tweet.user):
        return False
    # make sure tweet has location in text
    # TODO: this

def format_tweet(tweet):
    # Check if tweet has media and contains photos
    # if tweet.media is None or not tweet.media.photos:
    #     return None # Skip tweets that do not contain a photo
    
    # TODO: clarify that this is only for debugging and improving the filtering

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