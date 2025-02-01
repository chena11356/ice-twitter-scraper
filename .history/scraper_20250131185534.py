import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level

async def main():
    api = API()
    
    q = "ice sighting since:2025-01-20 until:2025-01-31"
    async for tweet in api.search(q, limit=50):
        print(tweet.id, tweet.user.username, tweet.rawContent)


if __name__ == "__main__":
    asyncio.run(main())