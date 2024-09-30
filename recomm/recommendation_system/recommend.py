import json
import os
import yake
import spacy
import torch
import numpy as np
import redis

from transformers import AutoTokenizer, AutoModel
from chunkipy import TextChunker, TokenEstimator
from math import sqrt 
from redis.commands.search.query import Query


def square_rooted(x):
    return round(sqrt(sum([a*a for a in x])),3)

def Cosine(x,y):
    numerator = sum([a*b for a,b in zip(x,y)])
    denominator = square_rooted(x)*square_rooted(y)
    return round(numerator/float(denominator),3)


def get_news_articles_similarity(r, type: str, k: int, nid: str, index_name: str, doc_prefix: str, vector_field: str, debug: bool):
    query = (
        Query(f"*=>[KNN {k+1} @embeddings $vec as score]")  # KNN search
        .sort_by("score")                                 # sorting by the score
        .return_fields("nid", "id", "score")               # return 'id' and 'score' fields
        .paging(1, k+1)                                     # get k results
        .dialect(2)                                       # dialect 2 means KNN
    )

    first_doc_embedding = r.hget(f"{doc_prefix}:{nid}", vector_field)
    first_doc_embedding_np = np.frombuffer(first_doc_embedding, dtype=np.float32)

    query_params = {
        "vec": first_doc_embedding_np.tobytes()
    }

    result = r.ft(index_name).search(query, query_params)

    if debug:
        for doc in result.docs:
            print(f"ID: {doc.id}, Score: {doc.score}")

    return result.docs
