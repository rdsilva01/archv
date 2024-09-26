import redis
import numpy as np
import json
from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition

host = "localhost"
port = 6379

def connect_redis():    
    r = redis.Redis(
            host=host,
            port=port,

        )
    return r

def drop_index(r, index_name, delete_documents=True):
    try:
        r.ft(index_name).dropindex(delete_documents=delete_documents)
        print(f"Index '{index_name}' dropped")
    except Exception as e:
        print(f"Error: {e}")


def create_index(r, index_name, doc_prefix, fields):
    try:
        r.ft(index_name).info()
        print("Index already exists!")
    except:
        r.ft(index_name).create_index(fields=fields, definition=IndexDefinition(prefix=[doc_prefix]))
        print("Index created")

def drop_data(r, index_name, delete_documents=True):
    try:
        r.ft(index_name).dropindex(delete_documents=delete_documents)
        print('Index and data dropped')
    except:
        print('Index does not exist')

def index_documents(r, doc_prefix, documents, *vector_field):
    for i, doc in enumerate(documents):
        key = f"{doc_prefix}:{str(i)}"
        for field in vector_field:
            if field in doc and doc[field] is not None:
                text_embedding = np.array(doc[field], dtype=np.float32).tobytes()
                doc[field] = text_embedding
            else:
                print(f"Field '{field}' missing or None in document {i}")
        print(f"Indexing document {i}: {doc['id']}")
        r.hset(key, mapping=doc)
    
    print("Documents indexed")

def populate(r, year):
    with open(f"arquivonc/news_recommendation/data/NC_{year}_sm01_em12_embeddings.json", "r", encoding="utf8") as readfile:
        key_moments = json.load(readfile)

    index_name = 'idx:news_articles'
    vector_field = 'embeddings'

    VECTOR_DIM = len(key_moments[0][vector_field])  # Length of the vectors
    VECTOR_NUMBER = len(key_moments)                # Initial number of vectors

    DISTANCE_METRIC = "COSINE"                      # Distance metric for the vectors (COSINE, IP, L2)

    embeddings = VectorField(vector_field,
        "FLAT", {
            "TYPE": "FLOAT32",
            "DIM": VECTOR_DIM,
            "DISTANCE_METRIC": DISTANCE_METRIC,
            "INITIAL_CAP": VECTOR_NUMBER,  # Pre-allocated size of the index
        }
    )

    fields_news = [
        TextField(name="id"),   # You can add more fields here, e.g., title, text, author if needed
        embeddings              # The embeddings vector field
    ]

    drop_index(r, index_name)
    drop_data(r, index_name)

    doc_prefix = f'news_articles:{year}'  # Define document prefix (you can add year to avoid collisions)
    create_index(r, index_name, doc_prefix, fields_news)

    index_documents(r, doc_prefix, key_moments, vector_field)