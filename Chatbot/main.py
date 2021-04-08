from typing import Any, Dict

from fastapi import Body, FastAPI
from pydantic import BaseModel
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

# client = dialogflow_v2beta1.AgentsClient()
# app = FastAPI()
#
#
# class Intent(BaseModel):
#     displayName: str
#
#
# class Request(BaseModel):
#     intent: Intent
#     parameters: Dict[str, Any]
#
#
# class OutputContext(BaseModel):
#     name: str


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


# @app.post("/")
# async def home(queryResult: Request = Body(..., embed=True)):
#     intent = queryResult.intent.displayName
#     count = len(queryResult.parameters)
#     text = f"I'm responding to the {intent} intent with {count} slots found: "
#     text += ",".join(queryResult.parameters.values())
#     return {"fulfillmentText": text}

if __name__ == '__main__':
    #     os.path.join("/c/Users/vihas/Desktop/UTDALLAS", "\"Semester 8\"/NLP/jordan-infobot-eaok-2dd0da1e3e3a.json")
    #     if os.path.exists("../../jordan-infobot-eaok-2dd0da1e3e3a.json"):
    #         print("IS FILE")
    #     else:
    #         print("IS NOT FILE")
    #     explicit()
    nba_teams = teams.get_teams()
    sonics = [team for team in nba_teams if team['abbreviation'] == 'SAS'][0]
    sonics_id = sonics['id']

    jordan = players.find_players_by_full_name("Lebron James")
    jordan_id = jordan[0]['id']
    print(jordan_id)

    # If you want all seasons, you must import the SeasonAll parameter
    from nba_api.stats.library.parameters import SeasonAll
    import pandas as pd

    gamelog_bron_all = playergamelog.PlayerGameLog(player_id=jordan_id, season=SeasonAll.all)

    df_jordan_games = playergamelog.PlayerGameLog(player_id=jordan_id, season=SeasonAll.all)
    #print(df_jordan_games)

    payton = players.find_players_by_full_name("Kobe Bryant")
    payton_id = payton[0]['id']

    print(playervsplayer.PlayerVsPlayer(player_id=jordan_id, vs_player_id=payton_id).get_data_frames())
