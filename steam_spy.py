
import requests, json
import pandas as pd
from colorama import Fore, Style

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

def main():
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- SteamSpy Script ---\n')

    print(Fore.CYAN + '- Reading main Steam data CSV file...')
    df = pd.read_csv('data/steam.csv')

    print('- Obtaining updated ratings and playtime data from SteamSpy API...')
    for index, row in df.head().iterrows(): # TODO: Replace this with sample
        app_id = row['appid']

        url = construct_request_url('appdetails', {
            'appid': str(app_id),
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

            for key, value in relevant.items():
                df.loc[index, key] = value
        else:
            print(Fore.RED + f'Request error: code {response.status_code}')
    
    print(Fore.CYAN + '- Writing updated data to new CSV file...')
    df.to_csv('data/steam_updated.csv', index=False)

    print(Fore.GREEN + '\nDone.\n' + Style.RESET_ALL)

if __name__ == '__main__':
    main()
