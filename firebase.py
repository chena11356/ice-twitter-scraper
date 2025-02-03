import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK with your service account key
cred = credentials.Certificate('serviceAccountKey.json') # Correct path to your JSON file
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
        'title': 'Sample Post', # Example field
            'content': 'This is a sample post content.', # Example field
            'author': 'Lauren', # Example field
            'timestamp': firestore.SERVER_TIMESTAMP # Automatically sets the timestamp on the server
        }

        # Add a new document with automatic ID
        posts_ref.add(data)
        print("Post added successfully.")

    except Exception as e:
        print(f'Error posting data: {e}') # Handle errors

# Call the post_data function to run
post_data()