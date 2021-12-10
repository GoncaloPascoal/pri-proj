
import requests, json
from colorama import Style, Fore
from pprint import pprint

def print_game(game):
    print(Style.BRIGHT + Fore.CYAN + game['name'] + Fore.LIGHTMAGENTA_EX + ' (' + 
        str(game['appid']) + ')' + Style.RESET_ALL)
    print('- Released:', Fore.YELLOW + game['release_date'][:10] + Fore.RESET)
    print('- Genres:', game['genres'])
    print('- Tags:', game['steamspy_tags'])
    print('- Price: {}'.format(Fore.GREEN + '$' + str(game['price']) + Fore.RESET))
    print()

def print_review(review):
    print(Style.BRIGHT + Fore.BLUE + review['name'], end=' ')

    if review['recommended']:
        print('\u2705', end='')
    else:
        print('\u274c', end='')

    up = review['votes_up']
    funny = review['votes_funny']
    score = round(review['vote_score'], 3)

    print(f'{Fore.RESET} | {up} \U0001F44D ({score}) | {funny} \U0001f602 ')

    hours_at_review = round(review['playtime_at_review'] / 60, 1)
    print(Fore.LIGHTYELLOW_EX + str(hours_at_review) + ' hours at review')
    print(Fore.RESET + str(review['steamspy_tags']) + Style.RESET_ALL + '\n')

    pprint(review['review'])
    print('\n' + '\u2500' * 80 + '\n')

qf = 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
    about_the_game^1.5 short_description detailed_description^0.8'
boost = 'mul(weighted_score, sqrt(log(total_ratings)))'

qf_reviews = 'review^4 steamspy_tags^2 developer name'
boost_reviews = 'vote_score'

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
    {
        # Precision @ 5: 100%
        # Precision @ 10: 80%
        'query': {
            'edismax': {
                'query': 'historical command army',
                'q.op': 'AND',
                'qf': qf,
                'boost': boost,
            }
        }
    },
    {
        # Precision @ 5: 80%
        # Precision @ 10: 80%
        # Interesting find: a lot of games mentioned were VR
        'query': {
            'edismax': {
                'query': 'immersion "good graphics" votes_up:[3 TO *]',
                'q.op': 'AND',
                'qf': qf_reviews,
                'boost': boost_reviews,
            }
        }
    },
    {
        # Precision @ 5: 80%
        # Precision @ 10: 80%
        'query': {
            'edismax': {
                'query': 'survival zombies votes_funny:[5 TO *]',
                'q.op': 'AND',
                'qf': qf_reviews,
                'boost': boost_reviews,
            }
        }
    },
    {
        # Precision @ 5: 80%
        # Precision @ 10: 70%
        'query': {
            'edismax': {
                'query': 'retro fps release_date:{2017-01-01T00:00:00Z TO *]',
                'q.op': 'AND',
                'qf': qf,
                'boost': boost,
            }
        }
    },
]

cores = ['games', 'reviews']

print(Style.BRIGHT + 'Pick a Core' + Style.RESET_ALL)
for i, core in enumerate(cores):
    print(f'[{i}] - {core}')
while True:
    try:
        idx = int(input('> '))
        core = cores[idx]
        break
    except ValueError:
        print(Fore.RED + 'Not an integer' + Fore.RESET)
    except IndexError:
        print(Fore.RED + 'Not in range' + Fore.RESET)

url = f'http://localhost:8983/solr/{core}/query'

response_str = requests.post(url, data=json.dumps(queries[-1]), headers={
    'Content-Type': 'application/json',
})

if response_str.status_code != 200:
    print(response_str.text)
    exit(1)

response = json.loads(response_str.text)
documents = response['response']['docs']

print('Found', response['response']['numFound'], 'documents.\n')

for doc in documents:
    if core == 'games':
        print_game(doc)
    else:
        print_review(doc)