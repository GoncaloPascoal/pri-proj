
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
    sb.histplot(data=steam_df, x='review_score', bins=10).set(title="Review Score Distribution", ylabel="Count", xlabel="Review Score")
    plt.show()

    # Price distribution
    df = steam_df.loc[steam_df['price'] <= 50]
    sb.histplot(data=df, x='price', bins=200).set(title="Price Distribution (< 50$)", ylabel="Count", xlabel="Price")
    plt.show()

    steam_df['decimal'] = steam_df['price'] % 1
    sb.histplot(data=steam_df, x='decimal', binwidth=0.01).set(title="Decimal Part of the Price Distribution", ylabel="Count", xlabel="Decimal Part of the Price")
    plt.show()

    # Owners distribution
    print(steam_df['owners'].nunique())
    owners_order = map(rename_owners, sorted(steam_df['owners'].unique(), key=sort_owners))
    steam_df['owners'] = steam_df['owners'].apply(rename_owners)
    sb.countplot(data=steam_df, order=owners_order, x='owners').set(title="Owners Distribution", ylabel="Count", xlabel="Number of Owners")
    plt.show()

    # ProtonDB rating histogram
    sb.countplot(
        data=proton_df[-(proton_df['protondb_tier'].isin(['unknown', 'pending']))],
        x='protondb_tier',
        order=['borked', 'bronze', 'silver', 'gold', 'platinum'],
    ).set(title="ProtonDB Tiers Distribution", ylabel="Count", xlabel="ProtonDB Tiers")
    plt.show()
    
    steam_df['release_year'] = steam_df['release_date'].apply(lambda x: x.year)
    merged = pd.merge(steam_df, hltb_df, on='appid')

    print(hltb_df[hltb_df.notnull()])

    main_per_year = merged.groupby('release_year')[['main_time', 'extras_time', 'completionist_time']].mean().reset_index()

    sb.barplot(data=main_per_year, x='release_year', y='main_time').set(title="Average Main Story Time per Release Year", ylabel="Average Main Story Time", xlabel="Release Year")
    plt.show()
    sb.barplot(data=main_per_year, x='release_year', y='extras_time').set(title="Average Main Story + Extras Time per Release Year", ylabel="Average Main Story + Extras Time", xlabel="Release Year")
    plt.show()
    sb.barplot(data=main_per_year, x='release_year', y='completionist_time').set(title="Average Completionist Time per Release Year", ylabel="Average Completionist Time", xlabel="Release Year")
    plt.show()




if __name__ == '__main__':
    main()
