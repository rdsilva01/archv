import json
import re
import time
import requests
import os

from bs4 import BeautifulSoup
from publicnewsarchive import dataExtraction
from cleantext import clean

def _save_urls(data: dict, output_file: str, year: str):
        '''
        Auxiliar function to save the retrieved URLs to a JSON file.
        
        :param data: Dictionary containing URLs.
        :param year: Year ...
        '''
        try:
            f = f"./data/{year}/{output_file}.json"
            directory = os.path.dirname(f)

            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(f, "w") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)

            print(f"URLs successfully saved to {output_file}")
            
        except IOError as e:
            print(f"Error saving URLs to file: {e}")


def get_past_urls(url: str, year: int, startMonth: str, endMonth: str, filename: str):
        '''
        Get all the past URLs of the newspaper in the given year, provided by the Arquivo.pt API
        through the PublicNewsArchive package.
        
        :param url: The base URL of the newspaper.
        :param year: The year for which past URLs are retrieved.
        :param startMonth: The starting month.
        :param endMonth: The end month.
        :return: A dictionary with the year as the key and a list of URLs as the value.
        '''
        past_urls = dataExtraction.getPastURLs(
            year=year,
            newspaper_url=url,
            startMonth=startMonth,
            endMonth=endMonth
        )

        past_urls_dict = { year: past_urls }

        _save_urls(data=past_urls_dict, output_file=filename, year=year)
        
        return past_urls_dict

        
          
def get_news_articles_urls(pastURLs: dict[int, list], news_articles_htmlTag: str, news_articles_htmlClass: str, link_htmlTag: str, link_htmlClass: str, filename: str, year: str, debug=False):
        '''
        Get the URLs of the news articles from the past URLs.
        
        :param pastURLs: Dictionary containing the past URLs with the year as the key.
        :param news_articles_htmlTag: The HTML tag containing the news articles.
        :param news_articles_htmlClass: The class of the HTML tag containing the news articles.
        :param link_htmlTag: The HTML tag containing the link.
        :param link_htmlClass: The class of the HTML tag containing the link.
        :param filename: The name of the JSON file to save the extracted information.
        :param debug: Whether to print debug information.
        '''
        dictOfTags = {'Link': [link_htmlTag, link_htmlClass]}
        ListOfContents = []
        ListOfProcessedLinks = []
        ListOfProcessedUrls = []
        link = ''
        
        start_time = time.time()  # Record the start time
        s = requests.Session()
        s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'

        for i in range(len(pastURLs)):
            if "mailto:" or "@regiaodeleiria.pt" not in pastURLs[i]:
                try:
                    page = s.get(pastURLs[i], allow_redirects=True, timeout=10)
                    page.raise_for_status() 
                    
                    soup = BeautifulSoup(page.content, 'html.parser', from_encoding="UTF-8")
                    ListOfLinks = soup.find_all(dictOfTags["Link"][0], class_=dictOfTags["Link"][1])

                    for link_tag in ListOfLinks:
                        dictOfFeatures = {}
                        try:
                            link = link_tag.get('href') 
                            if link and link.startswith('/noFrame/replay/'):
                                link = link.replace('/noFrame/replay/', 'https://arquivo.pt/wayback/')
                            dictOfFeatures["Link"] = link if link else ' '
                        except AttributeError:
                            dictOfFeatures["Link"] = ' '

                        if dictOfFeatures["Link"] not in ListOfProcessedLinks and dictOfFeatures["Link"] != ' ':
                            pattern = r"https?://(?:arquivo\.pt/noFrame/replay/)?\d*/(https?://.*)"
                            match = re.search(pattern, dictOfFeatures["Link"])
                            if match:
                                url = match.group(1) 
                                if url not in ListOfProcessedUrls:
                                    ListOfProcessedUrls.append(url)
                                    ListOfProcessedLinks.append(dictOfFeatures["Link"])
                                    ListOfContents.append(dictOfFeatures)

                        if debug == True:
                             if i != 0 and i % 1 == 0: 
                                elapsed_time = time.time() - start_time
                                estimated_total_time = (elapsed_time / i) * len(pastURLs)
                                time_left = estimated_total_time - elapsed_time

                                if time_left > 0:
                                    minutes_left, seconds_left = divmod(time_left, 60)
                                    time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
                                else:
                                    time_left_str = "Done!"

                                print(f"\r{100 * i / len(pastURLs):.2f}% | Time left: {time_left_str}", end='')

                                if i == len(pastURLs) - 1:
                                    print(f"\r100.00% | Time left: Done!", end='')

        
                except requests.exceptions.RequestException as e:
                    print(f"Error processing URL {pastURLs[i]}: {e}")

        path = f"data/{year}/"
        if not os.path.exists(path):
            os.makedirs(path)

        with open(f'{path + filename}', 'w', encoding='utf-8') as fp:
            json.dump(ListOfProcessedLinks, fp, indent=4, ensure_ascii=False)



