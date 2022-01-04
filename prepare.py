
from math import log10
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json, colorama, os.path
from colorama import Fore, Style
from reviews import convert_types

STEAM_JSON = 'data/steam.json'
REVIEWS_JSON = 'data/reviews.json'
HLTB_JSON = 'data/hltb.json'
PROTON_DB_JSON = 'data/proton_db.json'

def convert_to_list(df, col):
    df[col] = df[col].apply(lambda x: x.split(';'))

def extract_text_from_html(df, col):
    df[col] = df[col].apply(lambda x: BeautifulSoup(x, features='lxml').get_text())

def remove_trademark_symbols(df, col):
    df[col] = df[col].replace(to_replace='[\u2122\u00AE]', value='', regex=True)

def process_steam_data(df):
    remove_trademark_symbols(df, 'name')
    df['english'] = df['english'].astype(bool)
    df['release_date'] = pd.to_datetime(df['release_date']).apply(lambda x: x.isoformat())
    df['owners'] = df['owners'].astype('category')

    for col in ['developer', 'publisher', 'platforms', 'categories', 'genres', 'steamspy_tags']:
        convert_to_list(df, col)

    return df

def process_steam_description_data(df):
    df = df.rename(columns={'steam_appid': 'appid'})

    print('- Extracting text from HTML descriptions...')
    for col in ['detailed_description', 'about_the_game', 'short_description']:
        extract_text_from_html(df, col)
        remove_trademark_symbols(df, col)

    return df

def convert_dataframe_to_dict(df, unique_appid=True):
    dct = {}

    for i in range(len(df.index)):
        appid = int(df.loc[i, 'appid'])
        rest = {}

        for col in df.columns:
            rest[col] = df.loc[i, col]

            if pd.isnull(rest[col]):
                rest[col] = None
            
            if type(rest[col]) == np.int64:
                rest[col] = int(rest[col])
            
            if type(rest[col]) == np.float64:
                rest[col] = float(rest[col])
            
            if type(rest[col]) == np.bool_:
                rest[col] = bool(rest[col])
        
        del rest['appid']

        if unique_appid:
            dct[appid] = rest
        else:
            if appid in dct:
                dct[appid].append(rest)
            else:
                dct[appid] = [rest]

    return dct

def dict_to_json_file(dct, path):
    with open(path, 'w') as json_file:
        json.dump(dct, json_file, ensure_ascii=False)

def calc_weighted_score(row):
    return row['review_score'] - (row['review_score'] - 0.5) * \
        pow(2, -log10(row['total_ratings'] + 1))


def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Data Cleaning and Processing Script ---\n')

    print(Fore.CYAN + Style.BRIGHT + '- Reading main Steam data CSV file...')
    df = pd.read_csv('data/steam_updated.csv')

    print(Fore.CYAN + '- Performing data type conversion...')
    df = process_steam_data(df)
    
    print('- Reading description data CSV file...')
    desc = pd.read_csv('data/steam_description_data.csv')
    desc = process_steam_description_data(desc)

    print("- Merging game data and description...")
    data = pd.merge(left=df, right=desc, on='appid')

    print(Fore.CYAN + '- Reading HLTB CSV...')
    hltb_df = pd.read_csv('data/hltb.csv')

    convert_types(hltb_df, {
        'appid': int,
        'main_time': 'Int64',
        'extras_time': 'Int64',
        'completionist_time': 'Int64',
        'main_reports': 'Int64',
        'extras_reports': 'Int64',
        'completionist_reports': 'Int64',
    })

    data = pd.merge(left=data, right=hltb_df, on='appid')

    print(Fore.CYAN + '- Reading ProtonDB CSV...')
    proton_db_df = pd.read_csv('data/proton_db.csv')

    convert_types(proton_db_df, {
        'appid': int,
        'protondb_reports': 'Int64',
    })

    data = pd.merge(left=data, right=proton_db_df, on='appid')

    data['total_ratings'] = data['positive_ratings'] + data['negative_ratings']
    data['review_score'] = data['positive_ratings'] / data['total_ratings']
    data['weighted_score'] = data.apply(calc_weighted_score, axis=1) 

    convert_types(data, {
        'appid': int,
        'required_age': int,
        'achievements': int,
        'positive_ratings': int,
        'negative_ratings': int,
        'total_ratings': int,
        'review_score': float,
        'weighted_score': float,
        'average_playtime': int,
        'median_playtime': int,
        'price': float,
    })

    if os.path.exists(STEAM_JSON):
        print(Fore.YELLOW + '- Found existing processed Steam data file, skipping this step...')
    else:
        print('- Writing processed processed Steam data and descriptions to JSON file...')
        data.to_json(STEAM_JSON, orient='records')

    if os.path.exists(REVIEWS_JSON):
        print(Fore.YELLOW + '- Found existing processed reviews file, skipping this step...')
    else:
        print(Fore.CYAN + '- Reading reviews CSV...')
        reviews_df = pd.read_csv('data/reviews.csv')

        convert_types(reviews_df, {
            'appid': int,
            'author_steamid': int,
            'playtime_at_review': int,
            'created': int,
            'updated': int,
            'votes_up': int,
            'votes_funny': int,
            'vote_score': float,
        })

        for col in ['created', 'updated']:
            reviews_df[col] = pd.to_datetime(reviews_df[col], unit='s').apply(lambda x: x.isoformat())

        merge_cols = [
            'appid', 'name', 'developer', 'steamspy_tags', 'median_playtime',
        ]

        reviews_df = pd.merge(left=reviews_df, right=data[merge_cols], on='appid')

        print('- Writing processed review data to JSON file...')
        reviews_df.to_json(REVIEWS_JSON, orient='records')

    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Flattening Data into a Single Index ---\n')
    
    print(Fore.CYAN + '- Reading Games File...')
    games_file = open('data/steam.json')
    games = json.load(games_file)
    games_file.close()
    
    print(Fore.CYAN + '- Reading Reviews File...')
    reviews_file = open('data/reviews.json')
    reviews = json.load(reviews_file)
    reviews_file.close()

    print(Fore.CYAN + '- Adding the type...')
    for game in games:
        game['type'] = 'game'
    for review in reviews:
        review['type'] = 'review'
    
    print(Fore.CYAN + '- Writing Games and Reviews File...')
    file = open('data/games_and_reviews.json', 'w')
    json.dump(games + reviews, file, separators=(',', ':'))
    file.close()

    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
