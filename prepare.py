
import pandas as pd

def convert_to_list(df, col):
    df[col] = df[col].apply(lambda x: x.split(';'))

def main():
    df = pd.read_csv('data/steam.csv')
    df['english'] = df['english'].astype(bool)

    for col in ['platforms', 'categories', 'genres', 'steamspy_tags']:
        convert_to_list(df, col)

if __name__ == '__main__':
    main()
