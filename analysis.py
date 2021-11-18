
import numpy as np
import seaborn as sb
import pandas as pd
import matplotlib.pyplot as plt

from prepare import process_steam_data

MIN_REPORTS = 5
PROTON_DB_TIERS = ['native', 'platinum', 'gold', 'silver', 'bronze', 'borked', 'pending', 'unknown']
PROTON_DB_COLORS = ['forestgreen', 'lightsteelblue', 'gold', 'slategrey', 'chocolate', 'firebrick', 'darkslategrey', 'black']

def sort_owners(x):
    return int(x.split('-')[0])

def shorten_num(x):
    x = int(x)
    if x >= 1000000:
        return str(x // 1000000) + 'M'
    elif x >= 1000:
        return str(x // 1000) + 'K'
    else:
        return str(x)

def rename_owners(x):
    parts = x.split('-')
    low, high = parts[0], parts[1]
    return '-'.join([shorten_num(low), shorten_num(high)])

def main():
    steam_df = pd.read_csv('data/steam.csv')

    steam_df = process_steam_data(steam_df)
    steam_df['review_score'] = (steam_df['positive_ratings'] /
            (steam_df['positive_ratings'] + steam_df['negative_ratings']))

    # print(steam_df.sort_values('review_score', ascending=False)[['name', 'review_score']].head(20))
    
    descriptions_df = pd.read_json('data/steam.json')[['appid', 'detailed_description']]
    descriptions_df['word_count'] = descriptions_df['detailed_description'].apply(lambda x: len(x.split()))

    # Description word count
    sb.histplot(data=descriptions_df, x='word_count', bins=50, binrange=(0, 2000)).set(
        title='Description Word Count',
        xlabel='Word Count',
        ylabel='Count',
    )
    plt.show()

    # Review score distribution
    steam_df['total_ratings'] = steam_df['positive_ratings'] + steam_df['negative_ratings']
    sb.histplot(data=steam_df[steam_df['total_ratings'] >= 50], x='review_score', bins=40).set(
        title="Review Score Distribution",
        ylabel="Count",
        xlabel="Review Score",
    )
    plt.show()

    reviews_df = pd.read_csv('data/reviews.csv')

    bins = [0, 60, 120, 240, 480, 1200, 2400, 4800, 12000, 24000, 48000, 120000, 240000, 480000, 1200000]
    names = []

    for i in range(len(bins) - 1):
        low = shorten_num(bins[i])
        high = shorten_num(bins[i + 1])
        names.append(low + '-' + high)

    reviews_df['playtime_binned'] = pd.cut(reviews_df['playtime_at_review'], bins)

    df = reviews_df.groupby(['playtime_binned', 'recommended'])['appid'].count().rename('rec_count').reset_index()
    df['rec_count'] = df['rec_count'].div(df.groupby('playtime_binned')['rec_count'].transform(lambda x: x.sum())).mul(100)

    # Percentage of recommendations per time played
    g = sb.barplot(data=df, x='playtime_binned', hue='recommended', y='rec_count', 
        hue_order=[True], palette=['forestgreen'])
    g.set(
        ylim=(0, 100),
        xlabel='Playtime at Review (in minutes)',
        ylabel='Recommended (%)',
        title='Percentage of Positive Reviews by Playtime'
    )
    g.get_legend().remove()
    g.bar_label(g.containers[0], fmt='%.1f')
    g.set_xticklabels(names)
    plt.show()

    # Price distribution
    df = steam_df.loc[steam_df['price'] <= 60]
    g = sb.histplot(data=df, x='price', binwidth=2.5)
    g.set(title='Game Price Distribution (up to $60)', ylabel='Count', xlabel='Price')
    plt.show()

    # steam_df['decimal'] = steam_df['price'] % 1
    # sb.histplot(data=steam_df, x='decimal', binwidth=0.01).set(title="Decimal Part of the Price Distribution", ylabel="Count", xlabel="Decimal Part of the Price")
    # plt.show()

    # Number of games released per year
    steam_df['release_year'] = steam_df['release_date'].apply(lambda x: x.year)
    df = steam_df.groupby('release_year')['appid'].count().rename('num_games').reset_index()
    df = df[df['release_year'] >= 2007]
    df = df[df['release_year'] < 2019]
    g = sb.lineplot(data=df, x='release_year', y='num_games')
    g.set(
        xlabel='Release Year',
        ylabel='Number of Games',
        title='Number of Games Released per Year (2007-2018)'
    )
    plt.show()

    # Indie games per year
    df = steam_df.copy()
    df = df[df['release_year'] >= 2007]
    df['indie'] = df['genres'].apply(lambda x: 'Indie' in x)
    df = df.groupby('release_year')['indie'].value_counts(normalize=True).mul(100).rename('indie_percent').reset_index()
    g = sb.histplot(data=df, x='release_year', hue='indie', weights='indie_percent', 
        discrete=True, multiple='stack', shrink=0.8, hue_order=[False, True],
        palette=['firebrick', 'forestgreen'])
    g.set(
            title='Percentage of Games within the Indie Genre Per Year',
            ylabel='Percentage',
            xlabel='Release Year',
        )
    g.get_legend().set_title('Indie')
    g.bar_label(g.containers[0], fmt='%.2f')
    plt.show()

    # Owners distribution
    owners_order = map(rename_owners, sorted(steam_df['owners'].unique(), key=sort_owners))
    steam_df['owners'] = steam_df['owners'].apply(rename_owners)
    g = sb.countplot(data=steam_df, order=owners_order, x='owners')
    g.set(title='No. of Owners Distribution', ylabel='Count', xlabel='Number of Owners')
    g.bar_label(g.containers[0])
    plt.show()
    
    proton_df = pd.read_csv('data/proton_db.csv')
    print('Games with ProtonDB rating:', 
        len(proton_df[-proton_df['protondb_tier'].isin(['unknown', 'pending'])]))

    # ProtonDB rating histogram
    g = sb.countplot(
        data=proton_df[-(proton_df['protondb_tier'].isin(['unknown']))],
        x='protondb_tier',
        order=PROTON_DB_TIERS[:7],
        palette=PROTON_DB_COLORS[:7],
    )
    g.set(title='ProtonDB Tier Distribution (Count)', ylabel='Count', xlabel='ProtonDB Tiers')
    g.bar_label(g.containers[0])
    plt.show()
    
    merged = pd.merge(steam_df, proton_df, on='appid')

    # merged['protondb_tier'] = merged['protondb_tier'].replace({
    #     'pending': 'unknown',
    #     'borked': 'unsatisfactory',
    #     'bronze': 'unsatisfactory',
    #     'silver': 'unsatisfactory',
    #     'gold': 'satisfactory',
    #     'platinum': 'satisfactory',
    #     'native': 'satisfactory',
    # })

    merged = merged[merged['release_year'] >= 2007]
    merged = merged[-merged['protondb_tier'].isin(['unknown', 'pending'])]
    merged = merged.groupby('release_year')['protondb_tier'].value_counts(normalize=True) \
        .mul(100).rename('proton_db_tier_percent').reset_index()

    g = sb.histplot(data=merged, x='release_year', hue='protondb_tier', 
        weights='proton_db_tier_percent', discrete=True, multiple='stack', shrink=0.8,
        hue_order=PROTON_DB_TIERS[:6],
        palette=PROTON_DB_COLORS[:6])
    g.set(title='ProtonDB Tier Distribution per Release Year (Percentage)')
    g.get_legend().set_title('ProtonDB Tier')
    g.set(xlabel='Release Year')
    plt.show()

    hltb_df = pd.read_csv('data/hltb.csv')

    merged = pd.merge(steam_df, hltb_df, on='appid')
    merged = merged[merged['release_year'] >= 2008]

    merged = merged.loc[merged['main_reports'] >= MIN_REPORTS]
    merged = merged.loc[merged['extras_reports'] >= MIN_REPORTS]
    merged = merged.loc[merged['completionist_reports'] >= MIN_REPORTS]

    merged['main_time'] = merged['main_time'].div(60)
    merged['extras_time'] = merged['extras_time'].div(60)
    merged['completionist_time'] = merged['completionist_time'].div(60)

    main_per_year = merged.groupby('release_year')[['main_time', 'extras_time', 'completionist_time']].median().reset_index()

    g = sb.barplot(data=main_per_year, x='release_year', y='main_time')
    g.set(title='Median Main Story Time per Release Year (2008-2019)', ylabel='Main Story Time (in hours)', xlabel='Release Year')
    g.bar_label(g.containers[0], fmt='%.2f')
    plt.show()
    
    g = sb.barplot(data=main_per_year, x='release_year', y='extras_time')
    g.set(title='Median Main Story + Extras Time per Release Year (2008-2019)', ylabel='Main Story + Extras Time (in hours)', xlabel='Release Year')
    g.bar_label(g.containers[0], fmt='%.2f')
    plt.show()
    
    g = sb.barplot(data=main_per_year, x='release_year', y='completionist_time')
    g.set(title='Median Completionist Time per Release Year (2008-2019)', ylabel='Completionist Time (in hours)', xlabel='Release Year')
    g.bar_label(g.containers[0], fmt='%.2f')
    plt.show()


if __name__ == '__main__':
    main()
