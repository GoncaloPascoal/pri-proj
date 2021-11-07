
import requests
import json
import pandas as pd

def convert_types(df, types):
    for key, data_type in types.items():
        df[key] = df[key].astype(data_type)
    
    return df

def main():
    reviews_per_game = 5

    req_params = {
        'filter': 'all',    # Reviews sorted by helpfulness
        'language': 'en',   # Only English reviews
        'day_range': '365', # Only reviews from the last year
        'cursor': '*',
    }

    app_ids = pd.read_csv('data/steam.csv')[['appid']].copy()
    reviews_df = pd.DataFrame()

    for index, row in app_ids.head().iterrows():
        app_id = row['appid']

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
                'playtime_at_review': author['playtime_at_review'], 
                'review': review['review'].replace('\n', ' '),
                'created': review['timestamp_created'],
                'updated': review['timestamp_updated'],
                'votes_up': review['votes_up'],
                'votes_funny': review['votes_funny'],
                'vote_score': review['weighted_vote_score'],
                'steam_purchase': review['steam_purchase'],
                'received_for_free': review['received_for_free']
            }, ignore_index=True)

    reviews_df = convert_types(reviews_df, {
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

    reviews_df.to_csv('data/reviews.csv', index=False)

if __name__ == '__main__':
    main()
