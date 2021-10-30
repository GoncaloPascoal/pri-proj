
import pandas as pd

def convert_to_list(df, col):
    df[col] = df[col].apply(lambda x: x.split(';'))

def minutes_to_hours(df, col):
    df[col] = df[col].apply(lambda x: x / 60.0)

def main():
    df = pd.read_csv('data/steam.csv')
    df['english'] = df['english'].astype(bool)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['owners'] = df['owners'].astype('category')

    for col in ['developer', 'publisher', 'platforms', 'categories', 'genres', 'steamspy_tags']:
        convert_to_list(df, col)

    for col in ['average_playtime', 'median_playtime']:
        minutes_to_hours(df, col)

if __name__ == '__main__':
    main()
