import requests
import pandas as pd

def parse_page(game_id):
    url = f"https://www.protondb.com/api/v1/reports/summaries/{game_id}.json"
    answer = requests.get(url)

    if answer.status_code == 404:
        return {
            "appid" : game_id,
            "protondb_reports" : 0,
            "protondb_tier" : "unknown",
        }
    else:
        data = answer.json()
        return {
            "appid" : game_id,
            "protondb_reports" : data["total"],
            "protondb_tier" : data["tier"],
        }

def main():
    games = pd.read_csv('data/steam.csv')
    appids = list(games["appid"])
    
    res = []

    for appid in appids:
        res.append(parse_page(appid))
    
    pd.DataFrame(res).to_csv('data/proton_db.csv', index=False)

if __name__ == "__main__":
    main()