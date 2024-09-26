import json
import numpy as np
import redis
import time
import argparse
import os

from redis.commands.search.field import TextField, NumericField, VectorField
from redis.commands.search.indexDefinition import IndexDefinition

from redis_module import redis_aux

# def index_documents(r, doc_prefix, documents):
#     for i, doc in enumerate(documents):
#         key = f"{doc_prefix}:{doc['nid']}"
#         r.hset(key, mapping=doc)
    
#     print("Documents indexed")

def index_documents(r, year, doc_prefix, documents, *vector_field):
    for i, doc in enumerate(documents):
        key = f"{doc_prefix}:{year}_{doc['nid']}"
        for field in vector_field:
            if field in doc and doc[field] is not None:
                text_embedding = np.array(doc[field], dtype=np.float32).tobytes()
                doc[field] = text_embedding
            else:
                print(f"Field '{field}' missing or None in document {i}")
        print(f"Indexing document {i}: {doc['nid']}")
        r.hset(key, mapping=doc)
    
    print("Documents indexed")

def convert_lists_to_strings(data):
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            if value is None:
                new_data[key] = ""  # Replace None with empty string
            elif isinstance(value, list):
                new_data[key] = " ; ".join(value) # split by a ;
            elif isinstance(value, dict):
                new_data[key] = convert_lists_to_strings(value)
            else:
                new_data[key] = value
        return new_data
    elif isinstance(data, list):
        new_list = []
        for item in data:
            new_list.append(convert_lists_to_strings(item))
        return new_list
    else:
        return data

def main(year, file, emb_file, host="localhost", port=6379):
    if year is not None:
        r = redis_aux.connect_redis(host=host, port=port)

        with open(emb_file, "r", encoding="utf8") as readfile:
            na_embeddings = json.load(readfile)

        index_name = 'idx:news_articles'
        vector_field = 'embeddings'

        VECTOR_DIM = len(na_embeddings[0][vector_field]) 
        VECTOR_NUMBER = len(na_embeddings)                

        DISTANCE_METRIC = "COSINE"                      

        embeddings = VectorField(vector_field,
            "HNSW", {
                "TYPE": "FLOAT32",
                "DIM": VECTOR_DIM,
                "DISTANCE_METRIC": DISTANCE_METRIC,
                "INITIAL_CAP": VECTOR_NUMBER,
            }
        )

        fields_news = [TextField(name="nid"),
                       TextField(name="og_url"),
                       TextField(name="title"),
                       TextField(name="date"),
                       TextField(name="image"),
                       TextField(name="text"),
                       TextField(name="author"),
                       TextField(name="kw"),
                       TextField(name="ner_person"),
                       TextField(name="ner_org"),
                       TextField(name="ner_loc"),
                       TextField(name="ner_misc"),
                       TextField(name="ner_date"),
                       embeddings]


        doc_prefix = f'news_articles' 
        redis_aux.create_index(r, index_name, doc_prefix, fields_news)
        
        with open(file, "r", encoding="utf8") as readfile:
            news_articles = json.load(readfile)

        news_articles = convert_lists_to_strings(news_articles) # redis does not accepts lists !!
        index_documents(r, year, doc_prefix, news_articles)
        index_documents(r, year, doc_prefix, na_embeddings, vector_field)

    
# def parse_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '-y', '--year', help='Year', required=True, type=int)
#     args = parser.parse_args()

#     return args

# if __name__ == '__main__':
    
#     arguments = parse_arguments()
#     main(arguments.year)
