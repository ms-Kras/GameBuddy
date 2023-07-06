import pandas as pd

def preprocessing_df (df: pd.DataFrame):
    df = df.copy()
    df.dropna(how='any', subset=['Date', 'Tags'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], format='%d %b, %Y', errors='coerce')
    try: df['Year'] = df['Date'].dt.year.astype(int)
    except: df['Year'] = df['Date'].dt.year
    columns_to_drop = ['Total Review Cnt','Pos Review Cnt', 'Neg Review Cnt', 'Price', 'Unnamed: 0']
    df.drop(columns_to_drop, axis=1, inplace=True)
    df.dropna(how='any', subset=['Date'], inplace=True)
    df['appid'] = df['appid'].astype(int)

    print ('preprocessing of the df is done')
    return df


def processing_for_tfidf (df: pd.DataFrame): 
    df = df.copy()
    df = df.filter(['appid', 'Year', 'Genre', 'Tags'], axis=1)
    df['Genre'] = df['Genre'].str.lower()
    df['Tags'] = df['Tags'].str.lower()
    df['Vector'] = df['Genre'] + ' ' + df['Tags']

    print ('preprocessing for tfidf is done')
    return df