def get_news_articles_data(urls: list, year: str, filename: str, debug: bool, **kwargs):
    '''
    Get the data of the news articles from the past URLs.

    :param url: The URL where the data will be extracted.
    :param filename: The name of file where the data will be saved.
    :param debug: Show the debug the status 
    :param **kwargs: HTML tag and id/class pairs for categories (e.g., title, author, etc.), 
                     and optionally articleHtml_tag, articleHtml_class, and articleHtml_id 
                     for selecting a main article section.
    :return news_article_dict: A Dict object containing the (raw) data of the news article.
    '''
    
    ListOfTags = {}

    article_tag = kwargs.get('articleHtml_tag', None)
    article_class = kwargs.get('articleHtml_class', None)
    article_id = kwargs.get('articleHtml_id', None)
    
    start_time = time.time()  # Record the start time
    for kwarg, value in kwargs.items():
        if kwarg.endswith('Html_tag') and not kwarg.startswith('article'):
            category = kwarg.replace('Html_tag', '')
            html_tag = value
            html_class = kwargs.get(f"{category}Html_class", None)
            html_id = kwargs.get(f"{category}Html_id", None)
            ListOfTags[category] = {'tag': html_tag, 'class': html_class, 'id': html_id}

    # print(json.dumps(ListOfTags, indent=4))

    news_articles_list = []
    for i in range(len(urls)):
        page = requests.get(urls[i])
        soup = BeautifulSoup(page.text, 'html.parser')

        if article_tag:
            if article_id:
                article_section = soup.find(article_tag, id=article_id)
            elif article_class:
                article_section = soup.find(article_tag, class_=article_class)
            else:
                article_section = soup.find(article_tag)
        else:
            article_section = soup  # without a specific section, uses the whole page

        news_article = {
             "nid": len(news_articles_list),
             "og_url": urls[i]}
        
        for category, selectors in ListOfTags.items():
            tag = selectors['tag']
            html_class = selectors.get('class')
            html_id = selectors.get('id')
            
            # check if article_section is None
            if article_section is None:
                if debug:
                    print(f"Warning: article_section not found for {category}")
                continue 
            
            if html_id:
                element = article_section.find(tag, id=html_id)
            elif html_class:
                element = article_section.find(tag, class_=html_class)
            else:
                element = article_section.find(tag)  # if neither id nor class is specified, just find the tag

            if element is not None:
                if tag == "img":
                    text = element.get('src')
                else:
                    text = re.sub(r'\s+', ' ', element.get_text()).strip()
                    clean(text)
                
                news_article[category] = text
            else:
                if debug:
                    print(f"Warning: Element with tag '{tag}', id '{html_id}', class '{html_class}' not found for {category}")
        news_articles_list.append(news_article)
        if debug == True:
            if i != 0 and i % 1 == 0: 
                elapsed_time = time.time() - start_time
                estimated_total_time = (elapsed_time / i) * len(urls)
                time_left = estimated_total_time - elapsed_time

                if time_left > 0:
                    minutes_left, seconds_left = divmod(time_left, 60)
                    time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
                else:
                    time_left_str = "Done!"

                print(f"\r{100 * i / len(urls):.2f}% | Time left: {time_left_str}", end='')

                if i == len(urls) - 1:
                    print(f"\r100.00% | Time left: Done!", end='')
    
    path = f"data/{year}/"
    if not os.path.exists(path):
        os.makedirs(path)

    full_path = f'{path + filename}'
    if '.json' not in full_path:
         full_path += '.json'
    with open(f'{path + filename}', 'w', encoding='utf-8') as fp:
        json.dump(news_articles_list, fp, indent=4, ensure_ascii=False)

    return news_articles_list