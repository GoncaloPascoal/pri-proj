
import requests, json
from colorama import Style, Fore
from pprint import pprint

def print_game(game):
    print(Style.BRIGHT + Fore.CYAN + game['name'] + Style.RESET_ALL)
    print('- Released:', Fore.YELLOW + game['release_date'][:10] + Fore.RESET)
    print('- Genres:', game['genres'])
    print('- Tags:', game['steamspy_tags'])
    print('- Price: {}'.format(Fore.GREEN + '$' + str(game['price']) + Fore.RESET))
    print()

qf = 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
    about_the_game^1.5 short_description detailed_description^0.8'
boost = 'mul(weighted_score, sqrt(log(total_ratings)))'

queries = [
    {
        'query': {
            'edismax': {
                'query': 'story rich rpg turn based combat price:[* TO 20}',
                'q.op': 'AND',
                'qf': qf,
                'boost': boost,
            }
        }
    },
    {
        'query': {
            'edismax': {
                'query': 'strategy army steamspy_tags:Medieval',
                'q.op': 'AND',
                'qf': qf,
                'boost': boost,
                'rows': 20,
            }
        }
    },
]

url = 'http://localhost:8983/solr/games/query'

response_str = requests.post(url, data=json.dumps(queries[1]), headers={
    'Content-Type': 'application/json',
})

if response_str.status_code != 200:
    print(response_str.text)
    exit(1)

response = json.loads(response_str.text)
games = response['response']['docs']

print('Found', response['response']['numFound'], 'games\n')

for game in games:
    print_game(game)