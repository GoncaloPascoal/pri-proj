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
        return None
    if type(time) is str:
        if '½' in time:
            time = int(time[:len(time) -1]) + 0.5
        else:
            time = int(time)
    return time * get_minutes(time_unit)

def get_game_entry_from_hltb(hltb, name):
    results = hltb.search(name, similarity_case_sensitive=False)
    if results is None or len(results) == 0:
        return get_empty_game_entry(id)
    else:
        return results[0]

def add_game(games, id, game_entry):
    return games.append({
        'appid': id,
        'main_time' : get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         ),
        'extra_time' : get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   ),
        'completionist_time': get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit)
    }, ignore_index=True)

def add_new_columns(games):
    games.insert(len(games), 'main_time'         , -1)
    games.insert(len(games), 'extra_time'        , -1)
    games.insert(len(games), 'completionist_time', -1)
    return games

def get_gameplay_times(games):
    hltb = HowLongToBeat(1.0)
    game_entries = pd.DataFrame()
    for _, row in games.iterrows():
        game_entry = get_game_entry_from_hltb(hltb, row['name'])
        game_entries = add_game(game_entries, row['appid'], game_entry)
    return game_entries

def main():
    games = pd.read_csv('data/steam_processed.csv')
    games = games.head()
    games = get_gameplay_times(games)
    games.to_csv('data/gameplay_times.csv', index=False)

if __name__ == '__main__':
    main()
