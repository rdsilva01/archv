import json
import redis
import torch
import numpy as np

from transformers import AutoTokenizer, AutoModel
from redis.commands.search.query import Query

from news_retrieval import process_news_articles, fetch_news_articles
from recommendation_system import recommend
from redis_module import populate_db
from aux import verify

# Constants
MONTHS = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"
]

# Redis configuration
HOST = "localhost"
PORT = 6379

def connect_redis(host, port):
    """Establish a connection to Redis."""
    r = redis.Redis(host, port)
    return r

def search_redis_all(r, paging, return_fields):
    """Search all documents in Redis."""
    query = Query("*").return_fields(*return_fields).paging(0, paging)
    results = r.ft("idx:news_articles").search(query)
    return results.docs

def search_redis_per_id(r, paging, nid, return_fields):
    """Search for a specific document by ID in Redis."""
    query = Query(f"@nid:{nid}").return_fields(*return_fields).paging(0, paging)
    results = r.ft("idx:news_articles").search(query)
    return results.docs

def main():
    # Use case for the NC website
    year = 2015
    startMonth = "01"
    endMonth = "12"

    menu = f"\nMENU - {year}\n" + \
           "1- FETCH NEWS ARTICLES (PASTURLS + URLS)\n" + \
           "2- EXTRACT DATA FROM URLS\n" + \
           "3- KEYWORDS AND NER\n" + \
           "4- EMBEDDINGS CREATION\n" + \
           "5- POPULATING REDIS\n" + \
           "6- SIMILARITY\n" + \
           "0- (exit)\n"
    
    opt = -1
    while opt != 0:
        opt = int(input(menu))
        
        if opt == 1:
            urls_dict = fetch_news_articles.get_past_urls(
                url="https://noticiasdacovilha.pt/", year=year, 
                startMonth=startMonth, endMonth=endMonth, 
                filename=f"past_urls_NC_{year}"
            )
            fetch_news_articles.get_news_articles_urls(
                pastURLs=urls_dict[year],
                news_articles_htmlTag='', news_articles_htmlClass='',
                link_htmlTag='a', link_htmlClass='georgia t25 underhover',
                filename=f'urls_NC_{year}.json', 
                year=year,
                debug=True
            )

        elif opt == 2:
            urls_file = f"./data/{year}/urls_NC_{year}.json"
            with open(urls_file, 'r') as f:
                urls_data = json.load(f)

            news_article_dict = fetch_news_articles.get_news_articles_data(
                urls=urls_data,
                year=year,
                filename=f"news_articles_NC_{year}.json",
                debug=True,
                articleHtml_tag="div", articleHtml_id="tbl_print",
                titleHtml_tag="h1", titleHtml_class="georgia",
                dateHtml_tag="span", dateHtml_class="t10",
                imageHtml_tag="img",
                textHtml_tag="span", textHtml_id="mtexto",
                authorHtml_tag="span", authorHtml_class="t11",
            )

        elif opt == 3:
            news_articles_file = f"./data/{year}/news_articles_NC_{year}.json"
            with open(news_articles_file, 'r') as f:
                news_articles = json.load(f)

            # Process keywords and named entities
            process_news_articles.extract_keywords_news_articles(
                news_articles=news_articles,
                year=year,
                filename=f"news_articles_NC_{year}.json"
            )
            process_news_articles.extract_named_entities_news_articles(
                news_articles=news_articles,
                year=year,
                filename=f"news_articles_NC_{year}.json"
            )

        elif opt == 4:
            news_articles_file = f"./data/{year}/news_articles_NC_{year}.json"
            with open(news_articles_file, 'r') as f:
                news_articles = json.load(f)

            model_name = "PORTULAN/albertina-ptpt"  # Model to use
            model_name_tmp = model_name.split("/")[1]

            process_news_articles.get_news_articles_embeddings(
                news_articles=news_articles,
                year=year,
                filename=f"embeddings_NC_{year}_{model_name_tmp}.json",
                model_name=model_name,
                keys=["title", "text"]
            )

        elif opt == 5:
            news_articles_file = f"./data/{year}/news_articles_NC_{year}.json"
            news_articles_file_emb = f"./data/{year}/embeddings_NC_{year}_albertina-ptpt.json"

            populate_db.main(
                year=year, 
                file=news_articles_file, 
                emb_file=news_articles_file_emb, 
                host='localhost', 
                port=6379
            )

        elif opt == 6:
            r = connect_redis(host=HOST, port=PORT)
            docs = search_redis_all(r, 5000, ["nid", "title", "author", "text"])
            for doc in docs:
                doc_id = doc.id.split(":")[1]
                print(doc_id, " - ", doc.title, ", by ", doc.author)
            nid = input("Insert the ID to be compared: ")
            k = input("Insert the number of similar news articles to be found: ")
            snas = recommend.get_news_articles_similarity(
                r=r,
                type="", 
                k=int(k), 
                nid=nid, 
                index_name="idx:news_articles", 
                doc_prefix="news_articles", 
                vector_field="embeddings",
                debug=False
            )

            # Print reference article
            for doc in docs:
                if doc.id.split(":")[1] == nid:
                    print(f"REFERENCE - ID: {doc.id}\nTITLE: {doc.title}\nTEXT: {doc.text[:200]}...\n")

            # Print similar articles
            for i, sna in enumerate(snas):
                for doc in docs:
                    if sna.id.split(":")[1] == doc.id.split(":")[1]:
                        print(f"{i} - ID: {doc.id}\nTITLE: {doc.title}\nTEXT: {doc.text[:200]}...\n")

        elif opt == 7:
            news_articles_file = f"./data/{year}/news_articles_NC_{year}.json"
            news_articles_file_emb = f"./data/{year}/embeddings_NC_{year}_albertina-ptpt.json"

            with open(news_articles_file, "r", encoding="utf8") as f:
                documents = json.load(f)

            required_fields = ["nid", "og_url", "title", "date", "image", "text", "author", 
                    "kw", "ner_pers", "ner_org", "ner_loc", "ner_misc", "ner_date"]

            all_valid = verify.verify_documents(documents, required_fields)

            with open(news_articles_file_emb, "r", encoding="utf8") as f:
                documents = json.load(f)

            required_fields = ["nid", "embeddings"]
            all_valid = verify.verify_documents(documents, required_fields)

        elif opt == 0:
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()