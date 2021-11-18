
import pandas as pd
import asyncio
from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry
from reviews import convert_types
from colorama import Fore, Style

HLTB_CSV = 'data/hltb.csv'
SIMULTANEOUS_TASKS = 1400
CHECKPOINT = 2800

def get_minutes(time_unit):
    return 60 if time_unit == 'Hours' else 1 # 'Hours', 'Mins'

def get_time(time, time_unit, time_label):
    if time == -1 or time_unit == None or time_label == None:
        return None
    if type(time) is str:
        if '½' in time:
            time = int(time[:len(time) -1]) + 0.5
        else:
            time = int(time)
    return time * get_minutes(time_unit)

async def get_game_entry_from_hltb(hltb, name, appid):
    results = await hltb.async_search(name, similarity_case_sensitive=False)
    if results is None or len(results) == 0:
        return (HowLongToBeatEntry(), appid)
    else:
        return (results[0], appid)

def add_game(games, id, game_entry):
    return games.append({
        'appid': id,
        'main_time'         : get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         , game_entry.gameplay_main_label         ),
        'extras_time'        : get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   , game_entry.gameplay_main_extra_label   ),
        'completionist_time': get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit, game_entry.gameplay_completionist_label)
    }, ignore_index=True)

def get_game_entries():
    try:
        existing_times = pd.read_csv(HLTB_CSV)
        print(Fore.YELLOW + '- Found existing game times file, skipping API calls for existing games...')
        return existing_times
    except FileNotFoundError:
        return pd.DataFrame()

def get_missing_appids(games, game_entries):
    appids       = set(games['appid'])
    already_done = set()
    if 'appid' in game_entries.columns:
        already_done = set(game_entries['appid'])
    return appids - already_done

def get_gameplay_times(games, game_entries):
    hltb = HowLongToBeat(1.0)

    tasks = [get_game_entry_from_hltb(hltb, row['name'], row['appid']) for _, row in games.iterrows()]
    completed = asyncio.run(wait_for_tasks(tasks))
    for completed_task in completed:
        game_entry, appid = completed_task.result()
        game_entries = add_game(game_entries, appid, game_entry)
    return game_entries

def get_games_to_search(games, game_entries):
    missing_appids = get_missing_appids(games, game_entries)
    return games.loc[games['appid'].isin(missing_appids)]

async def wait_for_tasks(tasks):
    completed = set()
    while len(tasks) > 0:
        if len(tasks) > SIMULTANEOUS_TASKS:
            partial_tasks = tasks[:SIMULTANEOUS_TASKS]
            tasks = tasks[SIMULTANEOUS_TASKS:]
        else:
            partial_tasks = tasks
            tasks = []

        more_completed, pending = await asyncio.wait(partial_tasks)
        completed = completed.union(more_completed)

        while len(pending) > 0:
            more_completed, pending = await asyncio.wait(list(pending))
            completed = completed.union(more_completed)

    return completed 

def save_checkpoint(results):
    convert_types(results, {
        'appid': int,
        'main_time': 'Int64',
        'extras_time': 'Int64',
        'completionist_time': 'Int64',
    })
    results.to_csv(HLTB_CSV, index=False)

def get_checkpoints(games_to_search):
    checkpoints = []
    while len(games_to_search) > CHECKPOINT:
        checkpoints.append(games_to_search.iloc[:CHECKPOINT])
        games_to_search = games_to_search.iloc[CHECKPOINT:]
    checkpoints.append(games_to_search)
    return checkpoints

def main():
    print(Fore.MAGENTA + Style.BRIGHT + '\n--- HowLongToBeat Script ---\n')

    print(Fore.CYAN + '- Reading app ids from steam.csv file...')
    games = pd.read_csv('data/steam.csv')
    game_entries = get_game_entries()

    print(Fore.CYAN + '- Fetching game times using the howlongtobeatpy package...' + Fore.RESET)
    games = get_games_to_search(games, game_entries)
    for checkpoint in get_checkpoints(games):
        game_entries = get_gameplay_times(checkpoint, game_entries)
        save_checkpoint(game_entries)
    
    print(Fore.GREEN + '\nDone.\n' + Fore.RESET)

if __name__ == '__main__':
    main()