
import requests, json
from colorama import Style, Fore
from pprint import pprint

GAME_RESULT = 1
REVIEW_RESULT = 2

def print_result(result):
    if result['type'] == GAME_RESULT:
        print_game(result)
    elif result['type'] == REVIEW_RESULT:
        print_review(result)

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

def select_int(min_int, max_int):
    while True:
        try:
            index = int(input('> '))
            if min_int <= index <= max_int:
                return index
            print(Fore.RED + 'Out of range' + Fore.RESET)
        except ValueError:
            print(Fore.RED + 'Not an integer' + Fore.RESET)

def query(core, q):
    url = f'http://localhost:8983/solr/{core}/query'

    response_str = requests.post(url, data=json.dumps(q), headers={
        'Content-Type': 'application/json',
    })

    if response_str.status_code != 200:
        print(response_str.text)
        exit(1)

    response = json.loads(response_str.text)
    documents = response['response']['docs']
    n_found = response['response']['numFound']
    return (n_found, documents)

def multicore_query(q):
    game_results = query('games', q)
    review_results = query('reviews', q)
    # TODO
    return # TODO

def main():
    qf = 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
        about_the_game^1.5 short_description detailed_description^0.8'
    boost = 'mul(weighted_score, sqrt(log(total_ratings)))'

    qf_reviews = 'review^4 steamspy_tags^2 developer name'
    boost_reviews = 'vote_score'

    query_list = [
        # (Core, Query)
        ('games', {
            'query': {
                'edismax': {
                    'query': 'mgs',
                    'q.op': 'AND',
                    'qf': qf,
                    'boost': boost,
                }
            }
        },),
        ('games', {
            'query': {
                'edismax': {
                    'query': 'strategy army steamspy_tags:Medieval',
                    'q.op': 'AND',
                    'qf': qf,
                    'boost': boost,
                    'rows': 20,
                }
            }
        },),
        ('games', {
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
        },),
        ('reviews', {
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
        },),
        ('reviews', {
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
        },),
        ('games', {
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
        },),
        ('games', {
            # Precision @ 5: 80%
            # Precision @ 10: 60%
            'query': {
                'edismax': {
                    'query': 'forest platforms:linux',
                    'q.op': 'AND',
                    'qf': qf,
                    'boost': boost,
                }
            }
        },),
        ('reviews', {
            # Precision @ 5: 100%
            # Precision @ 10: 100%
            'query': {
                'edismax': {
                    'query': 'toxicity playtime_at_review:[3000 TO *]',
                    'q.op': 'AND',
                    'qf': qf_reviews,
                    'boost': boost_reviews,
                }
            }
        },),
    ]

    q = select_int(0, len(query_list) - 1)
    (n_found, documents) = query(query_list[q][0], query_list[q][1])
    
    
    print(f'Found {n_found} documents.\n')
    for doc in documents:
        print_result(doc)

if __name__ == '__main__':
    main()
