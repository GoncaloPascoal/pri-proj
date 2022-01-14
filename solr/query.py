
import requests, json
from os.path import exists as file_exists
from argparse import ArgumentParser
from rich import print
from rich.pretty import pprint
from math import log10

GAMES = 'games'
REVIEWS = 'reviews'

def print_result(result, result_type):
    if result_type == GAMES:
        print_game(result)
    elif result_type == REVIEWS:
        print_review(result)

def print_game_name(game):
    score = ''
    if 'score' in game:
        score = str(round(game['score'], 2)) + ' '

    name = game['name']
    appid = game['appid']

    print(f'[b]{score}[blue]{name}[/blue] [magenta]({appid})[/magenta][/b]')

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
    score = ''
    if 'score' in review:
        score = str(round(review['score'], 2)) + ' '

    name = review["name"]
    appid = review["appid"]

    print(f'[b]{score}[blue]{name}[/blue] [magenta]({appid})[/magenta][/b]', end=' ')

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

def query(q, core, mlt=False):
    '''
    Returns (n_found, documents), where documents are the solr_documents
    '''
    if mlt:
        url = f'http://localhost:8983/solr/{core}/mlt'
        response_str = requests.get(url, params={
            'q.op': 'OR',
            'q': ' '.join(q),
        })
    else:
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
        GAMES: 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 '
                'about_the_game^1.5 short_description detailed_description^0.8 '
                'wp_gameplay^1 wp_introduction^1.5 wp_synopsis^2',
        REVIEWS: 'review^4 steamspy_tags^2 developer name'
    }

    default_boost = {
        GAMES: 'mul(weighted_score, sqrt(log(total_ratings)))',
        REVIEWS: 'vote_score'
    }
    
    edismax = request['query']['edismax']
    if 'qf' in edismax and not edismax['qf']:
        edismax['qf'] = default_qf[core]

    if 'boost' in edismax and not edismax['boost']:
        edismax['boost'] = default_boost[core]

def single_core_query(obj):
    core = obj['core']
    q    = obj['request']
    q_str = q['query']['edismax']['query']
    print(f'[b yellow]{q_str}[/b yellow]')

    fill(q, core)
    
    (n_found, results) = query(q, core)
    return (n_found, [(result, core) for result in results])

def multi_core_query(obj):
    q = obj['q']
    print(f'[b yellow]{q}[/b yellow]')
    q_games   = obj['request_games'  ]
    q_reviews = obj['request_reviews']
    q_games  ['query']['edismax']['query'] = q
    q_reviews['query']['edismax']['query'] = q
    q_games  ['params'] = {'fl': '*, score'}
    q_reviews['params'] = {'fl': '*, score'}
    
    fill(q_games  , GAMES  )
    fill(q_reviews, REVIEWS)

    (n_found_games  ,  games_results) = query(q_games  , GAMES  )
    (n_found_reviews, review_results) = query(q_reviews, REVIEWS)
    
    n_found = n_found_games + n_found_reviews

    get_score = lambda x: x['score']
    scores_games = map(get_score, games_results)
    scores_reviews = map(get_score, review_results)

    min_games, max_games = min(scores_games), max(scores_games)
    min_reviews, max_reviews = min(scores_reviews), max(scores_reviews)

    def normalize_document_scores(results, s_min, s_max):
        return list(map(lambda x: (x['score'] - s_min) / (s_max - s_min), results))

    def lms(l, l_total):
        return log10(1 + l * 600 / l_total)

    def weighted_document_score(d, c):
        return (d + 0.4 * d * c) / 1.4

    lms_games = lms(n_found_games, n_found)
    lms_reviews = lms(n_found_reviews, n_found)

    games_results = normalize_document_scores(games_results, min_games, max_games)
    review_results = normalize_document_scores(review_results, min_reviews, max_reviews)

    print(n_found_games, n_found_reviews)
    print(lms_games, lms_reviews)

    for result in games_results:
        result['score'] = weighted_document_score(result['score'], lms_games)

    for result in review_results:
        result['score'] = weighted_document_score(result['score'], lms_reviews)

    result_tuples = []
    result_tuples += map(lambda x: (x, GAMES), games_results)
    result_tuples += map(lambda x: (x, REVIEWS), review_results)

    result_tuples = sorted(result_tuples, key=lambda x: -x[0]['score'])

    return (n_found, result_tuples)

def main():
    parser = ArgumentParser()
    parser.add_argument('query_file', help='name of the query\'s file, without the extension (on the solr/queries folder)')
    args = parser.parse_args()

    file_name = f'solr/queries/{args.query_file}.json'
    if not file_exists(file_name):
        print('[b red]Invalid File[/b red]')
        return 0

    print()
    file = open(file_name)
    query_json = json.load(file)
    file.close()

    multicore = query_json['core'] == None

    if multicore:
        (n_found, results) = multi_core_query(query_json)
    else:
        (n_found, results) = single_core_query(query_json)

    print(f'[b green]Found {n_found} documents.[/b green]\n')
    for result, result_type in results:
        print_result(result, result_type)

    if multicore:
        return

    print('[b]Enter result indices to perform [blue]MoreLikeThis[/blue] query[/b]')
    while True:
        indices = input('> ').split()

        try:
            indices = list(map(int, indices))
            invalid = list(filter(lambda x: x < 0 or x >= len(results), indices))

            if invalid:
                print(f'[b red]Invalid indices:[/b red] {invalid}')
            else:
                break
        except ValueError:
            print('[b red]Indices must be integers![/b red]')

    if indices:
        appids = []
        for idx in indices:
            appids.append('appid:' + str(results[idx][0]['appid']))

        (n_found, results) = query(appids, query_json['core'], True)
        print(f'[b green]Found {n_found} documents.[/b green]\n')
        for result in results:
            print_result(result, query_json['core'])


if __name__ == '__main__':
    main()
