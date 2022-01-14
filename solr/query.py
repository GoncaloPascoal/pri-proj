
import requests, json
from rich import print
from rich.pretty import pprint

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

default_qf = {
    'games': 'name^10 developer publisher categories^1.5 genres^3 steamspy_tags^2 \
    about_the_game^1.5 short_description detailed_description^0.8',
    'reviews': 'review^4 steamspy_tags^2 developer name'
}

default_boost = {
    'games': 'mul(weighted_score, sqrt(log(total_ratings)))',
    'reviews': 'vote_score'
}

print('[b]Enter the path to a JSON query file[/b]')
while True:
    try:
        path = input('> ')
        fp = open(path, 'r')
        obj = json.load(fp)
        break
    except FileNotFoundError:
        print('[b][red]File not found[/red][b]')
    except json.decoder.JSONDecodeError:
        print('[b][red]Error when parsing JSON[/red][b]')

core = obj['core']
query = obj['request']

if not query['query']['edismax']['qf']:
    query['query']['edismax']['qf'] = default_qf[core]

if not query['query']['edismax']['boost']:
    query['query']['edismax']['boost'] = default_boost[core]

url = f'http://localhost:8983/solr/{core}/query'

response_str = requests.post(url, data=json.dumps(query), headers={
    'Content-Type': 'application/json',
})

if response_str.status_code != 200:
    print(response_str.text)
    exit(1)

response = json.loads(response_str.text)
documents = response['response']['docs']

for doc in documents:
    if core == 'games':
        print_game(doc)
    else:
        print_review(doc)

print('Found', response['response']['numFound'], 'documents.\n')

print('[b]Enter result indices to perform [blue]MoreLikeThis[/blue] query[/b]')
while True:
    indices = input('> ').split()

    try:
        indices = list(map(int, indices))
        invalid = list(filter(lambda x: x < 0 or x >= len(documents), indices))

        if invalid:
            print(f'[b red]Invalid indices:[/b red] {invalid}')
        else:
            break
    except ValueError:
        print('[b red]Indices must be integers![/b red]')

if indices:
    # TODO: Perform MLT query
    appids = []
    for idx in indices:
        appids.append(documents[idx]['appid'])

    url = f'http://localhost:8983/solr/{core}/mlt'
    
    response_str = requests.get()
