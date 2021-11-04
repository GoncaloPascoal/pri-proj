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

def add_game(games, index, game_entry):
    main_time          = get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         )
    extra_time         = get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   )
    completionist_time = get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit)
    
    games.at[index, 'main_time'         ] = main_time
    games.at[index, 'extra_time'        ] = extra_time
    games.at[index, 'completionist_time'] = completionist_time
    
    return games

def add_new_columns(games):
    games.insert(len(games), 'main_time'         , -1)
    games.insert(len(games), 'extra_time'        , -1)
    games.insert(len(games), 'completionist_time', -1)
    return games

def get_time_for_some_games(games):
    hltb = HowLongToBeat(1.0)
    games = add_new_columns(games)
    for index in range(len(games)):
        name = games.loc[index]['name']
        game_entry = get_game_entry_from_hltb(hltb, name)
        games = add_game(games, index, game_entry)
    return games

def main():
    games = pd.read_csv('data/steam_processed.csv')
    some_games = games.head()
    #print(some_games)
    some_games = get_time_for_some_games(some_games)
    #print(some_games)

if __name__ == '__main__':
    main()