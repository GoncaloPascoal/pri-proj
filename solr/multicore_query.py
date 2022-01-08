
import requests, json
from colorama import Style, Fore
from pprint import pprint

GAMES = 'games'
REVIEWS = 'reviews'

def print_result(result, result_type):
    if result_type == GAME_RESULT:
        print_game(result)
    elif result_type == REVIEW_RESULT:
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
    print(f'Select an integer in the interval: [{min_int}-{max_int}]')
    while True:
        try:
            index = int(input(' -> '))
            if min_int <= index <= max_int:
                return index
            print(Fore.RED + 'Out of range' + Fore.RESET)
        except ValueError:
            print(Fore.RED + 'Not an integer' + Fore.RESET)

def query(q, core):
    '''
    Returns (n_found, documents), where documents are the solr_documents
    '''
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
    '''
    Returns (n_found, document_tuples) where document_tuples is a list of tuples: (solr_document, origin_core)
    '''
    game_results   = query(q, 'games'  )
    review_results = query(q, 'reviews')
    # TODO
    return (0, [])# TODO

def single_query():
    qf_games = 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
                about_the_game^1.5 short_description detailed_description^0.8'
    boost_games = 'mul(weighted_score, sqrt(log(total_ratings)))'

    qf_reviews = 'review^4 steamspy_tags^2 developer name'
    boost_reviews = 'vote_score'

    query_list = [
        # (Query, Core)
        ( {
            'query': {
                'edismax': {
                    'query': 'story-rich rpg "turn based combat" price:[* TO 20}',
                    'q.op': 'AND',
                    'qf': 'name^10 genres^3 steamspy_tags^2 detailed_description',
                    'boost': 'weighted_score',
                }
            }
        }, GAMES ), # Listing 1
        ( {
            'query': {
                'edismax': {
                    'query': 'fighting weighted_score:{0.6 to *]',
                    'q.op': 'AND',
                    'boost': 'weighted_score', # TODO: check if the query had boost or not
                }
            }
        }, GAMES ), # Table 1
        ( {
            'query': {
                'edismax': {
                    'query': 'fighting weighted_score:{0.6 to *]',
                    'q.op': 'AND',
                    'qf': 'steamspy_tags^2 short_description^1.5 detailed_description',
                    'boost': 'weighted_score', # TODO: check if the query had boost or not
                }
            }
        }, GAMES ), # Table 2
        ( {
           'query': {
                'edismax': {
                    'query': 'steamspy_tags:Difficult',
                    'boost': 'review_score',
                }
            } 
        }, GAMES ), # Table 3
        ( {
           'query': {
                'edismax': {
                    'query': 'steamspy_tags:Difficult',
                    'boost': 'mul(review_score, log(total_ratings))',
                }
            } 
        }, GAMES ), # Table 4
        ( {
           'query': {
                'edismax': {
                    'query': 'steamspy_tags:Difficult',
                    'boost': 'weighted_score',
                }
            } 
        }, GAMES ), # Table 5
        ( {
            'query': {
                'edismax': {
                    'query': 'gta',
                    'q.op': 'AND',
                    'qf': 'name^10 genres^3 steamspy_tags^2 detailed_description',
                    'boost': 'weighted_score',
                }
            }
        }, GAMES ), # Listing 6 and 7 # TODO: check

        ( {
            'query': {
                'edismax': {
                    'query': 'story sci-fi rpg combat price:[* TO 25]',
                    'q.op': 'AND',
                    'qf': qf_games,
                    'boost': boost_games,
                }
            }
        }, GAMES ), # Evaluation 1
        ( {
            'query': {
                'edismax': {
                    'query': 'historical command army',
                    'q.op': 'AND',
                    'qf': qf_games,
                    'boost': boost_games,
                }
            }
        }, GAMES ), # Evalutation 2
        ( {
            'query': {
                'edismax': {
                    'query': 'immersion "good graphics" votes_up:[3 TO *]',
                    'q.op': 'AND',
                    'qf': qf_reviews,
                    'boost': boost_reviews,
                }
            }
        }, REVIEWS ), # Evaluation 3
        ( {
            'query': {
                'edismax': {
                    'query': 'survival zombies votes_funny:[5 TO *]',
                    'q.op': 'AND',
                    'qf': qf_reviews,
                    'boost': boost_reviews,
                }
            }
        }, REVIEWS ), # Evaluation 4
        ( {
            'query': {
                'edismax': {
                    'query': 'strategy army steamspy_tags:Medieval',
                    'q.op': 'AND',
                    'qf': qf_games,
                    'boost': boost_games,
                    'rows': 20,
                }
            }
        }, GAMES ), # Evaluation 5
        ( {
            'query': {
                'edismax': {
                    'query': 'fantasy genres:RPG weighted_score:[0.92 TO *]',
                    'q.op': 'AND',
                    'qf': qf_games,
                    'boost': boost_games,
                }
            }
        }, GAMES ), # Evaluation 6
    ]

    q = select_int(0, len(query_list) - 1)
    (solr_query, solr_core) = query_list[q]
    (n_found, documents) = query(solr_query, solr_core)
    
    print(f'Found {n_found} documents.\n')
    for doc in documents:
        print_result(doc, solr_core)

def double_query():
    query_list = [
        {
            'query': {
                'edismax': {
                    'query': 'msgs',
                    'q.op': 'AND',
                    'qf': '', # TODO
                    'boost': '', # TODO
                    'fl': '*, score',
                }
            }
        }, # Multicore Query 1: msgs
    ]

    q = select_int(0, len(query_list) - 1)
    (n_found, documents) = multicore_query(query_list[q])
    
    print(f'Found {n_found} documents.\n')
    for doc, doc_type in documents:
        print_result(doc, doc_type)

def main():
    print('[1] Single Core Query')
    print('[2] Multi Core Query')
    menu = select_int(1, 2)
    if menu == 1:
        single_query()
    elif menu == 2:
        double_query()

if __name__ == '__main__':
    main()
