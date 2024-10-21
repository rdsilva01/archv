# archv

archv is a Python package created to retrieve, process, and perform Natural Language Processing (NLP) on news articles. This package includes modules for extracting news information, embedding generation, and the implementation of a recommendation system of news articles by implementing a Redis VSS backend.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
- [Demo](#demo)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rdsilva01/?
   cd news-recommendation-system
   ```
2.  (OPTIONAL) Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows use `venv\Scripts\activate`
    ````
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ````
4. Set up Docker for Redis and the web demo:
    ```bash
    docker-compose up --build
    ````

## Configuration
Make sure to update the configuration in the following files:
- docker-composer.yml (paths for Redis and the web demo)

## Usage

1. Fetch and Process News Articles
    One can fetch and process news articles with the news_retrieval module:
    ```bash
    python news_recommendation/news_retrieval/fetch_news_articles.py
    ```
2. Populate the Redis Database with News Articles and respective embeddings
    ```bash
    python news_recommendation/redis_module/populate_db.py
    python news_recommendation/redis_module/populate_embeddings.py
    ```
3. Run the Recommendation System
    You can use the recommendation system via the recommend.py module:
    ```bash
    python news_recommendation/recommendation_system/recommend.py
    ```
4. Access the Web Demo
    After running Docker, access the demo web interface in your browser:
    ```bash
    http://localhost:90/demo/index
    ```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes. Make sure to write tests and update documentation where applicable.

## License  
This project is licenced under the ??? License. See LICENSE file for more details.
