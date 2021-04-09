from typing import Any, Dict

from fastapi import Body, FastAPI
from pydantic import BaseModel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from numpy import dot
from numpy.linalg import norm
import random

import dialogflow_v2beta1
import os

from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import playervsplayer
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll


# def explicit():
#     from google.cloud import storage
#
#     # Explicitly use service account credentials by specifying the private key
#     # file.
#     storage_client = storage.Client.from_service_account_json(
#         '../../jordan-infobot-eaok-2dd0da1e3e3a.json')
#
#     # Make an authenticated API request
#     buckets = list(storage_client.list_buckets())
#     print(buckets)

#client = dialogflow_v2beta1.AgentsClient()
app = FastAPI()


class Intent(BaseModel):
    displayName: str

#class OutputContext(BaseModel):
#    name: str

class Request(BaseModel):
    queryText: str
    intent: Intent
    parameters: Dict[str, Any]
    #outputContext: OutputContext


def levenshtein_distance(stem: str, word: str):
    '''

    :param stem: string corresponding to the stem of a word
    :param word: string corresponding to the word that is being compared to it's stem
    :return: the edit distance (number of letters that need to be changed, deleted, or added to make both strings equal)
    '''
    stem_len = len(stem) + 1
    word_len = len(word) + 1
    matrix = [[0 for x in range(word_len)] for y in range(stem_len)]

    for x in range(1, stem_len):
        matrix[x][0] = x

    for y in range(1, word_len):
        matrix[0][y] = y

    substitution_cost = 0
    for y in range(1, word_len):
        for x in range(1, stem_len):
            if stem[x - 1] == word[y - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1
            matrix[x][y] = min(matrix[x - 1][y] + 1, matrix[x][y - 1] + 1, matrix[x - 1][y - 1] + substitution_cost)

    return matrix[stem_len - 1][word_len - 1]


def nba_team_dict() -> dict:
    nba_teams = dict()
    nba_teams["Atlanta Hawks"] = "ATL"
    nba_teams["Boston Celtics"] = "BOS"
    nba_teams["Brooklyn Nets"] = "BKN"
    nba_teams["Charlotte Hornets"] = "CHA"
    nba_teams["Chicago Bulls"] = "CHI"
    nba_teams["Cleveland Cavaliers"] = "CLE"
    nba_teams["Dallas Mavericks"] = "DAL"
    nba_teams["Denver Nuggets"] = "DEN"
    nba_teams["Detroit Pistons"] = "DET"
    nba_teams["Golden State Warriors"] = "GSW"
    nba_teams["Houston Rockets"] = "HOU"
    nba_teams["Indiana Pacers"] = "IND"
    nba_teams["Los Angeles Clippers"] = "LAC"
    nba_teams["Los Angeles Lakers"] = "LAL"
    nba_teams["Memphis Grizzlies"] = "MEM"
    nba_teams["Miami Heat"] = "MIA"
    nba_teams["Milwaukee Bucks"] = "MIL"
    nba_teams["Minnesota Timberwolves"] = "MIN"
    nba_teams["New Jersey Nets"] = "NJN"
    nba_teams["New Orleans Hornets"] = "NOK"
    nba_teams["New Orleans Pelicans"] = "NOP"
    nba_teams["New York Knicks"] = "NYK"
    nba_teams["Oklahoma City Thunder"] = "OKC"
    nba_teams["Orlando Magic"] = "ORL"
    nba_teams["Philadelphia 76ers"] = "PHI"
    nba_teams["Phoenix Suns"] = "PHX"
    nba_teams["Portland Trailblazers"] = "POR"
    nba_teams["Sacramento Kings"] = "SAC"
    nba_teams["San Antonio Spurs"] = "SAS"
    nba_teams["Seattle SuperSonics"] = "SEA"
    nba_teams["Toronto Raptors"] = "TOR"
    nba_teams["Utah Jazz"] = "UTA"
    nba_teams["Vancouver Grizzlies"] = "VAN"
    nba_teams["Washington Bullets"] = "WAS"
    nba_teams["Washington Wizards"] = "WAS"
    return nba_teams

question_list = ["Leave", "Exit", "I'm done", "I have no more questions", "Tell me a fact about you", "Give me a Jordan fact", "Tell me a random fact about you", "What is a random fact about you?", "Tell me a random fact about Jordan", "What is a random fact about Jordan?", "Functionality", "What functionality do you have", "What options do I have", "What can I ask?", "What can you do?"]
def handle_fallback(query_text: str) -> str:
    highest_cosine_similarity = 0
    closest_response = ""
    for response in question_list:
        cosine_val = cosine_similarity(query_text, response)
        #print(cosine_val)
        #print(response)
        if cosine_val != 0 and cosine_val >= highest_cosine_similarity:
            highest_cosine_similarity = cosine_val
            closest_response = response

    fullfillment_txt_return = ""
    if closest_response != "":
        fullfillment_txt_return += f"I didn't understand what you said. Did you mean \"{closest_response}\"? If yes, type the response. If no, some questions/responses I can act on are "
    else:
        fullfillment_txt_return += "I didn't understand what you said. Some questions/responses I can act on are "
    for x in range(0, 3):
        index = random.randint(0, len(question_list) - 1)
        if x != 2:
            fullfillment_txt_return += f"\"{question_list[index]}\", "
        else:
            fullfillment_txt_return += f"\"{question_list[index]}\"."

    return fullfillment_txt_return


def handle_random_fact() -> str:
    return "Here is a fact"


def cosine_similarity(query_text: str, prebuilt_questions: str) -> int:
    query_tokens = word_tokenize(query_text)
    question_tokens = word_tokenize(prebuilt_questions)
    stop_words = stopwords.words("english")
    occurrences_query = list()
    occurrences_question = list()

    query_no_stopwords = [x for x in query_tokens if x not in stop_words]
    question_no_stopwords = [x for x in question_tokens if x not in stop_words]
    query_set = set(query_no_stopwords)
    question_set = set(question_no_stopwords)
    vocab = query_set.union(question_set)
    sorted_vocab = sorted(vocab)

    for word in sorted_vocab:
        if word in query_set:
            occurrences_query.append(query_tokens.count(word))
        else:
            occurrences_query.append(0)
        if word in question_set:
            occurrences_question.append(question_tokens.count(word))
        else:
            occurrences_question.append(0)

    return float(dot(occurrences_query, occurrences_question)) / (norm(occurrences_query) * norm(occurrences_question))


intent_dict = {
    "Default Fallback Intent": handle_fallback,
    "Jordan_Random_Fact": handle_random_fact,
}

@app.post("/")
async def home(queryResult: Request = Body(..., embed=True)):
    intent = queryResult.intent.displayName
    #print(intent)
    if intent == "Welcome_Fallback_Intent":
        text = handle_fallback(queryResult.queryText)
    elif intent == "Jordan_Random_Fact":
        handle_random_fact()
    else:
        text = "I'm not sure how to help with that"
    # if handler := intent_dict.get(intent):
    #     text = handler(**queryResult.parameters)
    # else:
    #     text = "I'm not sure how to help with that"
    return {"fulfillmentText": text}

# if __name__ == '__main__':
# #     #print(handle_fallback("What can you say?"))
# # #     #     os.path.join("/c/Users/vihas/Desktop/UTDALLAS", "\"Semester 8\"/NLP/jordan-infobot-eaok-2dd0da1e3e3a.json")
# # #     #     if os.path.exists("../../jordan-infobot-eaok-2dd0da1e3e3a.json"):
# # #     #         print("IS FILE")
# # #     #     else:
# # #     #         print("IS NOT FILE")
# # #     #     explicit()
#     nba_teams = teams.get_teams()
#     sonics = [team for team in nba_teams if team['abbreviation'] == 'UTA'][0]
#     sonics_id = sonics['id']
#
#     jordan = players.find_players_by_full_name("Lebron James")
#     jordan_id = jordan[0]['id']
#     print(jordan_id)
#
#     # If you want all seasons, you must import the SeasonAll parameter
#     from nba_api.stats.library.parameters import SeasonAll
#     from nba_api.stats.endpoints import PlayerDashboardByOpponent
#     import nba_api.stats.library.parameters as nba_params
#     import pandas as pd
#
#     gamelog_bron_all = playergamelog.PlayerGameLog(player_id=jordan_id, season=SeasonAll.all)
#
#     df_jordan_games = playergamelog.PlayerGameLog(player_id=jordan_id, season=SeasonAll.all)
#     #print(df_jordan_games)
#
#     payton = players.find_players_by_full_name("Patrick Ewing")
#     payton_id = payton[0]['id']
#
#     print(PlayerDashboardByOpponent(player_id=jordan_id, opponent_team_id=sonics_id).get_data_frames())
