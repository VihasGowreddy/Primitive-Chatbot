from typing import Any, Dict, Tuple
from datetime import datetime
from fastapi import Body, FastAPI
from pydantic import BaseModel
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from numpy import dot
from numpy.linalg import norm
import random
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

app = FastAPI()


class Intent(BaseModel):
    displayName: str


class Request(BaseModel):
    queryText: str
    intent: Intent
    parameters: Dict[str, Any]
    # outputContext: OutputContext


def dfs_formatted():
    df_dict = dict()
    df_dict["College Stats"] = pd.read_csv("Chatbot/all_college_stats.csv")
    df_dict["Game Highs"] = pd.read_csv("Chatbot/game_highs.csv")
    df_dict["Per Game"] = pd.read_csv("Chatbot/per_game.csv")
    df_dict["Playoffs"] = pd.read_csv("Chatbot/playoffs_per_game.csv")
    df_dict["Against Teams"] = pd.read_csv("Chatbot/against_teams.csv")
    return df_dict


def get_career_points(df_dict: dict):
    return df_dict["Per Game"].PTS.iloc[21]


def get_season_points(df_dict: dict, season: str):
    return df_dict["Per Game"].where(df_dict["Per Game"]["Season"] == season).PTS.dropna()[0]


def get_career_rebounds(df_dict: dict):
    return df_dict["Per Game"].TRB.iloc[21]


def get_season_rebounds(df_dict: dict, season: str):
    return df_dict["Per Game"].where(df_dict["Per Game"]["Season"] == season).TRB.dropna()[0]


def get_career_assists(df_dict: dict):
    return df_dict["Per Game"].AST.iloc[21]


def get_season_assists(df_dict: dict, season: str):
    return df_dict["Per Game"].where(df_dict["Per Game"]["Season"] == season).AST.dropna()[0]


def get_against_team(df_dict: dict, opp: str, stat: str) -> float:
    if stat == "points" or stat == "points per game" or stat == "ppg" or stat == "pts":
        stat = "PPG"
    elif stat == "assists" or stat == "assists per game" or stat == "apg":
        stat = "APG"
    elif stat == "rebounds" or stat == "rebounds per game" or stat == "rpg" or stat == "trb":
        stat = "RPG"
    elif stat == "steals" or stat == "steals per game" or stat == "spg" or stat == "stl":
        stat = "SPG"
    elif stat == "blocks" or stat == "blocks per game" or stat == "bpg" or stat == "blk":
        stat = "BPG"
    elif stat == "field goal percentage" or stat == "field goal percent" or stat == "percent field goal" or stat == "fg%":
        stat = "FG%"
    index = df_dict[df_dict["OPP"] == opp].index.values.astype(int)
    return df_dict[stat].values[index].tolist()[0]


def get_random_against_team_stat(df_dict: dict, opp: str) -> Tuple[float, str]:
    retrieve_list = ["PPG", "RPG", "APG", "SPG", "BPG"]
    index = random.randint(0, len(retrieve_list) - 1)
    stat = get_against_team(df_dict["Against Teams"], opp, retrieve_list[index])
    return stat, retrieve_list[index]


df_dict = dfs_formatted()


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
    nba_teams["Atlanta"] = ["Hawks", "ATL"]
    nba_teams["Boston"] = ["Celtics", "BOS"]
    nba_teams["Charlotte"] = ["Hornets", "CHA"]
    nba_teams["Chicago"] = ["Bulls", "CHI"]
    nba_teams["Cleveland"] = ["Cavaliers", "CLE"]
    nba_teams["Dallas"] = ["Mavericks", "DAL"]
    nba_teams["Denver"] = ["Nuggets", "DEN"]
    nba_teams["Detroit"] = ["Pistons", "DET"]
    nba_teams["Golden State "] = ["Warriors", "GSW"]
    nba_teams["Houston"] = ["Rockets", "HOU"]
    nba_teams["Indiana"] = ["Pacers", "IND"]
    nba_teams["Los Angeles"] = ["Clippers", "LAC"]
    nba_teams["Los Angeles"] = ["Lakers", "LAL"]
    nba_teams["Memphis"] = ["Grizzlies", "MEM"]
    nba_teams["Miami"] = ["Heat", "MIA"]
    nba_teams["Milwaukee"] = ["Bucks", "MIL"]
    nba_teams["Minnesota"] = ["Timberwolves", "MIN"]
    nba_teams["New Jersey"] = ["Nets", "NJN"]
    nba_teams["New Orleans"] = ["Pelicans", "NOP"]
    nba_teams["New York"] = ["Knicks", "NYK"]
    nba_teams["Orlando"] = ["Magic", "ORL"]
    nba_teams["Philadelphia"] = ["76ers", "PHI"]
    nba_teams["Phoenix"] = ["Suns", "PHX"]
    nba_teams["Portland"] = ["Trail Blazers", "POR"]
    nba_teams["Sacramento"] = ["Kings", "SAC"]
    nba_teams["San Antonio"] = ["Spurs", "SAS"]
    nba_teams["Seattle"] = ["SuperSonics", "SEA"]
    nba_teams["Toronto"] = ["Raptors", "TOR"]
    nba_teams["Utah"] = ["Jazz", "UTA"]
    nba_teams["Washington"] = ["Wizards", "WAS"]
    return nba_teams


