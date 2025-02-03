import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK with service account key
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# Function to post data to the 'posts' collection
def post_data():
    try:
        # Reference to the 'posts' collection
        posts_ref = db.collection('posts')

        # Data to be posted
        data = {
            'latitude': 37.620274,
            'longitude': -77.526858,
            'poster': 'Alex2', # Example field
            'timestamp': firestore.SERVER_TIMESTAMP # Automatically sets the timestamp on the server
        }

        posts_ref.document("1884413606927753471").set(data)

        print("Post added successfully.")

    except Exception as e:
        print(f'Error posting data: {e}') # Handle errors

# Call the post_data function to run
post_data()