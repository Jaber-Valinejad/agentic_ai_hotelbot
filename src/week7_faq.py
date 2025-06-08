import os
from dotenv import load_dotenv
load_dotenv()
your_openai_api_key= os.getenv("OPENAI_API_KEY")
import getpass
import time
import os
#openai_api_key=your_openai_api_key
#from openai import OpenAI
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

'''
Initialize Redis for vector storage and LlamaIndex for semantic search
'''
import pandas as pd
from sentence_transformers import SentenceTransformer
import redis
import numpy as np

# Load documents (assuming text files in a folder)
#documents = SimpleDirectoryReader("data").load_data()

# Build the index
#index = VectorStoreIndex.from_documents(documents)

# Initialize Redis (if needed)




#redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# in docker
###redis_client = redis.Redis(host="redis", port=6379)
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

# SentenceTransformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

'''
Step 3: Prepare Data for Vectorization
'''


# Load CSVs
services_df = pd.read_csv("datasets/services.csv")
promotions_df = pd.read_csv("datasets/promotions.csv")
amenities_df = pd.read_csv("datasets/amenities.csv")


def df_to_strings(df, text_col):
    return [str(row[text_col]) for _, row in df.iterrows() if pd.notna(row[text_col])]

# Extract relevant text fields
service_texts = df_to_strings(services_df, "description")
promotion_texts = df_to_strings(promotions_df, "description")
amenity_texts = df_to_strings(amenities_df, "description")

# Combine all into a single list of strings
nodes = service_texts + promotion_texts + amenity_texts


# Sample hotel service data
hotel_services = nodes 
'''
[
    "Free Wi-Fi available in all areas",
    "24-hour room service",
    "Spa and wellness center",
    "Swimming pool and fitness center",
    "Check-in starts at 3 PM"
]
'''
if __name__ == "__main__":
  # Convert services to vectors using the sentence transformer model
  vectors = [model.encode(service) for service in hotel_services]
  # Store vectors in Redis
  #for idx, vector in enumerate(vectors):
  #    redis_client.set(f"service_{idx}", vector.astype(np.float32).tobytes())
  for idx, (vector, text) in enumerate(zip(vectors, hotel_services)):
    key = f"service_vector_{idx}"
    if not redis_client.exists(key): 
      redis_client.set(key, vector.astype(np.float32).tobytes())
      redis_client.set(key, text)

  redis_client.set(f"dim_service_{idx}", vector.shape[0])
  print("Hotel services vectorized and stored in Redis.")


'''
Step 4: Implement the Search Functionality
'''
def search_service(query, top_k=3):
    query_vector = model.encode(query).astype(np.float32)
    keys = redis_client.keys("service_*")
    results = []

    for key in keys:
        raw = redis_client.get(key)
        if raw is None:
            continue
        try:
            vector = np.frombuffer(raw, dtype=np.float32)
            score = np.dot(query_vector, vector)
            results.append((key.decode(), score))
        except ValueError:
            print(f"⚠️ Could not decode vector for key: {key}")
            continue

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]
    return [k for k, _ in sorted_results]
###############
def search_service1(query, top_k=3):
    query_vector = model.encode(query).astype(np.float32)
    keys = redis_client.keys("service_vector_*")
    results = []

    for key in keys:
        raw = redis_client.get(key)
        if raw is None:
            continue
        try:
            vector = np.frombuffer(raw, dtype=np.float32)
            score = np.dot(query_vector, vector)
            results.append((key.decode(), score))
        except ValueError:
            print(f"⚠️ Could not decode vector for key: {key}")
            continue

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)[:top_k]

    # Retrieve matching service descriptions
    service_descriptions = []
    for key, score in sorted_results:
        idx = key.replace("service_vector_", "")
        desc = redis_client.get(f"service_text_{idx}")
        service_descriptions.append(desc.decode())


    # Prompt to LLM
    system_prompt = (
        "You are a helpful assistant at a hotel. Use the provided service descriptions to answer user questions clearly and informatively."
    )
    full_prompt = f"{system_prompt}\n\nContext:\n{service_descriptions}\n\nUser Question: {query}\n\nAnswer:"

    try:
        #client = OpenAI(api_key=openai_api_key)
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ LLM error: {str(e)}"

    #return service_descriptions

# Test search functionality
#query = "Do you have a pool?"
#response = search_service1(query)
#print("Top matching hotel services:", response)


