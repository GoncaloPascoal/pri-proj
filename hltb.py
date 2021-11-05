
from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry

import pandas as pd
import asyncio

HLTB_CSV = 'data/hltb.csv'

def get_empty_game_entry():
    game_entry = HowLongToBeatEntry()
    game_entry.gameplay_main               = -1
    game_entry.gameplay_main_unit          = None
    game_entry.gameplay_main_extra         = -1
    game_entry.gameplay_main_extra_unit    = None
    game_entry.gameplay_completionist      = -1
    game_entry.gameplay_completionist_unit = None
    return game_entry

def get_minutes(time_unit):
    return 60 if time_unit == 'Hours' else 1 # 'Hours', 'Mins'

def get_time(time, time_unit):
    if time == -1 or time_unit == None:
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
        return (get_empty_game_entry(), appid)
    else:
        return (results[0], appid)

def add_game(games, id, game_entry):
    return games.append({
        'appid': id,
        'main_time'         : get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         ),
        'extra_time'        : get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   ),
        'completionist_time': get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit)
    }, ignore_index=True)

def get_game_entries():
    try:
        return pd.read_csv(HLTB_CSV)
    except FileNotFoundError:
        return pd.DataFrame()

def get_missing_appids(games, game_entries):
    appids       = set(games       ['appid'])
    already_done = set()
    if 'appid' in game_entries.columns:
        already_done = set(game_entries['appid'])
    return appids - already_done

async def get_gameplay_times(games, game_entries):
    hltb = HowLongToBeat(1.0)
    missing_appids = get_missing_appids(games, game_entries)
    games = games.loc[games['appid'].isin(missing_appids)]

    tasks = [get_game_entry_from_hltb(hltb, row['name'], row['appid']) for _, row in games.iterrows()]
    
    completed, _ = await asyncio.wait(tasks)
    for completed_task in completed:
        (game_entry, appid) = completed_task.result()
        game_entries = add_game(game_entries, appid, game_entry)
    
    return game_entries

def main():
    games = pd.read_csv('data/steam_processed.csv')
    games = games.loc[0:100]
    game_entries = get_game_entries()
    results = asyncio.run(get_gameplay_times(games, game_entries))
    results.to_csv(HLTB_CSV, index=False)
    
if __name__ == '__main__':
    main()
