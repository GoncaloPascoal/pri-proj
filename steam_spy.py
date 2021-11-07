
import requests, json
import pandas as pd
from colorama import Fore, Style
from reviews import convert_types

def construct_request_url(request, params):
    url = 'https://steamspy.com/api.php'

    if params:
        param_strings = [f'request={request}']
        param_strings.extend([key + '=' + value for key, value in params.items()])
        url += '?' + '&'.join(param_strings)

    return url

def clean_data(data):
    data['owners'] = data['owners'].replace(',', '').replace(' .. ', '-')
    data['price'] = int(data['price']) / 100

    return data

def write_data(df, messages=True):
    if not df.empty:
        if messages:
            print(Fore.CYAN + '- Performing type conversion...')

        df = convert_types(df, {
            'appid': int,
            'positive_ratings': int,
            'negative_ratings': int,
            'average_playtime': int,
            'median_playtime': int,
            'price': float, 
        })

        if messages:
            print(Fore.CYAN + '- Writing updated data to new CSV file...')
        
        df.to_csv('data/steam_updated.csv', index=False)

def main():
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- SteamSpy Script ---\n')

    print(Fore.CYAN + '- Reading main Steam data CSV file...')
    df = pd.read_csv('data/steam.csv')
    updated_df = pd.DataFrame()

    existing_appids = set()

    try:
        existing_data = pd.read_csv('data/steam_updated.csv')

        print(Fore.YELLOW + '- Found existing file, skipping API calls for existing games...')
        updated_df = updated_df.append(existing_data)
        existing_appids = set(existing_data['appid'])
    except FileNotFoundError:
        pass

    print(Fore.CYAN + '- Obtaining updated ratings and playtime data from SteamSpy API...')
    for index, row in df.head(20).iterrows(): # TODO: Replace this with sample
        appid = row['appid']

        if appid in existing_appids:
            continue

        url = construct_request_url('appdetails', {
            'appid': str(appid),
        })

        response = requests.get(url)

        if response.status_code == 200:
            response_dict = json.loads(response.text)

            key_to_col = {
                'positive': 'positive_ratings',
                'negative': 'negative_ratings',
                'owners': 'owners',
                'average_forever': 'average_playtime',
                'median_forever': 'median_playtime',
                'price': 'price',
            }

            relevant = {
                key_to_col[key]: response_dict[key] for key in response_dict.keys()
                    & ['positive', 'negative', 'owners', 'average_forever',
                    'median_forever', 'price']
            }

            relevant = clean_data(relevant)

            updated_df = updated_df.append(df.loc[index])
            for key, value in relevant.items():
                updated_df.loc[index, key] = value
        else:
            print(Fore.RED + f'Request error: code {response.status_code}')
        
        if index % 1000 == 0:
            write_data(updated_df, messages=False)
    
    write_data(updated_df)
    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
