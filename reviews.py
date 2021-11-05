
import requests, json
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style

def convert_types(df, types):
    for key, data_type in types.items():
        df[key] = df[key].astype(data_type)
    
    return df

def write_data(df, messages=True):
    if not df.empty:
        if messages:
            print(Fore.CYAN + 'Performing type conversion...')

        df = convert_types(df, {
            'appid': int,
            'author_steamid': int,
            'playtime_at_review': int,
            'created': int,
            'updated': int,
            'votes_up': int,
            'votes_funny': int,
            'vote_score': float,
            'steam_purchase': bool,
            'received_for_free': bool,
        })

        if messages:
            print('Writing review data to CSV...')

        df.to_csv('data/reviews.csv', index=False)

def main():
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Steam Reviews Script ---\n')

    reviews_per_game = 5

    req_params = {
        'filter': 'all',    # Reviews sorted by helpfulness
        'language': 'en',   # Only English reviews
        'day_range': '365', # Only reviews from the last year
        'cursor': '*',
    }

    print(Fore.CYAN + 'Reading app ids from steam.csv file...')
    app_ids = pd.read_csv('data/steam.csv')[['appid']].copy()
    reviews_df = pd.DataFrame()

    existing_app_ids = set()

    try:
        existing_reviews = pd.read_csv('data/reviews.csv')

        print(Fore.YELLOW + 'Found existing reviews file, skipping API calls for existing games...')
        reviews_df = reviews_df.append(existing_reviews)
        existing_app_ids = set(existing_reviews['appid'])
    except FileNotFoundError:
        pass

    print(Fore.CYAN + 'Fetching reviews using the Steam Store API...\n' + Fore.RESET)
    for index, row in tqdm(list(app_ids.head(50).iterrows())):
        app_id = row['appid']

        if app_id in existing_app_ids:
            continue

        url = 'https://store.steampowered.com/appreviews/' + str(app_id) + '?json=1'
        response = requests.get(
            url = url,
            headers = req_params,
        )

        reviews_json = json.loads(response.text)
        reviews_slice = reviews_json['reviews'][:reviews_per_game]

        for review in reviews_slice:
            author = review['author']

            reviews_df = reviews_df.append({
                'appid': app_id,
                'author_steamid': author['steamid'],
                'playtime_at_review': author['playtime_at_review'] if 'playtime_at_review' in author else 0, 
                'review': review['review'].replace('\n', ' '),
                'created': review['timestamp_created'],
                'updated': review['timestamp_updated'],
                'votes_up': review['votes_up'],
                'votes_funny': review['votes_funny'],
                'vote_score': review['weighted_vote_score'],
                'steam_purchase': review['steam_purchase'],
                'received_for_free': review['received_for_free']
            }, ignore_index=True)
        
        if index % 1000 == 0:
            write_data(reviews_df, messages=False)

    print()
    write_data(reviews_df)
    print(Fore.GREEN + 'Done.\n')

if __name__ == '__main__':
    main()
