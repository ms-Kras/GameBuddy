from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def get_user_input():
    preferences = {}

    # Get user input for release date, genres, and descriptive words
    preferences['Release_Date'] = input('Enter preferred release date (YYYY-MM-DD): ')
    preferences['Genres'] = input('Enter preferred genres (comma-separated): ')
    preferences['Descriptive_Words'] = input('Enter description for the game: ')

    # Create a DataFrame from the user input
    user_df = pd.DataFrame([preferences])

    return user_df

def calculate_vector(user_df):
    
    # Create a TF-IDF vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the data using the vectorizer
    tfidf_matrix = vectorizer.fit_transform(user_df['Genres'] + ' ' + user_df['Descriptive_Words'])

    # Get the vector representation for the user input
    user_vector = tfidf_matrix[-1]

    return user_vector
