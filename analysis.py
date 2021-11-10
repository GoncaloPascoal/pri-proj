
from pandas.core.reshape.merge import merge
import seaborn as sb
import pandas as pd
import matplotlib.pyplot as plt

from prepare import process_steam_data

def sort_owners(x):
    return int(x.split('-')[0])

def rename_owners(x):
    def f(x):
        x = int(x)
        if x >= 1000000:
            return str(x // 1000000) + 'M'
        elif x >= 1000:
            return str(x // 1000) + 'K'
        else:
            return str(x)
    
    parts = x.split('-')
    low, high = parts[0], parts[1]
    return '-'.join([f(low), f(high)])

def main():
    steam_df = pd.read_csv('data/steam.csv')
    descriptions_df = pd.read_json('data/descriptions.json')
    hltb_df = pd.read_csv('data/hltb.csv')
    proton_df = pd.read_csv('data/proton_db.csv')
    reviews_df = pd.read_csv('data/reviews.csv')

    steam_df = process_steam_data(steam_df)
    steam_df['review_score'] = (steam_df['positive_ratings'] /
            (steam_df['positive_ratings'] + steam_df['negative_ratings']))

    # print(steam_df.sort_values('review_score', ascending=False)[['name', 'review_score']].head(20))
    
    # Review score distribution
    sb.histplot(data=steam_df, x='review_score', bins=10)
    plt.show()

    # Price distribution
    sb.histplot(data=steam_df, x='price', bins=8)
    plt.show()

    # Owners distribution
    owners_order = map(rename_owners, sorted(steam_df['owners'].unique(), key=sort_owners))
    steam_df['owners'] = steam_df['owners'].apply(rename_owners)
    sb.countplot(data=steam_df, order=owners_order, x='owners')
    plt.show()

    # ProtonDB rating histogram
    sb.countplot(
        data=proton_df[-(proton_df['protondb_tier'].isin(['unknown', 'pending']))],
        x='protondb_tier',
        order=['borked', 'bronze', 'silver', 'gold', 'platinum'],
    )
    plt.show()
    
    steam_df['release_year'] = steam_df['release_date'].apply(lambda x: x.year)
    merged = pd.merge(steam_df, hltb_df, on='appid')

    print(hltb_df[hltb_df.notnull()])

    main_per_year = merged.groupby('release_year')[['main_time', 'extra_time', 'completionist_time']].mean().reset_index()

    sb.barplot(data=main_per_year, x='release_year', y='main_time')
    plt.show()
    sb.barplot(data=main_per_year, x='release_year', y='extra_time')
    plt.show()

    sb.barplot(data=main_per_year, x='release_year', y='completionist_time')
    # sb.displot(data=merged, x='main_time', hue='release_year', multiple='fill')
    #sb.displot(data=merged, x='main_time', hue='release_year')
    
    plt.show()




if __name__ == '__main__':
    main()
