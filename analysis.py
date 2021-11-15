
import seaborn as sb
import pandas as pd
import matplotlib.pyplot as plt

from prepare import process_steam_data

MIN_REPORTS = 5
PROTON_DB_TIERS_ALL = ['unknown', 'pending', 'borked', 'bronze', 'silver', 'gold', 'platinum']
PROTON_DB_TIERS = ['borked', 'bronze', 'silver', 'gold', 'platinum']

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
    hltb_df = pd.read_csv('data/hltb.csv')
    proton_df = pd.read_csv('data/proton_db.csv')
    reviews_df = pd.read_csv('data/reviews.csv')

    steam_df = process_steam_data(steam_df)
    steam_df['review_score'] = (steam_df['positive_ratings'] /
            (steam_df['positive_ratings'] + steam_df['negative_ratings']))

    # print(steam_df.sort_values('review_score', ascending=False)[['name', 'review_score']].head(20))
    
    # Review score distribution
    sb.histplot(data=steam_df, x='review_score', bins=20).set(title="Review Score Distribution", ylabel="Count", xlabel="Review Score")
    plt.show()

    # Price distribution
    df = steam_df.loc[steam_df['price'] <= 60]
    g = sb.histplot(data=df, x='price', binwidth=2.5)
    g.set(title="Price Distribution (up to 60$)", ylabel="Count", xlabel="Price")
    g.bar_label(g.containers[0])
    plt.show()

    # steam_df['decimal'] = steam_df['price'] % 1
    # sb.histplot(data=steam_df, x='decimal', binwidth=0.01).set(title="Decimal Part of the Price Distribution", ylabel="Count", xlabel="Decimal Part of the Price")
    # plt.show()

    # Number of games released per year
    steam_df['release_year'] = steam_df['release_date'].apply(lambda x: x.year)
    df = steam_df.groupby('release_year')['appid'].count().rename('num_games').reset_index()
    df = df[df['release_year'] < 2019]
    g = sb.lineplot(data=df, x='release_year', y='num_games')
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
            title='Percentage of Games within the Indie Genre',
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
    g.set(title="Owners Distribution", ylabel="Count", xlabel="Number of Owners")
    g.bar_label(g.containers[0])
    plt.show()

    # ProtonDB rating histogram
    sb.countplot(
        data=proton_df[-(proton_df['protondb_tier'].isin(['unknown', 'pending']))],
        x='protondb_tier',
        order=PROTON_DB_TIERS,
    ).set(title="ProtonDB Tiers Distribution", ylabel="Count", xlabel="ProtonDB Tiers")
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
        hue_order=['native', 'platinum', 'gold', 'silver', 'bronze', 'borked'],
        palette=['forestgreen', 'lightsteelblue', 'gold', 'slategrey', 'chocolate', 'firebrick'])
    g.set(title='ProtonDB tier distribution per release year')
    g.get_legend().set_title('ProtonDB Tier')
    plt.show()

    merged = pd.merge(steam_df, hltb_df, on='appid')

    merged = merged.loc[merged['main_reports'] >= MIN_REPORTS]
    merged = merged.loc[merged['extras_reports'] >= MIN_REPORTS]
    merged = merged.loc[merged['completionist_reports'] >= MIN_REPORTS]

    merged['main_time'] = merged['main_time'].div(60)
    merged['extras_time'] = merged['extras_time'].div(60)
    merged['completionist_time'] = merged['completionist_time'].div(60)

    main_per_year = merged.groupby('release_year')[['main_time', 'extras_time', 'completionist_time']].median().reset_index()

    sb.barplot(data=main_per_year, x='release_year', y='main_time') \
        .set(title="Median Main Story Time per Release Year", ylabel="Median Main Story Time (in hours)", xlabel="Release Year")
    plt.show()
    sb.barplot(data=main_per_year, x='release_year', y='extras_time') \
        .set(title="Median Main Story + Extras Time per Release Year", ylabel="Median Main Story + Extras Time (in hours)", xlabel="Release Year")
    plt.show()
    sb.barplot(data=main_per_year, x='release_year', y='completionist_time') \
        .set(title="Median Completionist Time per Release Year", ylabel="Median Completionist Time (in hours)", xlabel="Release Year")
    plt.show()


if __name__ == '__main__':
    main()
