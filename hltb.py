from howlongtobeatpy import HowLongToBeat, HowLongToBeatEntry

import pandas as pd

def get_empty_game_entry(id):
    game_entry = HowLongToBeatEntry()
    game_entry.game_id = id
    game_entry.game_name = 'Undefined'
    game_entry.gameplay_main               = -1
    game_entry.gameplay_main_unit          = None
    game_entry.gameplay_main_extra         = -1
    game_entry.gameplay_main_extra_unit    = None
    game_entry.gameplay_completionist      = -1
    game_entry.gameplay_completionist_unit = None
    return game_entry

def print_entry(game_entry: HowLongToBeatEntry):
    print("Base Game Details")
    print("  Game Id: "                      + str(game_entry.game_id                     ))
    print("  Game Name: "                    + str(game_entry.game_name                   ))
    print("  Game Name Suffix: "             + str(game_entry.game_name_suffix            ))
    print("  Game Image URL: "               + str(game_entry.game_image_url              ))
    print("  Game Web Link: "                + str(game_entry.game_web_link               ))
    print("Gameplay Main")
    print("  Gameplay Main: "                + str(game_entry.gameplay_main               ))
    print("  Gameplay Main Unit: "           + str(game_entry.gameplay_main_unit          ))
    print("  Gameplay Main Label: "          + str(game_entry.gameplay_main_label         ))
    print("Gameplay Main + Extra")
    print("  Gameplay Main Extra: "          + str(game_entry.gameplay_main_extra         ))
    print("  Gameplay Main Extra Unit: "     + str(game_entry.gameplay_main_extra_unit    ))
    print("  Gameplay Main Extra Label: "    + str(game_entry.gameplay_main_extra_label   ))
    print("Completionist")
    print("  Gameplay Completionist: "       + str(game_entry.gameplay_completionist      ))
    print("  Gameplay Completionist Unit: "  + str(game_entry.gameplay_completionist_unit ))
    print("  Gameplay Completionist Label: " + str(game_entry.gameplay_completionist_label))
    print("Similarity with original name")
    print("  Similarity: "                   + str(game_entry.similarity                  ))

def print_times(game_entry: HowLongToBeatEntry):
    print("Game: " + game_entry.game_name)
    print("  Gameplay Main: "          + str(game_entry.gameplay_main         ) + str(game_entry.gameplay_main_unit         ))
    print("  Gameplay Main Extra: "    + str(game_entry.gameplay_main_extra   ) + str(game_entry.gameplay_main_extra_unit   ))
    print("  Gameplay Completionist: " + str(game_entry.gameplay_completionist) + str(game_entry.gameplay_completionist_unit))

def add_times_to_games(games, game_entries):
    # TODO
    return games

def get_minutes(time_unit):
    return 60 if time_unit == 'Hours' else 1 # 'Hours', 'Mins'

def get_time(time, time_unit):
    if time == -1 or time_unit == None:
        return -1
    return time * get_minutes(time_unit)

def add_game_entry(game_entries, game_entry):
    main_time          = get_time(game_entry.gameplay_main         , game_entry.gameplay_main_unit         )
    extra_time         = get_time(game_entry.gameplay_main_extra   , game_entry.gameplay_main_extra_unit   )
    completionist_time = get_time(game_entry.gameplay_completionist, game_entry.gameplay_completionist_unit)
    
    game_entries = game_entries.append({
        'appid': game_entry.game_id,
        'main_time': main_time,
        'extra_time': extra_time,
        'completionist_time': completionist_time
    }, ignore_index=True)

    return game_entries

def get_time_for_some_games(games):
    hltb = HowLongToBeat()
    game_entries = pd.DataFrame()
    for id in games['appid']:
        game_entry = hltb.search_from_id(id)
        if (game_entry == None):
            game_entry = get_empty_game_entry(id)
        game_entries = add_game_entry(game_entries, game_entry)
    return add_times_to_games(games, game_entries)

def main():
    games = pd.read_csv('data/steam_processed.csv')
    some_games = games.head()
    print(some_games)
    some_games = get_time_for_some_games(some_games)
    print(some_games)

if __name__ == '__main__':
    main()