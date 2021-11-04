from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry

import pandas as pd

def get_empty_game_entry(id):
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
        return -1
    return time * get_minutes(time_unit)

def get_game_entry_from_hltb(hltb, name):
    results = hltb.search(name, similarity_case_sensitive=False)
    if results is None or len(results) == 0:
        return get_empty_game_entry(id)
    else:
        return results[0]

def add_times_to_games(games, game_entries):
    return games.merge(right=game_entries, left_on='appid', right_on='appid')

def add_game_entry(game_entries, game_entry):
    main_time          = get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         )
    extra_time         = get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   )
    completionist_time = get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit)
    
    game_entries = game_entries.append({
        'main_time': main_time,
        'extra_time': extra_time,
        'completionist_time': completionist_time
    }, ignore_index=True)

    return game_entries

def get_time_for_some_games(games):
    hltb = HowLongToBeat(1.0)
    game_entries = pd.DataFrame()
    for index in range(len(games)):
        name = games.loc[index]['name']
        game_entry = get_game_entry_from_hltb(hltb, name)
        game_entries = add_game_entry(game_entries, game_entry)
    #return add_times_to_games(games, game_entries)

def main():
    games = pd.read_csv('data/steam_processed.csv')
    some_games = games.head()
    print(some_games)
    some_games = get_time_for_some_games(some_games)
    print(some_games)

if __name__ == '__main__':
    main()