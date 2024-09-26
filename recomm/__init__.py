'''
recom is a package that provides functionalities for news article recommendation and similarity search.
'''

__version__ = '0.1.0'
__author__ = ''
__email__ = ''

# necessary imports
from .news_retrieval import fetch_news_articles, process_news_articles
from .recommendation_system import recommend, redis_service
from .aux import verify
from .redis_module import populate_db, populate_embeddings