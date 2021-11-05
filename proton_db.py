from requests_futures.sessions import FuturesSession
import pandas as pd
from tqdm import tqdm

def parse_future(future):
    answer = future.result()

    if answer.status_code == 404:
        return {
            "appid" : future.appid,
            "protondb_reports" : 0,
            "protondb_tier" : "unknown",
        }
    else:
        data = answer.json()
        return {
            "appid" : future.appid,
            "protondb_reports" : data["total"],
            "protondb_tier" : data["tier"],
        }

def main():
    games = pd.read_csv('data/steam.csv')
    appids = list(games["appid"])

    session = FuturesSession(max_workers=10)
    
    futures=[]
    for appid in appids:
        future = session.get(f"https://www.protondb.com/api/v1/reports/summaries/{appid}.json")
        future.appid = appid
        futures.append(future)

    res = []
    for future in tqdm(futures):
        res.append(parse_future(future))

    pd.DataFrame(res).to_csv('data/proton_db.csv', index=False)

if __name__ == "__main__":
    main()