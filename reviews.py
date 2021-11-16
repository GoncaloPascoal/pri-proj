
import json
import pandas as pd
from requests_futures.sessions import FuturesSession
from tqdm import tqdm
import colorama
from colorama import Fore, Style

REVIEWS_PER_GAME = 15

def convert_types(df, types):
    for key, data_type in types.items():
        df[key] = df[key].astype(data_type)
    
    return df

def parse_future(future, reviews_df):
    response = future.result()

    reviews_json = json.loads(response.text)
    reviews_slice = reviews_json['reviews'][:REVIEWS_PER_GAME]

    for review in reviews_slice:
        author = review['author']

        reviews_df = reviews_df.append({
            'appid': future.appid,
            'author_steamid': author['steamid'],
            'playtime_at_review': author['playtime_at_review'] if 'playtime_at_review' in author else 0, 
            'review': review['review'].replace('\n', ' '),
            'created': review['timestamp_created'],
            'updated': review['timestamp_updated'],
            'recommended': review['voted_up'],
            'votes_up': review['votes_up'],
            'votes_funny': review['votes_funny'],
            'vote_score': review['weighted_vote_score'],
            'steam_purchase': review['steam_purchase'],
            'received_for_free': review['received_for_free']
        }, ignore_index=True)

    return reviews_df

def write_data(df, messages=True):
    if not df.empty:
        if messages:
            print(Fore.CYAN + '- Performing type conversion...')

        df = convert_types(df, {
            'appid': int,
            'author_steamid': int,
            'playtime_at_review': int,
            'created': int,
            'updated': int,
            'recommended': bool,
            'votes_up': int,
            'votes_funny': int,
            'vote_score': float,
            'steam_purchase': bool,
            'received_for_free': bool,
        })

        if messages:
            print('- Writing review data to CSV...')

        df.to_csv('data/reviews.csv', index=False)

def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Steam Reviews Script ---\n')

    session = FuturesSession(max_workers=10)
    futures = []

    req_params = {
        'filter': 'all',    # Reviews sorted by helpfulness
        'language': 'en',   # Only English reviews
        'day_range': '365', # Only reviews from the last year
        'cursor': '*',
    }

    print(Fore.CYAN + '- Reading app ids from steam.csv file...')
    app_ids = pd.read_csv('data/steam.csv')[['appid']].copy()
    reviews_df = pd.DataFrame()

    existing_appids = set()

    try:
        existing_reviews = pd.read_csv('data/reviews.csv')

        print(Fore.YELLOW + '- Found existing reviews file, skipping API calls for existing games...')
        reviews_df = reviews_df.append(existing_reviews)
        existing_appids = set(existing_reviews['appid'])
    except FileNotFoundError:
        pass

    print(Fore.CYAN + '- Fetching reviews using the Steam Store API...\n' + Fore.RESET)
    for _, row in app_ids.iterrows():
        appid = row['appid']

        if appid in existing_appids:
            continue

        url = 'https://store.steampowered.com/appreviews/' + str(appid) + '?json=1'
        future = session.get(url, headers=req_params)
        future.appid = appid
        futures.append(future)

    for i, future in enumerate(tqdm(futures)):
        reviews_df = parse_future(future, reviews_df)
        
        if i % 1000 == 0:
            write_data(reviews_df, messages=False)

    print()
    write_data(reviews_df)
    print(Fore.GREEN + '\nDone.' + Fore.RESET)

if __name__ == '__main__':
    main()
