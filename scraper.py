import asyncio
from twscrape import API, gather
from twscrape.logger import set_log_level
from datetime import datetime, timezone, timedelta
import requests
import re
import geonamescache
import pandas as pd

def load_city_data(csv_file):
    df = pd.read_csv(csv_file)
    # Ensure the necessary columns exist
    required_columns = ['city', 'state_id', 'state_name', 'county_name']
    if all(col in df.columns for col in required_columns):
        return df
    else:
        raise ValueError(f"CSV must contain the following columns: {required_columns}")

csv_file = "uscities.csv"  # Replace with your actual CSV path
city_data = load_city_data(csv_file)
gc = geonamescache.GeonamesCache()
us_states = gc.get_us_states()

# List of common prepositions or words related to locations
location_prepositions = {'in', 'at', 'near', 'around', 'by', 'on', 'within'}
# List of common place keywords
place_keywords = {
    'markets': ['market', 'mall', 'supermarket', 'grocery store', 'bazaar', 'shopping center', 'retail store'],
    'hospitals': ['hospital', 'clinic', 'medical center', 'healthcare center', 'emergency room', 'urgent care'],
    'parks': ['park', 'garden', 'playground', 'nature reserve', 'wildlife preserve', 'forest park', 'recreation area'],
    'landmarks': ['stadium', 'monument', 'museum', 'theater', 'tower', 'bridge', 'temple', 'palace', 'cathedral', 'church', 'clock tower', 'fountain', 'fort', 'arch', 'obelisk'],
    'restaurants': ['restaurant', 'diner', 'cafe', 'bistro', 'eatery', 'brasserie', 'food court', 'steakhouse', 'sushi bar', 'coffee shop'],
    'hotels': ['hotel', 'motel', 'inn', 'guesthouse', 'resort', 'bed and breakfast', 'hostel', 'lodge', 'penthouse', 'suite'],
    'universities': ['university', 'college', 'academy', 'institute', 'school of', 'campus'],
    'schools': ['school', 'high school', 'middle school', 'elementary school', 'primary school', 'secondary school'],
    'amusement parks': ['amusement park', 'theme park', 'water park', 'funfair', 'carnival', 'roller coaster park'],
    'beaches': ['beach', 'shore', 'coast', 'seaside', 'boardwalk', 'bay', 'cove', 'pier'],
    'mountains': ['mountain', 'hill', 'peak', 'ridge', 'summit', 'cliff', 'rocky mountain'],
    'beacons': ['lighthouse', 'beacon'],
    'airport': ['airport', 'airfield', 'terminal', 'runway'],
    'stations': ['station', 'train station', 'bus station', 'metro station', 'subway station'],
    'malls': ['mall', 'shopping mall', 'shopping center', 'outlet mall', 'strip mall'],
    'stadiums': ['stadium', 'arena', 'sports complex', 'ballpark', 'field', 'court'],
    'casinos': ['casino', 'gaming hall', 'gambling hall', 'slot hall'],
    'theaters': ['theater', 'cinema', 'movie theater', 'playhouse', 'opera house'],
    'nightclubs': ['nightclub', 'disco', 'dance hall', 'club', 'bar'],
    'gyms': ['gym', 'fitness center', 'health club', 'exercise center', 'yoga studio'],
    'stores': ['store', 'shop', 'boutique', 'outlet', 'department store', 'convenience store'],
    'libraries': ['library', 'reading room', 'bookstore'],
    'churches': ['church', 'cathedral', 'chapel', 'temple', 'synagogue', 'mosque', 'shrine'],
    'pools': ['pool', 'swimming pool', 'spa', 'hot spring'],
    'gardens': ['botanical garden', 'flower garden', 'rose garden', 'greenhouse'],
    'zoos': ['zoo', 'animal park', 'wildlife park'],
    'aquariums': ['aquarium', 'marine park'],
    'factories': ['factory', 'plant', 'manufacturing plant'],
    'construction sites': ['construction site', 'building site', 'development area'],
    'cemeteries': ['cemetery', 'graveyard', 'burial ground', 'memorial park'],
    'courthouses': ['courthouse', 'court building', 'justice building'],
    'jails': ['jail', 'prison', 'detention center', 'correctional facility'],
    'police stations': ['police station', 'police precinct', 'law enforcement center'],
    'fire stations': ['fire station', 'firehouse'],
    'embassies': ['embassy', 'consulate'],
    'post offices': ['post office', 'mailing center'],
    'government buildings': ['government building', 'town hall', 'city hall', 'state house'],
    'military bases': ['military base', 'army base', 'naval base', 'air force base'],
    'fairs': ['fair', 'county fair', 'state fair', 'exposition'],
    'theme parks': ['theme park', 'water park', 'amusement park'],
}

API_KEY = "TBA"

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

class Sighting:
    def __init__(
        self,
        tweet_id: str,
        poster: str,
        address: str,
        latitude: float,
        longitude: float,
        timestamp: datetime
    ):
        self.id = tweet_id
        self.poster = poster
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp

    def __repr__(self):
        return f"TweetLocation(id={self.id}, poster='{self.poster}', address='{self.address}', latitude={self.latitude}, longitude={self.longitude}, timestamp={self.timestamp})"

# Build the query by excluding each keyword and including 'ice' or 'DHS'
def build_query() -> str:
    q = "ice OR DHS OR Migra OR CPB sighting since:2025-01-20 until:2025-02-08 filter:media"
    for KEYWORD in EXCLUDE_KEYWORDS:
        q += f" -{KEYWORD}" # Exclude keyword by adding `-`
    return q

