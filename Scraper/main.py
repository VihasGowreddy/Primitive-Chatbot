# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
from urllib import request
from bs4 import BeautifulSoup
from nltk import sent_tokenize
import os
import re
import math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import sqlite3
import pyrebase
import pandas as pd

firebaseConfig = {"apiKey": "AIzaSyDap-GPtbPxRCJwwsxAmNyhdM24Fx_XI5w",
                  "authDomain": "jordanbot-2a753.firebaseapp.com",
                  "databaseURL": "https://jordanbot-2a753-default-rtdb.firebaseio.com",
                  "projectId": "jordanbot-2a753",
                  "storageBucket": "jordanbot-2a753.appspot.com",
                  "messagingSenderId": "862087965887",
                  "appId": "1:862087965887:web:50c213631d9b579c496a0a",
                  "measurementId": "G-VDVTP2EZLM"}

firebase = pyrebase.initialize_app(firebaseConfig)
# auth = firebase.auth()
# storage = firebase.storeage()
db = firebase.database()

# db.child("Random Info")
# db.child("User Models")
# db.child("Statistics")
# db.child("Current User").set({"current username": "None"})
# db.child("Current User").update({"try": "None"})

# if os.path.exists("knowledge_base.db"):
#     os.remove("knowledge_base.db")
#
# conn = sqlite3.connect("knowledge_base.db")
# c = conn.cursor()


# def create_database():
#     c.execute("CREATE TABLE knowledgeBase (term REAL, sentence TEXT)")
#     conn.commit()


def preprocess(file_txt: str) -> list:
    '''
    preprocesses text
    :param file_txt: string representing content of file
    :return: filtered_tokens a list of lowercase filtered tokens with no punctuation or stopwords
    '''
    lower_txt = file_txt.lower()
    no_punc_txt = re.sub("[^\w\s]", " ", lower_txt)
    txt_tokens = word_tokenize(no_punc_txt)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [i for i in txt_tokens if i.isalpha() and i not in stop_words]
    return filtered_tokens


def clean_up_txt() -> list:
    index = 0
    total_sent_list = list()

    for filename in os.listdir("Unedited_txt"):
        if "url_contents" in filename:
            with open(os.path.join("Unedited_txt", filename), "r", encoding="utf-8") as f, open(
                    os.path.join("Edited_txt", f"{index}_url_contents_edited"), "w", encoding="utf-8") as f_write:
                unedited = f.read().replace("\n", "")
                edited = unedited.replace("\t", "")
                edited_sent = sent_tokenize(edited)
                for sent in edited_sent:
                    f_write.write(sent)
                    total_sent_list.append(sent)
            index += 1

    return total_sent_list


