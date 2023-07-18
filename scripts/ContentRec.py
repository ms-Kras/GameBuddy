import numpy as np
import pandas as pd
import sqlite3

class ContentRec:
    def __init__(self, db_path):
        self.db_path = db_path
        self.game_info = None
        self.appids_list = None
        self.V_matrix = None

    def connect_db(self):
        conn = sqlite3.connect(self.db_path)
        return conn

    def read_game_info_table(self):
        conn = self.connect_db()
        query = "SELECT game, rating FROM ratings"
        df = pd.read_sql_query(query, conn)
        conn.close()
        max_rating = df['rating'].max()
        game_with_max_rating = df[df['rating'] == max_rating]['game'].iloc[0]
        max_rating = int(max_rating)
        return max_rating, game_with_max_rating

    def get_appid_by_game_name(self, game_name):
        conn = self.connect_db()
        query = "SELECT appid FROM game_info WHERE Name = ?"
        cursor = conn.cursor()
        cursor.execute(query, (game_name,))
        appid = cursor.fetchone()[0]
        conn.close()
        return appid

    def get_game_name_by_appid(self, appid):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Name FROM game_info WHERE appid = ?", (appid,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        else:
            return None

    def second_step(self, appid):
        app_id = int(np.where(self.appids_list == [str(appid)])[0])
        k = 50
        top_n = 10
        sliced = self.V_matrix.T[:, :k]
        indexes = self.top_cosine_similarity(sliced, app_id, top_n)
        rec_ids = self.appids_list[indexes[1:]]
        rec_ids = rec_ids.astype('int')
        rec_ids_str = ', '.join(map(str, rec_ids))
        rec_ids_list = rec_ids_str.split(', ')
        game_names=self.get_games_with_descriptions(rec_ids_list)
        return game_names

    def top_cosine_similarity(self, data, app_id, top_n=10):
        index = app_id
        app_row = data[index, :]
        magnitude = np.sqrt(np.einsum('ij, ij -> i', data, data))
        similarity = np.dot(app_row, data.T) / (magnitude[index] * magnitude)
        sort_indexes = np.argsort(-similarity)
        return sort_indexes[:top_n]

    def first_step(self, genres, genres_neg, tags, tags_neg):
        test_df = self.game_info
        test_df = test_df.sort_values('Score', ascending=False)
        top5 = []
        for tag_neg in tags_neg:
            filtered_df = test_df[~test_df['Tags'].str.contains(tag_neg)]
            if len(top5) + len(filtered_df) >= 20:
                top5 += filtered_df['appid'].head(20 - len(top5)).tolist()
                break
        if len(top5) < 20:
            for genre in genres:
                filtered_df = test_df[test_df['Genres'].str.contains(genre)]
                if len(top5) + len(filtered_df) >= 20:
                    top5 += filtered_df['appid'].head(20 - len(top5)).tolist()
                    break
        if len(top5) < 20:
            for genre_neg in genres_neg:
                filtered_df = test_df[~test_df['Genres'].str.contains(genre_neg)]
                if len(top5) + len(filtered_df) >= 20:
                    top5 += filtered_df['appid'].head(20 - len(top5)).tolist()
                    break
        if len(top5) < 20:
            for tag in tags:
                filtered_df = test_df[test_df['Tags'].str.contains(tag)]
                if len(top5) + len(filtered_df) >= 20:
                    top5 += filtered_df['appid'].head(20 - len(top5)).tolist()
                    break
        top5 = test_df.head(5)['appid'].to_list()
        return self.get_games_with_descriptions(top5)

    def get_games_with_descriptions(self, top5):
        conn = self.connect_db()
        cursor = conn.cursor()
        placeholders = ', '.join(['?'] * len(top5))
        query = f"SELECT Name, description FROM game_info WHERE appid IN ({placeholders})"
        cursor.execute(query, top5)
        rows = cursor.fetchall()
        conn.close()
        game_names = [row[0] for row in rows]
        game_descriptions = [row[1] for row in rows]
        return list(zip(game_names, game_descriptions))

    def get_user_preferences(self):
        conn = self.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT genres, disliked_genres, tags, disliked_tags FROM user_data ORDER BY rowid DESC LIMIT 1;")
        row = cursor.fetchone()
        conn.close()
        if row:
            genres = row[0].split(', ')
            disliked_genres = row[1].split(', ')
            tags = row[2].split(', ')
            disliked_tags = row[3].split(', ')
        else:
            genres = []
            disliked_genres = []
            tags = []
            disliked_tags = []
        return genres, disliked_genres, tags, disliked_tags

    def initialize(self):
        conn = self.connect_db()
        self.game_info = pd.read_sql_query(f"SELECT * FROM game_info", conn)
        conn.close()
        self.appids_list = np.load('GB.app/appids.npy', allow_pickle=True)
        self.V_matrix = np.load('GB.app/user_matrix.npy')


