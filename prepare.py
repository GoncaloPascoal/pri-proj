
from bs4 import BeautifulSoup
import pandas as pd
import json, colorama, os.path
from colorama import Fore, Style

STEAM_JSON = 'data/steam_processed.json'
DESCRIPTIONS_JSON = 'data/descriptions_processed.json'
REVIEWS_JSON = 'data/reviews.json'
HLTB_JSON = 'data/hltb.json'
PROTON_DB_JSON = 'data/proton_db.json'

def convert_to_list(df, col):
    df[col] = df[col].apply(lambda x: x.split(';'))

def minutes_to_hours(df, col):
    df[col] = df[col].apply(lambda x: x / 60.0)

def extract_text_from_html(df, col):
    df[col] = df[col].apply(lambda x: BeautifulSoup(x, features='lxml').get_text())

def process_steam_description_data():
    desc = pd.read_csv('data/steam_description_data.csv')
    desc = desc.rename(columns={'steam_appid': 'appid'})

    print('- Extracting text from HTML descriptions...')
    for col in ['detailed_description', 'about_the_game', 'short_description']:
        extract_text_from_html(desc, col)

    return desc

def convert_dataframe_to_dict(df, unique_appid=True):
    dct = {}

    for _, row in df.iterrows():
        appid = row['appid']
        rest = row.to_dict()
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

def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Data Cleaning and Processing Script ---\n')

    print(Fore.CYAN + Style.BRIGHT + '- Reading main Steam data CSV file...')
    df = pd.read_csv('data/steam.csv')

    if os.path.exists(DESCRIPTIONS_JSON):
        print(Fore.YELLOW + '- Found existing processed descriptions file, skipping this step...')
    else:
        print('- Reading description data CSV file...')
        desc = process_steam_description_data()

        print('- Writing processed descriptions to JSON file...')
        desc.to_json(DESCRIPTIONS_JSON, orient='records')

    if os.path.exists(STEAM_JSON):
        print(Fore.YELLOW + '- Found existing processed Steam data file, skipping this step...')
    else:
        print(Fore.CYAN + '- Performing data type conversion...')
        df['english'] = df['english'].astype(bool)
        df['release_date'] = pd.to_datetime(df['release_date'])
        df['owners'] = df['owners'].astype('category')

        for col in ['developer', 'publisher', 'platforms', 'categories', 'genres', 'steamspy_tags']:
            convert_to_list(df, col)

        for col in ['average_playtime', 'median_playtime']:
            minutes_to_hours(df, col)
        
        print('- Writing processed Steam data to JSON file...')
        df.to_json(STEAM_JSON, orient='records')

    if os.path.exists(REVIEWS_JSON):
        print(Fore.YELLOW + '- Found existing processed reviews file, skipping this step...')
    else:
        print(Fore.CYAN + '- Reading reviews CSV...')
        reviews_df = pd.read_csv('data/reviews.csv')

        print('- Grouping reviews by appid...')
        reviews_dict = convert_dataframe_to_dict(reviews_df, unique_appid=False)

        print('- Writing processed review data to JSON file...')
        dict_to_json_file(reviews_dict, REVIEWS_JSON)

    if os.path.exists(HLTB_JSON):
        print(Fore.YELLOW + '- Found existing processed HLTB file, skipping this step...')
    else:
        print(Fore.CYAN + '- Reading HLTB CSV...')
        hltb_df = pd.read_csv('data/reviews.csv')

        print('- Reshaping data for JSON format...')
        hltb_dict = convert_dataframe_to_dict(hltb_df)

        print('- Writing processed HLTB data to JSON file...')
        dict_to_json_file(hltb_dict, HLTB_JSON)
    
    if os.path.exists(PROTON_DB_JSON):
        print(Fore.YELLOW + '- Found existing processed ProtonDB file, skipping this step...')
    else:
        print(Fore.CYAN + '- Reading ProtonDB CSV...')
        proton_db_df = pd.read_csv('data/reviews.csv')

        print('- Reshaping data for JSON format...')
        proton_db_dict = convert_dataframe_to_dict(proton_db_df)

        print('- Writing processed ProtonDB data to JSON file...')
        dict_to_json_file(proton_db_dict, PROTON_DB_JSON)

    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
