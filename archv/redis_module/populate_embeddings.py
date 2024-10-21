import json
import redis
import argparse
import numpy as np

from redis.commands.search.field import TextField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition

from . import redis_aux

def index_documents(r, doc_prefix, documents, *vector_field):
    for i, doc in enumerate(documents):
        key = f"{doc_prefix}:{doc['nid']}"
        for field in vector_field:
            if field in doc and doc[field] is not None:
                text_embedding = np.array(doc[field], dtype=np.float32).tobytes()
                doc[field] = text_embedding
            else:
                print(f"Field '{field}' missing or None in document {i}")
        print(f"Indexing document {i}: {doc['nid']}")
        r.hset(key, mapping=doc)
    
    print("Documents indexed")

def main(year, file, host="localhost", port=6379):
    if year is not None:
        r = redis_aux.connect_redis(host=host, port=port)
        with open(file, "r", encoding="utf8") as readfile:
            key_moments = json.load(readfile)

        index_name = 'idx:news_articles'
        vector_field = 'embeddings'

        VECTOR_DIM = len(key_moments[0][vector_field]) 
        VECTOR_NUMBER = len(key_moments)                

        DISTANCE_METRIC = "COSINE"                      

        embeddings = VectorField(vector_field,
            "HNSW", {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIM,
                "DISTANCE_METRIC": DISTANCE_METRIC,
                "INITIAL_CAP": VECTOR_NUMBER,
            }
        )

        fields_news = [
            TextField(name="nid"),   
            embeddings              
        ]

        # drop_index(r, index_name)
        # drop_data(r, index_name)
        doc_prefix = f'news_articles:{year}' 
        redis_aux.create_index(r, index_name, doc_prefix, fields_news)
        index_documents(r, doc_prefix, key_moments, vector_field)

    
# def parse_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '-y', '--year', help='Year', required=True, type=int)
#     args = parser.parse_args()

#     return args

# if __name__ == '__main__':
#     arguments = parse_arguments()
#     main(arguments.year)