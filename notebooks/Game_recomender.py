import re
import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import BM25

class GameRecommender:

    def __init__(self, filename, columns, t_column, d_column):
        self.filename = filename
        self.columns = columns
        self.title_column = t_column
        self.description_column = d_column
        self.df = None
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.model = SentenceTransformer('prajjwal1/bert-tiny')

    def process(self, show=True):
        self.df = pd.read_csv(self.filename, usecols=self.columns)
        self.df[self.description_column].fillna('', inplace=True)
        self.df[self.description_column] = self.df[self.title_column] + '. ' +  self.df[self.description_column].map(str)
        self.df.dropna(inplace=True)
        self.df.drop_duplicates(inplace=True)
        return self.df

    def get_normalized_corpus(self, tokens = False):
        norm_corpus = np.vectorize(self.__normalize_text)        
        if tokens:
            norm_courpus = norm_corpus(list(self.df[self.description_column]))
            return np.array([nltk.word_tokenize(d) for d in norm_courpus])            
        else:
            return norm_corpus(list(self.df[self.description_column]))

    def get_bert_weights(self, corpus):
        vectors = self.model.encode(corpus)
        weights = pd.DataFrame(cosine_similarity(vectors))
        return weights

    def search_games_by_term(self, term='game'):
        term = term.lower()
        games = self.df[self.title_column].values
        possible_options = [(i, game) for i, game in enumerate(games) for word in game.lower().split(' ') if word == term]
        return possible_options    
    
    def recommend_games_by_text(self, input_text, n=5):
        normalized_input = self.__normalize_text(input_text)

        # Get the features
        corpus = list(self.df[self.description_column])
        base_vectors = self.model.encode(corpus)

        # Calculate vector for new text
        new_vector = self.model.encode([normalized_input])

        # Calculate cosine similarity
        similarities = cosine_similarity(base_vectors, new_vector)
        similar_indices = np.argsort(-similarities.flatten())[:n]
        games = self.df[self.title_column].values
        recommended_games = games[similar_indices]
        
        return '\n'.join([game for game in recommended_games])


    def __normalize_text(self, text):
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text, re.I | re.A)
        text = text.lower().strip()
        tokens = nltk.word_tokenize(text)
        filtered_tokens = [t for t in tokens if t not in self.stopwords]
        return ' '.join(filtered_tokens)
