import json
import numpy as np
import redis
import time
import argparse
import os

from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition

from redis_module import redis_aux

def index_documents(r, doc_prefix, documents):
    for i, doc in enumerate(documents):
        if 'title' in doc and 'text' in doc:  # Ensure both 'title' and 'text' are present
            key = f"{doc_prefix}:{doc['nid']}"
            r.hset(key, mapping=doc)
        else:
            print(f"Document with nid {doc['nid']} skipped (missing 'title' or 'text')")

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

def main(year, file, host="localhost", port=6379):
    if year is not None:
        r = redis_aux.connect_redis(host=host, port=port)
        index_name = 'idx:news_articles_RL'
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
                       TextField(name="ner_date"),]

    
        redis_aux.create_index(r, index_name, "news_articles:RL:", fields_news) 
        
        doc_prefix = f'news_articles:RL:{year}'  
        with open(file, "r", encoding="utf8") as readfile:
            key_moments = json.load(readfile)

        key_moments = convert_lists_to_strings(key_moments) # redis does not accepts lists !!
        index_documents(r, doc_prefix, key_moments) 

    
# def parse_arguments():
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         '-y', '--year', help='Year', required=True, type=int)
#     args = parser.parse_args()

#     return args

# if __name__ == '__main__':
    
#     arguments = parse_arguments()
#     main(arguments.year)
