'''
recom is a package that provides functionalities for news article recommendation and similarity search.
'''

__version__ = '0.1.0'
__author__ = 'Rodrigo Silva'
__email__ = 'rd.silva@ubi.pt'

# Importing necessary modules and functionalities

# News retrieval functionalities
from .news_retrieval.fetch_news_articles import get_past_urls, get_news_articles_urls, get_news_articles_data
from .news_retrieval.process_news_articles import extract_keywords, extract_keywords_news_articles, extract_named_entities, extract_named_entities_news_articles, get_embeddings_bert, get_news_articles_embeddings, get_text_to_speech,get_news_articles_tts

# Recommendation system functionalities
from .recommendation_system.recommend import get_news_articles_similarity
from .recommendation_system.redis_service import connect_redis, drop_data, drop_index, create_index, index_documents, populate

# Auxiliary functions
from .aux import verify
from .redis_module import populate_db, populate_embeddings

__all__ = [
    'get_past_urls', 'get_news_articles_urls', 'get_news_articles_data',
    'extract_keywords', 'extract_keywords_news_articles', 'extract_named_entities',
    'extract_named_entities_news_articles', 'get_embeddings_bert', 'get_news_articles_embeddings',
    'get_news_articles_similarity', 'connect_redis', 'drop_data', 'drop_index',
    'create_index', 'index_documents', 'populate', 'verify', 'populate_db', 'populate_embeddings', 
    'get_text_to_speech', 'get_news_articles_tts'
]