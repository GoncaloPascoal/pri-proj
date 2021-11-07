
from bs4 import BeautifulSoup
import pandas as pd
import colorama
import os.path
from colorama import Fore, Style

STEAM_JSON = 'data/steam_processed.json'
DESCRIPTIONS_JSON = 'data/descriptions_processed.json'

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

    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
