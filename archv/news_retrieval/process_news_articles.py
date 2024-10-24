import json
import os
import time
import yake
import spacy
import torch
import numpy as np
import text_to_speech as tts
import pyttsx3

from transformers import AutoTokenizer, AutoModel

def extract_keywords(text: str, max_ngram_size=1, language="pt", num_of_kw=10, kw_extractor="yake"):
    '''
    Extract the most relevent keywords from a textual context
    '''
    deduplication_thresold = 0.9
    deduplication_algo = 'seqm'
    windowSize = 1
    keywords = []

    if kw_extractor == "yake":
        custom_kw_extractor = yake.KeywordExtractor(lan=language, windowsSize=windowSize, top=num_of_kw, features=None, n=max_ngram_size)
        keywords_tmp = custom_kw_extractor.extract_keywords(text)

        for kw in keywords_tmp:
            # print(kw)
            keywords.append(kw[0]) # ???
                        
    return keywords

def extract_named_entities(text: str, ner_extractor="spacy", language="pt"):
    '''
    Extract the named entities from a textual context
    '''
    data_PER = []
    data_ORG = []
    data_LOC = []
    data_MISC = []
    data_DATE = []
                    
    # entities scrapping using spaCy
    if ner_extractor == "spacy":
        model = 'pt_core_news_lg' # lg over sm, to get accuracy over efficieny
        nlp = spacy.load(model, disable=['tagger', 'parser'])

        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PER":
                if ent.text not in data_PER:
                    data_PER.append(ent.text)
            elif ent.label_ == "ORG":
                if ent.text not in data_ORG:
                    data_ORG.append(ent.text)
            elif ent.label_ == "LOC":
                if ent.text not in data_LOC:
                    data_LOC.append(ent.text)
            elif ent.label_ == "MISC":
                if ent.text not in data_MISC:
                    data_MISC.append(ent.text)
            elif ent.label_ == "DATE":
                if ent.text not in data_DATE:
                    data_DATE.append(ent.text)
                    
    return data_PER, data_ORG, data_LOC, data_MISC, data_DATE


def extract_keywords_news_articles(news_articles: list, year: str, filename: str, max_ngram_size=1, language="pt", num_of_kw=10, kw_extractor="yake"):
    '''
    Extract the most relevant keywords from a list of news articles

    :param news_articles: News articles list to be consumed.
    :param max_ngram_size: The size of gram considered ...
    '''

    start_time = time.time()  # Record the start time
    for i in range(len(news_articles)):
        if "text" in news_articles[i] and news_articles[i]["text"] is not None:
            kw = extract_keywords(text=news_articles[i]["text"], kw_extractor=kw_extractor)
            news_articles[i]["kw"] = kw
        
        if i != 0 and i % 1 == 0: 
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / i) * len(news_articles)
            time_left = estimated_total_time - elapsed_time

            if time_left > 0:
                minutes_left, seconds_left = divmod(time_left, 60)
                time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
            else:
                time_left_str = "Done!"

            print(f"\r{100 * i / len(news_articles):.2f}% | Time left: {time_left_str}", end='')

            if i == len(news_articles) - 1:
                print(f"\r100.00% | Time left: Done!", end='')
        

    if not os.path.exists(f"data/{year}/"):
        os.makedirs(f"data/{year}/")
    full_path = f'{f"data/{year}/" + filename}'
    if '.json' not in full_path:
         full_path += '.json'
    with open(full_path, 'w', encoding='utf-8') as fp:
        json.dump(news_articles, fp, indent=4, ensure_ascii=False)


def extract_named_entities_news_articles(news_articles: list, year: str, filename: str, ner_extractor="spacy", language="pt"):
    '''

    '''
    start_time = time.time()  # Record the start time
    for i in range(len(news_articles)):
        if "text" in news_articles[i] and news_articles[i]["text"] is not None:
            pers, org, loc, misc, date = extract_named_entities(news_articles[i]["text"], ner_extractor=ner_extractor, language=language)
            news_articles[i]["ner_pers"] = pers
            news_articles[i]["ner_org"] = org
            news_articles[i]["ner_loc"] = loc
            news_articles[i]["ner_misc"] = misc
            news_articles[i]["ner_date"] = date
        
        if i != 0 and i % 1 == 0: 
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / i) * len(news_articles)
            time_left = estimated_total_time - elapsed_time

            if time_left > 0:
                minutes_left, seconds_left = divmod(time_left, 60)
                time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
            else:
                time_left_str = "Done!"

            print(f"\r{100 * i / len(news_articles):.2f}% | Time left: {time_left_str}", end='')

            if i == len(news_articles) - 1:
                print(f"\r100.00% | Time left: Done!", end='')


    if not os.path.exists(f"data/{year}/"):
        os.makedirs(f"data/{year}/")
    full_path = f'{f"data/{year}/" + filename}'
    if '.json' not in full_path:
         full_path += '.json'
    with open(full_path, 'w', encoding='utf-8') as fp:
        json.dump(news_articles, fp, indent=4, ensure_ascii=False)


def get_embeddings_bert(text: str, model_name) -> list:
    '''
    
    '''
    model = AutoModel.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=False)
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    
    with torch.no_grad():
        output = model(**inputs)
        document_embedding = output.last_hidden_state.mean(dim=1).squeeze().detach().numpy().tolist()
    
    return document_embedding

