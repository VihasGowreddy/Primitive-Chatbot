from urllib.request import urlopen
import pandas as pd
from urllib import request
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio
import nest_asyncio
import pyrebase
from os import path


firebase_config = {"apiKey": "AIzaSyDapqZlf62xaytO4xix6BUcYCt9DpMPaZ4",
    "authDomain": "mj-chatbot.firebaseapp.com",
    "projectId": "mj-chatbot",
    "storageBucket": "mj-chatbot.appspot.com",
    "messagingSenderId": "362248514135",
   "appId": "1:362248514135:web:f3a51bb13a937f9f431112",
    "measurementId": "G-MGFQ0NFXMP",
    "databaseURL": '000'
}

firebase =pyrebase.initialize_app(firebase_config)
#auth = firebase.auth()
storage = firebase.storage()


nest_asyncio.apply()


async def get_player_selector(url, selector):

# with reference to basketball-reference-scraper https://pypi.org/project/basketball-reference-web-scraper/
    # Launch the browser and a new page
    browser = await launch()
    page = await browser.newPage()
    await page.goto(url)
    await page.waitForSelector(f'{selector}')
    table = await page.querySelectorEval(f'{selector}', '(element) => element.outerHTML')
    await browser.close()
    # Use pandas to read the table easily
    return table

url = "https://www.basketball-reference.com/players/j/jordami01.html"
selectors= ["#per_game","#game_highs","#playoffs_per_game","#all_all_salaries","#all_college_stats","#leaderboard_notable-awards"]
df_dict = dict()
for selector in selectors:
    print(selector)
    table = asyncio.get_event_loop().run_until_complete(get_player_selector(url, selector))
    df = pd.read_html(table)[0]
    selector = selector[1:]
    df_dict[selector] = df 
print("Done")
for key in df_dict:

    fname = f"bbref_data/{key}.csv"
    df_dict[key].to_csv(fname)
    storage.child(fname).put(f"/Users/narain/Classes/CS-4395/cs-4395/week-9/Primitive-Chatbot/bbref_data/{key}.csv")
    
    
