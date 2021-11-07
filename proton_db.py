from requests_futures.sessions import FuturesSession
import pandas as pd
from tqdm import tqdm

PROTON_CSV = 'data/proton_db.csv'

def parse_future(future):
    response = future.result()

    if response.status_code == 404:
        return {
            'appid' : future.appid,
            'protondb_reports' : 0,
            'protondb_tier' : 'unknown',
        }
    else:
        data = response.json()
        return {
            'appid' : future.appid,
            'protondb_reports' : data['total'],
            'protondb_tier' : data['tier'],
        }

def get_missing_appids(appids):
    try:
        already_done_df = pd.read_csv(PROTON_CSV)
        already_done = set(list(already_done_df['appid']))
        return list(set(appids) - already_done)
    except FileNotFoundError:
        return appids

def main():
    games = pd.read_csv('data/steam.csv')
    appids = list(games['appid'])

    session = FuturesSession(max_workers=10)
    
    futures = []
    for appid in get_missing_appids(appids):
        future = session.get(f'https://www.protondb.com/api/v1/reports/summaries/{appid}.json')
        future.appid = appid
        futures.append(future)

    try:
        already_done_df = pd.read_csv(PROTON_CSV)
        res = already_done_df.to_dict('records') # Lets continue from where we left off
    except FileNotFoundError:
        res = []

    for i, future in enumerate(tqdm(futures)):
        res.append(parse_future(future))

        if i % 1000 == 0:
            pd.DataFrame(res).to_csv(PROTON_CSV, index=False)

    pd.DataFrame(res).to_csv(PROTON_CSV, index=False)

if __name__ == '__main__':
    main()