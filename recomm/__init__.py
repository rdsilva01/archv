'''
recom is a package that provides functionalities for news article recommendation and similarity search.
'''

__version__ = '0.1.0'
__author__ = 'Your Name'
__email__ = 'your_email@example.com'

# Importing necessary modules and functionalities

# News retrieval functionalities
from .news_retrieval.fetch_news_articles import get_past_urls, get_news_articles_urls, get_news_articles_data
from .news_retrieval.process_news_articles import process_news

# Recommendation system functionalities
from .recommendation_system.recommend import generate_recommendations, calculate_similarity_score
from .recommendation_system.redis_service import connect_to_redis, get_redis_data

# Auxiliary functions
from .aux import verify
from .redis_module import populate_db, populate_embeddings

# Optional: Define what gets imported with 'from recom import *'
__all__ = [
    'get_past_urls', 'get_news_articles_urls', 'get_news_articles_data', 
    'process_news', 'generate_recommendations', 'calculate_similarity_score',
    'connect_to_redis', 'get_redis_data', 'verify', 'populate_db', 'populate_embeddings'
]