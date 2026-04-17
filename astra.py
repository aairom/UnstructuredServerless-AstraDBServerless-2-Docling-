from astrapy import DataAPIClient

# Instantiate the client
client = DataAPIClient()

# Connect to a database
database = client.get_database(
    "API_ENDPOINT", token="APPLICATION_TOKEN"
)

# Get an existing collection
collection = database.get_collection("COLLECTION_NAME")

# Use vector search and filters to find a document
result = collection.find_one(
    {
        "$and": [
            {"is_checked_out": False},
            {"number_of_pages": {"$lt": 300}},
        ]
    },
    sort={"$vectorize": "A thrilling story set in a futuristic world"},
)

print(result)