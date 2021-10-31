
from bs4 import BeautifulSoup
import pandas as pd
import colorama
from colorama import Fore, Style

def convert_to_list(df, col):
    df[col] = df[col].apply(lambda x: x.split(';'))

def minutes_to_hours(df, col):
    df[col] = df[col].apply(lambda x: x / 60.0)

def extract_text_from_html(df, col):
    df[col] = df[col].apply(lambda x: BeautifulSoup(x, features='lxml').get_text())

def process_steam_description_data():
    desc = pd.read_csv('data/steam_description_data.csv')
    desc = desc.rename(columns={'steam_appid': 'appid'})

    print('Extracting text from HTML descriptions...')
    for col in ['detailed_description', 'about_the_game', 'short_description']:
        extract_text_from_html(desc, col)

    return desc

def main():
    colorama.init()

    print(Fore.CYAN + Style.BRIGHT + 'Reading main Steam data CSV file...')
    df = pd.read_csv('data/steam.csv')

    print('Reading description data CSV file...')
    desc = process_steam_description_data()

    print('Merging main data & description data...')
    df = df.merge(desc, on='appid')

    print('Performing data type conversion...')
    df['english'] = df['english'].astype(bool)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['owners'] = df['owners'].astype('category')

    for col in ['developer', 'publisher', 'platforms', 'categories', 'genres', 'steamspy_tags']:
        convert_to_list(df, col)

    for col in ['average_playtime', 'median_playtime']:
        minutes_to_hours(df, col)
    
    print('Writing processed data to a new CSV file...')
    df.to_csv('data/steam_processed.csv', index=False)

    print(Fore.GREEN + 'Done.' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