question_list = ["Leave", "Exit", "I'm done", "I have no more questions", "Tell me a fact about you",
                 "Give me a Jordan fact", "Tell me a random fact about you", "What is a random fact about you?",
                 "Tell me a random fact about Jordan", "What is a random fact about Jordan?", "Functionality",
                 "What functionality do you have", "What options do I have", "What can I ask?", "What can you do?"]


def handle_fallback(query_text: str) -> str:
    highest_cosine_similarity = 0
    closest_response = ""
    for response in question_list:
        cosine_val = cosine_similarity(query_text, response)
        # print(cosine_val)
        # print(response)
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


term_list = ["jordan", "game", "bulls", "chicago", "vs", "career", "finals", "points", "season"]


def handle_random_fact() -> str:
    username = db.child("Current User").get().val()['current username']
    user_root = db.child("User Models").child(username).get().val()

    key_to_use = term_list[random.randint(0, len(term_list) - 1)]
    if 'previous fact' not in user_root.keys():
        # key_to_use = term_list[random.randint(0, len(term_list) - 1)]
        iterator = iter(db.child("Random Info").child(key_to_use).get().val())
        next(iterator)
        next(iterator)
        key_of_info = next(iterator)
        info = db.child("Random Info").child(key_to_use).child(key_of_info).get().val()["sentence"]
        db.child("User Models").child(username).update({"last info given": info})
        text = f"{info}\nDid you find this fact interesting?"

    elif 'previous fact' in user_root.keys() and user_root['liked fact'] == "True":
        shortest_leven_dist = 100000
        shortest_leven_info = ""

        info_interesting = user_root["previous fact"]

        for sentence in db.child("Random Info").child(key_to_use).get().val().values():
            current_leven_dist = levenshtein_distance(info_interesting, sentence)
            if current_leven_dist < shortest_leven_dist:
                shortest_leven_dist = current_leven_dist
                shortest_leven_info = sentence

        db.child("User Models").child(username).update({"last info given": shortest_leven_info})
        text = f"{shortest_leven_info}\nDid you find this fact interesting?"

    else:
        longest_leven_dist = 0
        longest_leven_info = ""

        info_interesting = user_root["previous fact"]

        for sentence in db.child("Random Info").child(key_to_use).get().val().values():
            current_leven_dist = levenshtein_distance(info_interesting, sentence)
            if current_leven_dist > longest_leven_dist:
                longest_leven_dist = current_leven_dist
                longest_leven_info = sentence

        db.child("User Models").child(username).update({"last info given": longest_leven_info})
        text = f"{longest_leven_info}\nDid you find this fact interesting?"

    return text


def handle_random_fact_no() -> str:
    username = db.child("Current User").get().val()['current username']
    db.child("User Models").child(username).update({"liked fact": "False"})
    return "I'll keep that in mind next time"


def handle_random_fact_yes() -> str:
    username = db.child("Current User").get().val()['current username']
    db.child("User Models").child(username).update({"liked fact": "True"})
    return "I'll keep that in mind next time"


########################
def handle_created_username(username: str) -> str:
    db.child("Current User").set({"current username": username})
    favorite_team = db.child("User Models").child(username).get().val()["favorite team"]
    return_text = f"Welcome back {username}. "

    if favorite_team == "None":
        return_text += "Just want to remind you unfortunate it is that your city's inhabitants couldn't witness Jordan destroying their team."
    else:
        stat_val, stat_measure = get_random_against_team_stat(df_dict, favorite_team)
        return_text += f"Just wanted to let you know that Jordan dropped an average of {stat_val} {stat_measure} on the {favorite_team}"
    return return_text


def handle_username(username: str) -> Tuple[list, str]:
    user_list = db.child("User Models").get().val().keys()
    if username in user_list:
        output_context = [dict(), dict(), dict()]
        output_context[0][
            "name"] = "projects/jordan-infobot-eaok/locations/global/agent/sessions/f75dcaba-b09f-6dc5-7f5c-f6f0f2c6cc5b/contexts/ask_if_conversed-followup"
        output_context[0]["lifespanCount"] = 1
        output_context[1][
            "name"] = "projects/jordan-infobot-eaok/locations/global/agent/sessions/f75dcaba-b09f-6dc5-7f5c-f6f0f2c6cc5b/contexts/default_welcome_intent-followup"
        output_context[1]["lifespanCount"] = 1
        output_context[2][
            "name"] = "projects/jordan-infobot-eaok/locations/global/agent/sessions/f75dcaba-b09f-6dc5-7f5c-f6f0f2c6cc5b/contexts/created_account-no-followup"
        output_context[2]["lifespanCount"] = 1
        return output_context, "This username is already taken. Please create a new username"

    db.child("Current User").set({"current username": username})
    return [], f"Welcome {username}! Do you have a favorite team?"


