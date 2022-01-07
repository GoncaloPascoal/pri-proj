
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
            print(Fore.CYAN + '- Writing raw data to JSON file...')
        
        df.to_json('data/wikipedia_raw.json', orient='records')

def main():
    colorama.init()
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- Wikipedia Script ---\n')

    print(Fore.CYAN + '- Reading Steam data CSV file...')
    df = pd.read_csv('data/steam_updated.csv')
    wp = pd.DataFrame()

    existing_appids = set()

    try:
        f = open('data/wikipedia_raw.json', 'r')
        existing_data = pd.read_json(f, orient='records')

        print(Fore.YELLOW + '- Found existing file, skipping API calls for existing games...')
        wp = wp.append(existing_data)
        existing_appids = set(existing_data['appid'])
    except FileNotFoundError:
        pass

    print(Fore.CYAN + '- Obtaining plot synopses and gameplay descriptions ' +
        'from Wikipedia API...\n' + Fore.RESET)

    url = 'https://en.wikipedia.org/w/api.php'
    df['release_year'] = df['release_date'].apply(lambda x: x[:4])

    for index, row in tqdm(list(df.iterrows())):
        appid = row['appid']
        name = row['name']
        year = row['release_year']

        if appid in existing_appids:
            continue

        # Attempt to query these two titles, if both fail query title with just the game name
        opt = [f'{name} ({year} video game)', f'{name} (video game)']
        opt_str = '|'.join(opt)

        extract = None
        params = {
            'action': 'query',
            'prop': 'extracts',
            'exsectionformat': 'wiki',
            'explaintext': 'true',
            'titles': opt_str,
            'format': 'json',
            'formatversion': '2',
        }

        def perform_request():
            nonlocal url, params, extract
            backoff = 0.5

            while True:
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    jsr = json.loads(response.text)

                    if 'errors' in jsr:
                        rate_limited = False
                        for error in jsr['errors']:
                            if error['code'] == 'ratelimited':
                                rate_limited = True
                                break
                        
                        if rate_limited:
                            tqdm.write(Fore.RED + f'Rate limited! Sleeping for {backoff}s'
                                + Fore.RESET)
                            sleep(backoff)
                            backoff *= 2
                        else:
                            # Another kind of error in the response, abort
                            return
                    else:
                        # No errors in response
                        break
                else:
                    tqdm.write(Fore.RED + f'Error: {response.status_code}' + Fore.RESET)
                    return
            
            if 'pages' not in jsr['query']:
                tqdm.write(Fore.RED + f'\nError: request did not return page list')
                tqdm.write('Titles were: ' + Fore.BLUE + str(params['titles'].split('|')) + Fore.RESET)
                return

            pages = jsr['query']['pages']
            for page in pages:
                if 'extract' in page:
                    extract = page['extract']
                    break
        
        perform_request()
        if extract == None:
            params['titles'] = name
            perform_request()

        wp = wp.append({
            'appid': appid,
            'wp_article': extract,
        }, ignore_index=True)

        # Sleep for 250ms between each request to avoid rate limiting
        sleep(0.25)

        if index % 50 == 0:
            write_data(wp, messages=False)

    print()
    write_data(wp)
    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)


if __name__ == '__main__':
    main()
