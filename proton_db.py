from requests_futures.sessions import FuturesSession
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style

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
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- ProtonDB Reports Script ---\n')
    
    print(Fore.CYAN + '- Reading app ids from steam.csv file...')
    games = pd.read_csv('data/steam.csv')
    appids = list(games['appid'])

    session = FuturesSession(max_workers=10)
    
    try:
        already_done_df = pd.read_csv(PROTON_CSV)
        print(Fore.YELLOW + '- Found existing proton db file, skipping calls for existing games...')
        res = already_done_df.to_dict('records') # Lets continue from where we left off
    except FileNotFoundError:
        res = []
    
    futures = []
    games = games.set_index('appid')
    for appid in get_missing_appids(appids):
        if 'linux' in set(games.loc[appid, 'platforms'].split(';')):
            res.append({
                'appid': appid,
                'protondb_reports': 0,
                'protondb_tier': 'native',
            })
            continue

        future = session.get(f'https://www.protondb.com/api/v1/reports/summaries/{appid}.json')
        future.appid = appid
        futures.append(future)

    print(Fore.CYAN + '- Fetching proton reports and tier using the Proton DB API...\n' + Fore.RESET)
    for i, future in enumerate(tqdm(futures)):
        res.append(parse_future(future))

        if i % 1000 == 0:
            pd.DataFrame(res).to_csv(PROTON_CSV, index=False)

    print(Fore.CYAN + '\n- Writing proton reports data to CSV...')
    pd.DataFrame(res).to_csv(PROTON_CSV, index=False)
    print(Fore.GREEN + '\nDone.' + Fore.RESET)

if __name__ == '__main__':
    main()