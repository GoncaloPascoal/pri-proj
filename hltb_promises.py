import pandas as pd
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession
from tqdm import tqdm
import re

HLTB_CSV = "data/hltb.csv"

HEADERS = {
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}

def craft_game_search_future(game_name, session : FuturesSession):
    payload = {
        'queryString': game_name,
        't': 'games',
        'sorthead': 'popular',
        'sortd': 'Normal Order',
        'plat': '',
        'length_type': 'main',
        'length_min': '',
        'length_max': '',
        'detail': "hide_dlc"
    }

    return session.post('https://howlongtobeat.com/search_results.php', data=payload, headers=HEADERS)

def get_game_hltb_url_future(future, session : FuturesSession):
    r = future.result()

    assert r.status_code == 200
    if "No results for" in r.text:
        return "No results"

    hltb_url = BeautifulSoup(r.text, features="lxml").find("a")["href"]

    return session.get("https://howlongtobeat.com/" + hltb_url, headers=HEADERS)

def empty_game_playtime(appid):
    return {
        "appid" : appid,
        "Main Story" : 0, 
        "Main + Extras" : 0, 
        "Completionists" : 0,
    }

def convert_to_minutes(hm_string):
    match = re.search(r"((\d+)h\s?)?((\d+)m)?", hm_string)
    
    if match.group(2) == None:
        h = 0
    else:
        h = int(match.group(2))
    
    if match.group(4) == None:
        m = 0
    else:
        m = int(match.group(4))
    
    return int(h * 60 + m)

def get_game_playtime(game_url_future, appid):
    if game_url_future == "No results":
        return empty_game_playtime(appid)

    r = game_url_future.result()

    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find("table", {"class" : "game_main_table"})
    if table == None:
        return empty_game_playtime(appid)

    table_entries = table.find_all("tbody")
    
    res = {
        "appid" : appid
    }

    for category, entry in zip(("Main Story", "Main + Extras", "Completionists"), table_entries):
        if category not in str(entry):
            res[category] = 0
        else:
            res[category] = convert_to_minutes(entry.find_all("td")[2].text)
    
    return res

def get_missing_appids(appids):
    try:
        already_done_df = pd.read_csv(HLTB_CSV)
        already_done = set(list(already_done_df["appid"]))
        return list(set(appids) - already_done)
    except FileNotFoundError:
        return appids

def main():
    games = pd.read_csv('data/steam.csv')
    appids = list(games["appid"])
    name_lookup = {appid : name for appid, name in zip(list(games["appid"]), list(games["name"]))}

    session_1 = FuturesSession(max_workers=10)
    session_2 = FuturesSession(max_workers=10)

    try:
        already_done_df = pd.read_csv(HLTB_CSV)
        res = already_done_df.to_dict('records') # Lets continue from where we left off
    except FileNotFoundError:
        res = []

    missing_appids = get_missing_appids(appids)

    batches = [missing_appids[x:x+300] for x in range(0, len(missing_appids), 300)]
    # We need to do batches in order save progress regularly     

    for batch in tqdm(batches):
        futures_urls = [(appid, craft_game_search_future(name_lookup[appid], session_1)) for appid in batch]

        futures_results = [(appid, get_game_hltb_url_future(future, session_2)) for appid, future in futures_urls]

        res.extend([get_game_playtime(future, appid) for appid, future in futures_results])

        pd.DataFrame(res).to_csv(HLTB_CSV, index=False)


if __name__ == "__main__":
    main()