def webcrawler_scrape(starting_url: str) -> list:
    '''

    :param starting_url:
    :return:
    '''
    num_urls = 0
    url_queue = list()
    url_queue.insert(0, starting_url)

    while num_urls < 0:
        url = url_queue.pop()
        print(f"Link Currently being Scraped: {url}")
        print("--------------------------------------")
        r = requests.get(url)
        data = r.text
        soup = BeautifulSoup(data, "html.parser")

        for link in soup.find_all('a'):
            if link.get("href") is None or "map" in link.get("href"):
                continue

            if "https://" in link.get("href"):
                index_http = link.get("href").index("https://")
                end_index = len(link.get("href"))
                if "&sa=" in link.get("href"):
                    end_index = link.get("href").index("&sa=")
                print(link.get("href")[index_http:end_index])
                if link.get("href")[index_http:end_index] not in url_queue:
                    url_queue.insert(0, link.get("href")[index_http:end_index])
                num_urls += 1
            if num_urls >= 200:
                break

    url_queue.clear()
    url_queue.append("https://en.wikipedia.org/wiki/Michael_Jordan")
    url_queue.append("https://en.wikipedia.org/wiki/List_of_career_achievements_by_Michael_Jordan")
    url_queue.append("https://en.wikipedia.org/wiki/1984_NBA_draft")
    url_queue.append("https://www.sbnation.com/secret-base/22307608/seagram-award-michael-jordan-mvp-1987")
    url_queue.append("https://www.nba.com/history/legends/profiles/michael-jordan")
    url_queue.append("https://www.nba.com/stats/player/893/career/")
    url_queue.append("https://bleacherreport.com/articles/2888183-how-michael-jordan-broke-the-jordan-rules")
    url_queue.append("https://www.cnbc.com/2020/05/17/michael-jordan-was-jerk-says-teammates-why-it-helped.html")
    url_queue.append(
        "https://www.essentiallysports.com/nba-news-on-this-day-michael-jordan-signed-a-deal-that-changed-nba-forever-chicago-bulls-basketball/")
    url_queue.append(
        "https://www.theguardian.com/sport/2020/may/24/michael-jordan-was-years-ahead-of-his-game-the-last-dance-showed-that-he-still-is")
    url_queue.append(
        "https://www.cbssports.com/nba/news/michael-jordan-didnt-retire-just-because-of-jerry-krause-who-continues-to-be-disproportionately-vilified/")
    url_queue.append("https://faze.ca/michael-jordan-a-global-icon/")
    url_queue.append(
        "https://www.miningjournal.net/sports/2020/05/chicago-bulls-teammates-saw-first-hand-the-price-michael-jordan-had-to-pay-for-excellence/")
    url_queue.append("https://www.biography.com/athlete/michael-jordan")
    url_queue.append("https://www.usatoday.com/story/gameon/2012/12/12/nba-jordan-bulls-12/1763265/")
    url_queue.append("https://www.basketball-reference.com/players/j/jordami01.html")
    url_queue.append("https://www.basketball-reference.com/players/j/jordami01/gamelog-playoffs/")
    url_queue.append("https://www.basketball-reference.com/teams/WAS/2002.html")
    url_queue.append("https://www.basketball-reference.com/teams/CHI/1985.html")

    for count, url in enumerate(url_queue):
        with open(os.path.join("Unedited_txt", f"{count}_url_contents"), "w", encoding="utf-8") as f:
            # print(count)
            html = request.urlopen(url).read().decode("utf8")
            soup = BeautifulSoup(html, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            f.write(text)

    return url_queue


def tf_idf_frequency() -> dict:
    total_doc_tokens = list()
    idf_dict = dict()  # key is word and value is num documents that word occurs in
    num_docs = 0
    for filename in os.listdir("Edited_txt"):
        if "url_contents_edited" in filename:
            with open(os.path.join("Edited_txt", filename), "r", encoding="utf-8") as f:
                file_txt = f.read()
                file_preprocessed_tokens = preprocess(file_txt)
                total_doc_tokens.extend(file_preprocessed_tokens)
                num_docs += 1
                for token in set(file_preprocessed_tokens):
                    if token not in idf_dict:
                        idf_dict[token] = 1
                    else:
                        idf_dict[token] = idf_dict[token] + 1
    # print(total_doc_tokens)
    # print(type(total_doc_tokens))
    tf_idf_dict = dict()
    occurrences = Counter(total_doc_tokens)
    frequency_temp = {key: ((value / len(total_doc_tokens)) * math.log((1 + num_docs) / (1 + idf_dict[key]))) for
                      (key, value) in occurrences.items()}
    sorted_keys = sorted(frequency_temp, key=frequency_temp.get)
    for word in sorted_keys:
        tf_idf_dict[word] = frequency_temp[word]

    return tf_idf_dict


if __name__ == '__main__':

    starting_url = "https://www.google.com/search?q=michael+jordan&rlz=1C1SQJL_enUS807US807&oq=michael+jordan+&aqs=chrome.0.69i59l3j35i39j0j69i60l3.3303j0j7&sourceid=chrome&ie=UTF-8"

    url_queue = webcrawler_scrape(starting_url)
    sent_list = clean_up_txt()

    frequency_dict = tf_idf_frequency()
    print("\nList of Top 40 Terms by Frequency")
    print(list(frequency_dict.keys())[-40:])

    term_list = ["nba", "chicago", "vs", "career", "finals", "points", "season"]
    terms_added = []

    # create_database()

    for term in term_list:
        to_reach = 0
        for sent in sent_list:
            if term in sent or term.capitalize() in sent:
                print(sent)
                print("\n")
                confirm = input("Add to database: ")
                if confirm == "y" or confirm == "yes":
                    db.child("Random Info").child(term).push({"sentence": sent})
                    to_reach += 1
                if to_reach == 10:
                    break

                # c.execute("INSERT INTO knowledgeBase (term, sentence) VALUES (?,?)",
                #           (term, sent))
                # conn.commit()
    # c.execute("INSERT INTO knowledgeBase (term, sentence) VALUES (?,?)", ("vs", "asdfasdfasdf fasdf d"))
    # conn.commit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
