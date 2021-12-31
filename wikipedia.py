
import pandas as pd
import colorama, requests, json
from colorama import Fore, Style
from reviews import convert_types
from tqdm import tqdm
from time import sleep

def write_data(df, messages=True):
    if not df.empty:
        if messages:
            print(Fore.CYAN + '- Performing type conversion...')

        df = convert_types(df, {
            'appid': int,
        })

        if messages:
            print(Fore.CYAN + '- Writing updated data to new CSV file...')
        
        df.to_csv('data/wikipedia.csv', index=False)

def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Wikipedia Script ---\n')

    print(Fore.CYAN + '- Reading Steam data CSV file...')
    df = pd.read_csv('data/steam_updated.csv')
    wp = pd.DataFrame()

    existing_appids = set()

    try:
        existing_data = pd.read_csv('data/wikipedia.csv')

        print(Fore.YELLOW + '- Found existing file, skipping API calls for existing games...')
        wp = wp.append(existing_data)
        existing_appids = set(existing_data['appid'])
    except FileNotFoundError:
        pass

    print(Fore.CYAN + '- Obtaining plot synopses and gameplay descriptions ' +
        'from Wikipedia API...\n' + Fore.RESET)

    url = 'https://en.wikipedia.org/w/api.php'
    backoff = 0.5

    for index, row in tqdm(list(df.iterrows())):
        appid = row['appid']
        name = row['name']

        if appid in existing_appids:
            continue

        response = requests.get(url, params={
            'action': 'query',
            'prop': 'extracts',
            'exsectionformat': 'plain',
            'explaintext': 'true',
            'titles': name,
            'format': 'json',
            'formatversion': '2',
        })

        if response.status_code == 200:
            jsr = json.loads(response.text)

            if 'errors' in jsr:
                rate_limited = False
                for error in jsr['errors']:
                    if error['code'] == 'ratelimited':
                        rate_limited = True
                        break
                
                if rate_limited:
                    print(Fore.RED + f'Rate limited! Sleeping for {backoff}s'
                        + Fore.RESET)
                    sleep(backoff)
                    backoff *= 2
            else:
                # TODO: Parse JSON response
                json.dump(jsr, open('data/wiki_test.json', 'w'), indent=2)
        else:
            print(Fore.RED + response.text + Fore.RESET)

        exit(0) # FIXME: Remove
        
        if index % 50 == 0:
            write_data(wp, messages=False)

    write_data(wp)
    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)


if __name__ == '__main__':
    main()