#############
def handle_favorite_team(team: str) -> str:
    team_list = nba_team_dict()
    team_found = False
    for team_syn in list(team_list.values()):
        if team in team_syn:
            team_found = True
            break
    if not team_found:
        team = "None"
    elif team_found and len(team) == 3:
        for key in team_list:
            if team_list[key][1] == team:
                team = team_list[key][0]
                break

    username = db.child("Current User").get().val()['current username']
    db.child("User Models").child(username).set({"favorite team": team})

    if team != "None":
        stat_val, stat_measure = get_random_against_team_stat(df_dict, team)
        return_text = f"Thanks {username}. Looks like Jordan destroyed your {team} by averaging {stat_val} {stat_measure}"
    else:
        return_text = f"Thanks {username}. I didn't recognize the team you entered so looks like you're lucky they never faced Jordan"
    return return_text


##############
def handle_favorite_location(city: str) -> str:
    username = db.child("Current User").get().val()['current username']
    team_list = nba_team_dict()

    if city in team_list.keys():
        hometown_team = team_list[city][0]
        db.child("User Models").child(username).set({"favorite team": hometown_team})
        stat_val, stat_measure = get_random_against_team_stat(df_dict, hometown_team)
        return_text = f"Thanks {username}. Jordan destroyed your hometown team, the {hometown_team}, by averaging {stat_val} {stat_measure}"
    else:
        db.child("User Models").child(username).set({"favorite team": "None"})
        return_text = f"Thanks {username}. Looks like your hometown doesn't have a team or didn't have a team when Jordan played. Unlucky that your city was unable to witness greatness."

    return return_text


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


def convert_stat(stat: str) -> str:
    if stat == "points" or stat == "points per game" or stat == "ppg" or stat == "pts":
        stat_ret = "PTS"
    elif stat == "assists" or stat == "assists per game" or stat == "apg":
        stat_ret = "AST"
    elif stat == "rebounds" or stat == "rebounds per game" or stat == "rpg" or stat == "trb":
        stat_ret = "TRB"
    elif stat == "steals" or stat == "steals per game" or stat == "spg" or stat == "stl":
        stat_ret = "STL"
    elif stat == "blocks" or stat == "blocks per game" or stat == "bpg" or stat == "blk":
        stat_ret = "BLK"
    elif stat == "field goal percentage" or stat == "field goal percent" or stat == "percent field goal" or stat == "fg%":
        stat_ret = "FG%"
    return stat_ret


@app.post("/")
async def home(queryResult: Request = Body(..., embed=True)):
    intent = queryResult.intent.displayName
    # print(intent)
    if intent == "Default_Welcome_Intent - fallback":
        text = handle_fallback(queryResult.queryText)

    elif intent == "Enter_Username":
        context_list, text = handle_username(queryResult.parameters["Username"])
        if len(context_list) == 0:
            return {"fulfillmentText": text}
        return {"fulfillmentText": text, "outputContexts": context_list}

    elif intent == "Enter_Favorite_Team":
        text = handle_favorite_team(queryResult.parameters["BasketballTeam"])

    elif intent == "Enter_Favorite_City":
        text = handle_favorite_location(queryResult.parameters["geo-city"])

    elif intent == "Provide_Created_Username":
        text = handle_created_username(queryResult.parameters["Username"])

    elif intent == "Jordan_Random_Fact":
        text = handle_random_fact()

    elif intent == "Jordan_Random_Fact-no":
        text = handle_random_fact_no()

    elif intent == "Jordan_Random_Fact-yes":
        text = handle_random_fact_yes()

    elif intent == "Jordan_Stat":
        stat_type = queryResult.parameters["BasketballStat"]
        opp_team = queryResult.parameters["BasketballTeam"]
        if stat_type == "" and opp_team == "":
            text = "Michael Jordan has 6 NBA championship rings"
        elif opp_team == "":
            question = queryResult.queryText
            stat_convert_type = convert_stat(stat_type)
            if "college" in question or "university" in question:
                stat_val = df_dict["College Stats"][stat_convert_type].values[3]
                text = f"Jordan averaged {stat_val} {stat_type} in college"
            elif "playoffs" in question:
                stat_val = df_dict["Playoffs"][stat_convert_type].values[13]
                text = f"Jordan averaged {stat_val} {stat_type} in the NBA playoffs"
            else:
                stat_val = df_dict["Per Game"][stat_convert_type].values[19]
                text = f"Jordan averaged {stat_val} {stat_type} per game in the NBA"
        else:
            stat_val = get_against_team(df_dict["Against Teams"], opp_team, stat_type)
            text = f"For his career, Jordan averaged {stat_val} {stat_type} against the {opp_team}"
    #########
    # Add the season specific information

    else:
        text = "I'm not sure how to help with that"

    return {"fulfillmentText": text}
