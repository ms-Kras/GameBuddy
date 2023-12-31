import pandas as pd 
import requests
import json
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from lightfm import LightFM
from scipy.sparse import csr_matrix
import re
from bs4 import BeautifulSoup


import sqlite3


class LightfmRecomender: 
    
    def __init__(self, gametime_df_path, item_dict_path):

        self.gametime_df = pd.read_csv(gametime_df_path)
        self.scaler = MinMaxScaler(feature_range=(0,10))
        self.gametime_df = self.__gametime_transform(self.gametime_df)
        self.gametime_df.columns = ['steam_id', 'game_id', 'ranking']
        self.item_dict = json.load(open(item_dict_path))
        self.item_dict = {int(k): v for k, v in self.item_dict.items()}
        self.model = LightFM(loss='bpr',
                            random_state=42,
                            learning_rate=0.10,
                            no_components=100,
                            user_alpha=0.000005)
        
    def __get_profile_id(self, url):
        
        userpage = requests.get(url)
        user_page = BeautifulSoup(userpage.content, 'lxml')
        text = str(user_page.find('div', class_="responsive_page_template_content"))
        steamid = int(text[text.find('"steamid"')+11:text.find('"steamid"')+28])
        
        return steamid

    def __gametime_transform(self, df): 
        
        df.iloc[:,:-1] = np.log(df.iloc[:,:-1])
        df.iloc[:,:-1] = df.iloc[:,:-1].replace([np.inf, -np.inf], 0.0)
        df.iloc[:,:-1] = self.scaler.fit_transform(df.iloc[:,:-1])
        transformed_df = pd.melt(df, id_vars='steamid', var_name='game_id', value_name='ranking')
        transformed_df['game_id'] = transformed_df['game_id'].astype(int)
        
        return transformed_df

    def get_user_games(self, url):
        
        steamid = self.__get_profile_id(url)

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
       
        transformed_user_profile = pd.melt(id_df, id_vars='steam_id', var_name='game_id', value_name='ranking')
        transformed_user_profile['game_id'] = transformed_user_profile['game_id'].astype(int)
        transformed_user_profile['ranking'] = np.log(transformed_user_profile['ranking'].replace(0, np.nan)).replace(-np.inf, np.nan)
        transformed_user_profile['ranking'] = self.scaler.fit_transform(transformed_user_profile[['ranking']])
        transformed_user_profile['ranking'] = pd.to_numeric(transformed_user_profile['ranking'])
        games_ids_df = self.__get_unique_games_ids()
        merged_df = games_ids_df.merge(transformed_user_profile, on='game_id', how='left')
        merged_df['steam_id'] = steamid
        merged_df.fillna(0, inplace=True)
            
        return merged_df, steamid
    
    def get_user_games_cold_start (self, df): 
        df.columns = ['game_name', 'ranking']
        df['game_id'] = df['game_name'].map({v: k for k, v in self.item_dict.items()})
        df['ranking'] = self.scaler.fit_transform(df[['ranking']])
        df.drop('game_name', axis=1)
        games_ids_df = self.__get_unique_games_ids()
        df = games_ids_df.merge(df, on='game_id', how='left')
        df['steam_id'] = 1234567891010102930
        df.fillna(0, inplace=True)
        
        return df, df['steam_id'][0]

    
    
    def __get_unique_games_ids (self): 
        games_ids = self.gametime_df['game_id'].unique()
        games_ids_df = pd.DataFrame(games_ids, columns=['game_id']).astype(int)

        return games_ids_df
    
    def get_csr_matrix_for_all_users (self, df_user): 
        one_user_interactions = pd.pivot_table(df_user, index='steam_id', columns='game_id', values='ranking')
        all_users_interactions = pd.pivot_table(self.gametime_df, index='steam_id', columns='game_id', values='ranking')
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
#----------------------------update by ms_Kras------------------------------------------------#
        else:
            return scores

