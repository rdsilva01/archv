import json
import numpy as np
import redis
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition

def connect_redis(host, port):    
    r = redis.Redis( host=host, port=port, decode_responses=True )
    return r

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

def search_redis_all(return_fields):
    r = connect_redis()
       
    query = Query("*").return_fields(*return_fields).paging(0,10)
    results = r.ft("idx:news_articles").search(query)
    
    return results.docs