def is_bot(user) -> bool:
    one_month_ago = datetime.now(timezone.utc) - timedelta(days=30)

    return (
        user.followersCount < 10 or user.friendsCount > 5000 or  # Suspicious follower ratio
        user.created >= one_month_ago or  # New account
        not user.profileImageUrl or user.username.isdigit()  # Default profile or numeric username
    )

def format_location_for_google_maps(text) -> str:
    city_and_state_result = extract_city_state_from_csv(text, city_data)
    if city_and_state_result:
        city, state, modified_text = city_and_state_result[0], city_and_state_result[1], city_and_state_result[2]
        found_entities = extract_named_entities(modified_text)
        if found_entities:
            return found_entities[0] + ", " + city + ", " + state
        return modified_text + ", " + city + ", " + state
    return text

def extract_and_validate_location(text) -> str | None:
    query = format_location_for_google_maps(text)
    
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={
            "query": query,
            "key": API_KEY
        }
    )
    
    data = response.json()
    if data.get("results"):
        place = data["results"][0]
        return {
            "address": place["formatted_address"],
            "latitude": place["geometry"]["location"]["lat"],
            "longitude": place["geometry"]["location"]["lng"]
        }

    return None  # No valid location found

def extract_valid_ice_sighting(tweet) -> Sighting | None:
    # make sure tweet has media (filter:media already in search query)
    # make sure account is not a bot
    if not tweet.user or is_bot(tweet.user):
        print("Tweet has no user or seems like bot")
        return None
    # make sure tweet has location in text
    location = extract_and_validate_location(tweet.rawContent)
    if not location:
        print("Tweet has no valid location")
        return None
    return Sighting(
        tweet_id=tweet.id,
        poster=tweet.user.username,
        address=location["address"],
        latitude=location["latitude"],
        longitude=location["longitude"],
        timestamp=datetime.fromisoformat(str(tweet.date))
    )
    
def format_tweet(tweet): # TODO: remove this
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

# Function to parse text and find city-state pairs, also remove the city and state tokens
def extract_city_state_from_csv(text, city_data):
    # Tokenize the text and convert to lowercase
    tokens = re.findall(r'\b\w+\b', text.lower())

    # Create sets for state abbreviations and names
    state_abbr_set = {abbr.lower() for abbr in us_states.keys()}
    state_name_set = {state_data["name"].lower() for state_data in us_states.values()}

    # Process the tokens and look for state mentions
    for i, token in enumerate(tokens):
        if token in state_abbr_set or token in state_name_set:
            # Find the state
            state_token = token
            state_name = next(
                (state["name"] for state_code, state in us_states.items() if state_code.lower() == state_token), 
                token.title()
            )

            # Look for city or county preceding the state token (within 2 tokens before)
            for j in range(max(0, i - 2), i):
                city_candidate = " ".join(tokens[j:i]).title()
                
                # Check if city or county is in the CSV for the identified state
                matching_city_or_county = city_data[
                    (city_data['state_name'].str.lower() == state_name.lower()) & 
                    ((city_data['city'].str.lower() == city_candidate.lower()) | 
                     (city_data['county_name'].str.lower() == city_candidate.lower()))
                ]
                
                if not matching_city_or_county.empty:
                    # City-state pair found, now remove city and state from the original text
                    city_state_str = f"{city_candidate} {state_name}".lower()
                    city_token = city_candidate.lower()

                    # Remove both the city and state tokens from the original text
                    tokens_to_remove = {city_token, state_token}
                    
                    # Remove location prepositions if they precede both city and state
                    if j > 0 and tokens[j - 1] in location_prepositions:
                        tokens_to_remove.add(tokens[j - 1].lower())
                    
                    # Remove both the city and state tokens (and preposition if applicable)
                    modified_text = ' '.join([
                        word for word in text.split() 
                        if word.lower() not in tokens_to_remove
                    ])

                    return (city_candidate, state_name, modified_text)
    
    # Return None if no match is found
    return None

# Function to extract places as a list of full place names
def extract_named_entities(text):
    # Convert the text to lowercase to make the search case-insensitive
    text = text.lower()

    # Initialize an empty list to hold the matched places
    found_places = []

    # Check for each category of places
    for category, keywords in place_keywords.items():
        for keyword in keywords:
            # Match keywords and allow for multi-word place names by finding sequences of words before and including the keyword
            # Adjust regex to match up to 3 words before the keyword and the keyword itself
            pattern = r'(\b(?:\w+\s+){0,3}' + re.escape(keyword) + r'\b)'  # Match up to 3 words before the keyword and the keyword itself
            matches = re.findall(pattern, text)
            if matches:
                # Add the matches to the result list, avoiding duplicates
                for match in matches:
                    # Clean up and strip extra spaces, ensuring full names are returned
                    full_name = match.strip()
                    if full_name not in found_places:
                        found_places.append(full_name)

    # Return a list of found places (without duplicates)
    return found_places

async def main():
    api = API()

    q = build_query() # Generate query with exclusions
    async for tweet in api.search(q, limit=200):
        # print("got tweet")
        tweet_info = format_tweet(tweet) # Format tweet to include only the needed information
        # print(f"Tweet ID: {tweet_info['id']}")
        # print(f"Username: {tweet_info['username']}")
        # print(f"Content: {tweet_info['raw_content']}")
        # print(f"Location: {tweet_info['location']}")
        sighting = extract_valid_ice_sighting(tweet)
        if sighting:
            print("VALID TWEET:")
            print(f"Tweet ID: {tweet_info['id']}")
            print(f"Username: {tweet_info['username']}")
            print(f"Content: {tweet_info['raw_content']}")
            print(f"Location: {tweet_info['location']}")
            print(sighting)
        else:
            print("INVALID TWEET:")
        print("\n") # Add a blank line between posts

if __name__ == "__main__":
    asyncio.run(main())