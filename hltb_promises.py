import requests
from bs4 import BeautifulSoup

HEADERS = {
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0"
}

def get_game_hltb_url(game_name):
    payload = {
        'queryString': game_name,
        't': 'games',
        'sorthead': 'popular',
        'sortd': 'Normal Order',
        'plat': '',
        'length_type': 'main',
        'length_min': '',
        'length_max': '',
        'detail': "hide_dlc"
    }
    # Make the post request and return the result if is valid
    r = requests.post('https://howlongtobeat.com/search_results.php', data=payload, headers=HEADERS)

    assert r.status_code == 200
    assert "We Found 1 Games" in r.text

    return "https://howlongtobeat.com/" + BeautifulSoup(r.text, features="lxml").find("a")["href"]

def get_game_playtime(game_url):
    table_entries = BeautifulSoup(requests.get(game_url, headers=HEADERS).text, features="lxml").find("table", {"class" : "game_main_table"}).find_all("tbody")
    
    res = {}
    for category, entry in zip(("Main Story", "Main + Extras", "Completionists"), table_entries):
        assert category in str(entry)
        res[category] = entry.find_all("td")[2].text.strip()
    
    return res

def main():
    print(get_game_playtime(get_game_hltb_url("Factorio")))

if __name__ == "__main__":
    main()