def get_news_articles_embeddings(news_articles: list, year: str, filename: str, keys: list, model_name):
    '''
    Extracts embeddings for each news article by combining specified keys (e.g., title, author) with the article text,
    and saves them into a JSON file.

    Parameters:
        news_articles (list): List of dictionaries containing news articles.
        filename (str): The filename to save the embeddings.
        keys (list): List of keys to use from each article for constructing the text (e.g., title, author).
        tokenizer: Tokenizer used for the embeddings.
        model: Model used for extracting embeddings.
    '''
    
    embeddings_list = []
    start_time = time.time()  # Record the start time
    for i in range(len(news_articles)):
        embedding_dict = { 'nid': f"{news_articles[i]['nid']}", 'embeddings': [] }
        key_parts = ". ".join(
            [news_articles[i].get(key, '').strip().rstrip('.') for key in keys if news_articles[i].get(key, '').strip()])
        text = f"{key_parts}"

        embedding_dict["embeddings"] = get_embeddings_bert(text=text, model_name=model_name)
        embeddings_list.append(embedding_dict)

        if i != 0 and i % 1 == 0: 
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / i) * len(news_articles)
            time_left = estimated_total_time - elapsed_time

            if time_left > 0:
                minutes_left, seconds_left = divmod(time_left, 60)
                time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
            else:
                time_left_str = "Done!"

            print(f"\r{100 * i / len(news_articles):.2f}% | Time left: {time_left_str}", end='')

            if i == len(news_articles) - 1:
                print(f"\r100.00% | Time left: Done!", end='')

    if not os.path.exists(f"data/{year}/"):
        os.makedirs(f"data/{year}/")
    full_path = f'data/{year}/{filename}'
    
    if not full_path.endswith('.json'):
        full_path += '.json'

    with open(full_path, 'w', encoding='utf-8') as fp:
        print("Saved at", full_path)
        json.dump(embeddings_list, fp, indent=4, ensure_ascii=False)


def get_text_to_speech(tts_type: str, text: str, language: str, output_file: str):
    '''
    Converts input text into speech and saves it as an MP3 file.
    
    Args:
        tts_type (str): Type of text-to-speech engine ('text-to-speech', 'gcloud-tts', 'other-tts').
        text (str): The text that will be converted to speech.
        language (str): Language in IETF tag format (e.g., 'en' for English, 'pt' for Portuguese).
        output_file (str): Path to the output MP3 file. Must end with '.mp3'.

    Supported engines:
    - 'text-to-speech': Uses the text-to-speech PyPI package.
    - 'gcloud-tts': Google Cloud TTS implementation.
    - 'pyttsx3': Uses pyttsx3 package, limited to English ('en').
    
    Raises:
        ValueError: If the `output_file` does not end with '.mp3'.
    '''

    if not output_file.endswith('.mp3'):
        raise ValueError("Output file must have a .mp3 extension.")

    if tts_type == 'text-to-speech':
        tts.save(text, language, file=output_file)
        print(f"Text-to-speech conversion complete. Saved as {output_file}")
    
    elif tts_type == 'gcloud-tts':
        print("Google Cloud TTS is not implemented yet.")
    
    elif tts_type == 'pyttsx3':
        engine = pyttsx3.init() # object creation

        """ RATE"""
        rate = engine.getProperty('rate')   # getting details of current speaking rate
        #print (rate)                        #printing current voice rate
        engine.setProperty('rate', 125)     # setting up new voice rate

        """VOLUME"""
        volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
        #print (volume)                          #printing current volume level
        engine.setProperty('volume',1.0)        # setting up volume level  between 0 and 1

        """VOICE"""
        voices = engine.getProperty('voices')       #getting details of current voice
        #engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
        engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

        """Saving Voice to a file"""
        engine.save_to_file(text, filename=output_file)
        engine.runAndWait()
        print(f"Text-to-speech with pyttsx3 conversion complete. Saved as {output_file}")
    
    else:
        raise ValueError(f"Unsupported TTS type: {tts_type}")
    
    
def get_news_articles_tts(tts_type: str, news_articles: list, year: str, keys: list, language: str):
    start_time = time.time()  
    for i in range(len(news_articles)):
        key_parts = ". ".join(
            [news_articles[i].get(key, '').strip().rstrip('.') for key in keys if news_articles[i].get(key, '').strip()])
        text = f"{key_parts}"

        if not os.path.exists(f"data/{year}/"):
            os.makedirs(f"data/{year}/")
        filename = f"data/{year}/{news_articles[i]['nid']}.mp3"
        get_text_to_speech(tts_type=tts_type, text=text, language=language, output_file=filename)

        if i != 0 and i % 1 == 0: 
            elapsed_time = time.time() - start_time
            estimated_total_time = (elapsed_time / i) * len(news_articles)
            time_left = estimated_total_time - elapsed_time

            if time_left > 0:
                minutes_left, seconds_left = divmod(time_left, 60)
                time_left_str = f"{int(minutes_left)}m {int(seconds_left)}s"
            else:
                time_left_str = "Done!"

            print(f"\r{100 * i / len(news_articles):.2f}% | Time left: {time_left_str}", end='')

            if i == len(news_articles) - 1:
                print(f"\r100.00% | Time left: Done!", end='')
