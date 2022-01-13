
import requests, json
from os.path import exists as file_exists
from argparse import ArgumentParser
from rich import print
from rich.pretty import pprint

GAMES = 'games'
REVIEWS = 'reviews'

def print_result(result, result_type):
    if result_type == GAMES:
        print_game(result)
    elif result_type == REVIEWS:
        print_review(result)

def print_game_name(game):
    name = game['name']
    appid = game['appid']

    print(f'[b][bright_cyan]{name}[/bright_cyan] [magenta]({appid})[/magenta][/b]')

def print_game(game):
    print_game_name(game)

    release_date = game['release_date'][:10]
    genres = game['genres']
    tags = game['steamspy_tags']
    price = game['price']

    print(f'- Released: [b][yellow]{release_date}[/yellow][/b]')
    print(f'- Genres: {genres}')
    print(f'- Tags: {tags}')
    print(f'- Price: [b][green]${price}[/green][/b]\n')

def print_review(review):
    name = review["name"]
    appid = review["appid"]

    print(f'[b][blue]{name}[/blue] [magenta]({appid})[/magenta][/b]', end=' ')

    if review['recommended']:
        print(':white_check_mark:', end=' ')
    else:
        print(':cross_mark:', end=' ')

    up = review['votes_up']
    funny = review['votes_funny']
    score = round(review['vote_score'], 3)

    print(f' | {up} :thumbsup: ({score}) | {funny} :joy:')

    hours_at_review = round(review['playtime_at_review'] / 60, 1)
    print(f'[bright_yellow]{hours_at_review} hours at review[/bright_yellow]')
    print(str(review['steamspy_tags']) + '\n')

    pprint(review['review'], max_string=500)
    print('\n' + '\u2500' * 80 + '\n')

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

def fill(request, core):
    default_qf = {
        GAMES: 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
        about_the_game^1.5 short_description detailed_description^0.8',
        REVIEWS: 'review^4 steamspy_tags^2 developer name'
    }

    default_boost = {
        GAMES: 'mul(weighted_score, sqrt(log(total_ratings)))',
        REVIEWS: 'vote_score'
    }

    if not request['query']['edismax']['qf']:
        request['query']['edismax']['qf'] = default_qf[core]

    if not request['query']['edismax']['boost']:
        request['query']['edismax']['boost'] = default_boost[core]

def single_core_query(obj):
    global default_qf, default_boost

    core = obj['core']
    q    = obj['request']

    fill(q, core)
    
    (n_found, results) = query(q, core)
    return (n_found, [(result, core) for result in results])

def multi_core_query(obj):
    global default_qf, default_boost

    q = obj['q']
    q_games   = obj['request_games'  ]
    q_reviews = obj['request_reviews']
    q_games  ['query']['edismax']['query'] = q
    q_reviews['query']['edismax']['query'] = q
    
    fill(q_games  , GAMES  )
    fill(q_reviews, REVIEWS)

    (n_found_games  ,  games_results) = query(q_games  , GAMES  )
    (n_found_reviews, review_results) = query(q_reviews, REVIEWS)
    
    n_found = n_found_games + n_found_reviews

    result_tuples = []
    # TODO: between
    for game_doc in games_results:
        result_tuples.append((game_doc, GAMES))
    for review_doc in review_results:
        result_tuples.append((review_doc, REVIEWS))
    # TODO: between

    return (n_found, result_tuples)

def main():
    parser = ArgumentParser()
    parser.add_argument('query_file', help='name of the query\'s file, without the extension (on the solr/queries folder)')
    args = parser.parse_args()

    file_name = f'solr/queries/{args.query_file}.json'
    if file_exists(file_name):
        file = open(file_name)
        query_json = json.load(file)
        file.close()

        # (n_found, results) = (0, [])
        if query_json['core'] == None:
            (n_found, results) = multi_core_query(query_json)
        else:
            (n_found, results) = single_core_query(query_json)

        print(f'[b][green]Found {n_found} documents.[/green][/b]\n')
        for result, result_type in results:
            print_result(result, result_type)

    else:
        print('[b][red]Invalid File[/red][/b]')

if __name__ == '__main__':
    main()
