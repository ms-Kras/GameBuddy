import pandas as pd 
import requests
import json
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from lightfm import LightFM
from scipy.sparse import csr_matrix


class LightfmRecomender: 
    
    def __init__(self, users_games_df_path, item_dict_path):

        self.id = None
        self.users_games_df = pd.read_csv(users_games_df_path)
        self.users_games_df.columns = ['steam_id', 'game_id', 'ranking']
        self.item_dict = json.load(open(item_dict_path))
        self.item_dict = {int(k): v for k, v in self.item_dict.items()}
        self.scaler = MinMaxScaler(feature_range=(0, 100))
        self.model = LightFM(loss='bpr',
                            random_state=42,
                            learning_rate=0.10,
                            no_components=100,
                            user_alpha=0.000005)
        


    def get_user_games(self, steamid):
        
        url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key=ED07BAAA8209FFE5932318F82B8242A6&format=json&steamid={steamid}'
        response = requests.get(url)
        profile = response.json()

        id_df = pd.DataFrame([steamid], columns=['steam_id'])
        for game in profile['response']['games']:
            appid = game['appid']
            playtime = game['playtime_forever']
            temp_df = pd.DataFrame({
                'steam_id': [steamid],
                appid: [playtime]
            })
            id_df = pd.merge(id_df, temp_df, on='steam_id', how='inner')
            transformed_user_profile = []
        
            for index, row in id_df.iterrows():
                user_id = row.values[0]

                for game_ids, ranking in row.items():
                    if game_ids != 'steam_id':
                        transformed_user_profile.append([user_id, game_ids, ranking])

        transformed_user_profile = pd.DataFrame(transformed_user_profile, columns=['steam_id', 'game_id', 'ranking'])
        transformed_user_profile['ranking'] = self.scaler.fit_transform(transformed_user_profile[['ranking']])
        transformed_user_profile['ranking'] = pd.to_numeric(transformed_user_profile['ranking'])
        games_ids_df = self.__get_unique_games_ids()
        merged_df = games_ids_df.merge(transformed_user_profile, on='game_id', how='left')
        merged_df['steam_id'] = steamid
        merged_df.fillna(0, inplace=True)
            
        return merged_df
    
    
    def __get_unique_games_ids (self): 
        games_ids = self.users_games_df['game_id'].unique()
        games_ids_df = pd.DataFrame(games_ids, columns=['game_id']).astype(int)

        return games_ids_df
    
    def get_csr_matrix_for_all_users (self, df_user): 
        one_user_interactions = pd.pivot_table(df_user, index='steam_id', columns='game_id', values='ranking')
        all_users_interactions = pd.pivot_table(self.users_games_df, index='steam_id', columns='game_id', values='ranking')
        new_user_added_df = pd.concat([all_users_interactions, one_user_interactions], axis=0)
        new_user_added_df = new_user_added_df.fillna(0)
        new_user_added_df_csr = csr_matrix(new_user_added_df)

        return new_user_added_df_csr, new_user_added_df
    

    def __get_steam_ids(self, df): 
        user_id = list(df.index)
        user_dict = {}
        counter = 0 
        for i in user_id:
            user_dict[i] = counter
            counter += 1
        return user_dict
    
    def fit_model (self, csr_matrix, num_threads = 8, epochs= 100): 
        model = self.model.fit(csr_matrix, num_threads=num_threads, epochs=epochs)

        return model
    
    
    def sample_recommendation_user(self, model, interactions, user_id,
                               threshold = 0,nrec_items = 5, show = True):

        self.user_dict = self.__get_steam_ids(interactions)


        n_users, n_items = interactions.shape
        user_x = self.user_dict[user_id]
        scores = pd.Series(model.predict(user_x,np.arange(n_items), item_features=None))
        scores.index = interactions.columns
        scores = list(pd.Series(scores.sort_values(ascending=False).index))
        
        known_items = list(pd.Series(interactions.loc[user_id,:] \
                                    [interactions.loc[user_id,:] > threshold].index).sort_values(ascending=False))
        
        scores = [x for x in scores if x not in known_items]
        return_score_list = scores[0:nrec_items]
        known_items = [self.item_dict[x] if x in self.item_dict else x for x in known_items]
        scores = [self.item_dict[x] if x in self.item_dict else x for x in return_score_list]
        
        if show == True:
            print ("User: " + str(user_id))
            print("Recommended Items:")
            counter = 1
            for i in scores:
                print(str(counter) + '- ' + str(i))
                counter+=1


            print("\n Known Likes:")
            counter = 1
            for i in known_items:
                print(str(counter) + '- ' + str(i))
                counter+=1

