from flask import Flask, render_template, request, redirect, url_for
from ContentRec import ContentRec
import sqlite3


app = Flask(__name__, template_folder='/home/nika/GameBuddy/GB.app/templates/opros')

db_path = '/home/nika/GameBuddy/GB.app/database.db'

genres = ['Action', 'Adventure', 'AnimationModeling', 'AudioProduction', 'Casual', 'DesignIllustration', 'EarlyAccess', 'Education', 
          'FreetoPlay', 'GameDevelopment', 'Indie', 'MassivelyMultiplayer', 'Movie', 'PhotoEditing', 'RPG', 'Racing', 'Simulation', 
          'SoftwareTraining', 'Sports', 'Strategy', 'Utilities', 'VideoProduction', 'WebPublishing']

tags = [ 'DFighter', 'Difficult', 'TurnBasedTactics', 'ChoicesMatter', 'FemaleProtagonist', 'SoftwareTraining', 'AutomobileSim', 'Sandbox', 
        'Puzzle', 'Zombies', 'ThirdPerson', 'Lemmings', 'WorldWarII', 'Comedy', 'RPGMaker', 'Memes', 'Mechs', 'MMORPG', 'MassivelyMultiplayer',
        'PointClick', 'Medieval', 'Building', 'Cats', 'SocialDeduction', 'DPlatformer', 'VideoProduction', 'AudioProduction', 'Utilities', 
        'Spectaclefighter', 'Indie', 'StrategyRPG', 'Relaxing', 'Atmospheric', 'Colorful', 'Music', 'MOBA', 'Typing', 'WarhammerK', 'FreetoPlay', 
        'RTS', 'Nudity', 'Retro', 'ArenaShooter', 'ShootEmUp', 'ThirdPersonShooter', 'Roguelite', 'Crime', 'Exploration']

years = ['2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', 
         '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002', '2001', '2000']

languages = ['English', 'Russian', 'French']

class GameRecommendationApp:
    def __init__(self, recommendations):
        # for i in range (0, len(recommendations)):
        #     print(recommendations[i][0] + " " + recommendations[i][1] + "\n")
        self.recommendations = recommendations
        self.current_index = 0

    def get_next_game(self):
        if self.current_index < len(self.recommendations):
            #добавил изменение индекса после того, как новая игра взята
            game = self.recommendations[self.current_index][0]
            self.current_index = self.current_index + 1
            return game
        else:
            return None
        
    def get_current_game(self):
        if self.current_index > 0:
            return self.recommendations[self.current_index - 1][0]
        else:
            return None
        
    def get_current_game_description(self):
        if self.current_index > 0:
            return self.recommendations[self.current_index - 1][1]  # Индекс 1 соответствует описанию игры
        else:
            return None
    
    def has_more_games(self):
        return self.current_index < len(self.recommendations)

    def rate_game(self, rating):
        game = self.recommendations[self.current_index]
        self.save_rating(game,rating)
        self.current_index += 1

    def save_rating(self, game, rating):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            game TEXT,
                            rating TEXT
                        )''')

        cursor.execute("INSERT INTO ratings (game, rating) VALUES (?, ?)", (game, rating))

        conn.commit()
        conn.close()



def save_data(genres, disliked_genres, tags, disliked_tags, years, languages, wishes, steams):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        genres TEXT,
                        disliked_genres TEXT,
                        tags TEXT,
                        disliked_tags TEXT,
                        years TEXT,
                        languages TEXT,
                        wishes TEXT,
                        steams TEXT
                    )''')
    
    conn.commit()
    
    cursor.execute("INSERT INTO user_data (genres, disliked_genres, tags, disliked_tags, years, languages, wishes, steams) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (', '.join(genres), ', '.join(disliked_genres), ', '.join(tags), ', '.join(disliked_tags),
                    ', '.join(years), ', '.join(languages), wishes, steams))

    conn.commit()
    conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_genres = request.form.getlist('genres')
        selected_disliked_genres = request.form.getlist('disliked_genres')
        selected_tags = request.form.getlist('tags')
        selected_disliked_tags = request.form.getlist('disliked_tags')
        selected_years = request.form.getlist('years')
        selected_languages = request.form.getlist('languages')
        wishes = request.form.get('wishes')
        steams = request.form.get('steams')

        save_data(selected_genres, selected_disliked_genres, selected_tags, selected_disliked_tags,
                  selected_years, selected_languages, wishes, steams)

        if steam_url == None:
            return redirect(url_for('recommendations'))
        else:
            return redirect(url_for('completed'))
    else:
        return render_template('index.html', genres=genres, tags=tags, years=years, languages=languages)
    
def get_user_data():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT genres, tags, wishes FROM user_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()

    conn.close()

    if row:
        genres, tags, wishes = row
        input_text = f"{genres} {tags} {wishes}"
        return input_text
    else:
        return ""

# -------------------------------------------новая версия, Ванина модель--------------------------------------------------
# Создание экземпляра класса GameBuddy и инициализация данных
game_buddy = ContentRec('/home/nika/GameBuddy/GB.app/database.db')
print('class created')
game_buddy.initialize()
print('class initiated')
# пользователь заполняет опрос, мы сортируем топ игр и выдаем топ-5 в виде списка списков
genres_us, genres_neg_us, tags_us, tags_neg_us=game_buddy.get_user_preferences()
print('user preferences set')
recommendations = game_buddy.first_step(genres_us, genres_neg_us, tags_us, tags_neg_us)
print('recommendations given')
# поиск игры с макс рейтингом в базе по пользователю
max_rating, game_with_max_rating = game_buddy.read_game_info_table()
print(max_rating, game_with_max_rating)
# если в базе есть игра с оценкой не ниже 7
if max_rating>=7:
    # подтаскиваем ее айдишник
    appid = game_buddy.get_appid_by_game_name(game_with_max_rating)
    print('appid received')
    # и переходим на второй шаг, на выходе - список игр с описаниями в формате списка списков
    recommendations = game_buddy.second_step(appid)
    print('game list/description obtained')
game_app = GameRecommendationApp(recommendations)
print('class created')
# -------------------------------------------новая версия, Ванина модель--------------------------------------------------
# ----------------------------------вот этот кусок вставить для получения списка рекомендаций------------------------------------------#
from lightfm_recomender import LightfmRecomender
import pandas as pd

db_path = '/home/nika/GameBuddy/GB.app/database.db'



####-------steam--------###
def get_user_steam():
    conn = sqlite3.connect('/home/nika/GameBuddy/GB.app/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT steams FROM user_data ORDER BY rowid DESC LIMIT 1;")
    steams = cursor.fetchone()[0]
    conn.close()
    return steams


steam_url=get_user_steam()
####-------steam--------###

def lfm_games_with_descriptions(top5):
    conn = sqlite3.connect('/home/nika/GameBuddy/GB.app/database.db')
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(top5))
    query = f"SELECT Name, description FROM game_info WHERE Name IN ({placeholders})"
    cursor.execute(query, top5)
    rows = cursor.fetchall()
    conn.close()
    game_names = [row[0] for row in rows]
    game_descriptions = [row[1] for row in rows]
    return list(zip(game_names, game_descriptions))

def lfm_game_info_table(db_path):
    conn = sqlite3.connect(db_path)
    query = "SELECT game,rating FROM ratings"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


df_cold_start = lfm_game_info_table(db_path)
item_dict_path = '/home/nika/GameBuddy/data/for_models/item_dict.json'
gametime_df_path = '/home/nika/GameBuddy/data/final_gametime_df.csv'
lfr = LightfmRecomender(gametime_df_path, item_dict_path)

# if steam_url == '':
#     cold_start_user, steamid_cold = lfr.get_user_games_cold_start(df_cold_start)
#     matrix_cs, df_cs = lfr.get_csr_matrix_for_all_users(cold_start_user)
#     model = lfr.fit_model(matrix_cs, epochs=10)
#     top_10=lfr.sample_recommendation_user(model, df_cs, steamid_cold, threshold = 0, nrec_items = 10,show=False)
# else:
#     new_user, steamid = lfr.get_user_games(steam_url)
#     matrix, df = lfr.get_csr_matrix_for_all_users(new_user)
#     model = lfr.fit_model(matrix, epochs=10)
#     top_10=lfr.sample_recommendation_user(model, df, steamid, threshold = 0, nrec_items = 10,show=False)

# lfm_reccomendations=lfm_games_with_descriptions(top_10)
# ----------------------------------вот этот кусок вставить для получения списка рекомендаций-----------------------------------------#
@app.route('/recommendations')
def recommendations():
    print("run recommendations")
    game = game_app.get_next_game()
    if game:
        index = game_app.current_index
        description = game_app.get_current_game_description()
        return render_template('rate.html', game=game, index=index, description=description)
    else:
        return render_template('completed.html', lfm_reccomendations=lfm_reccomendations)

@app.route('/completed')
def completed():
    print("completed run")

# ----------------------------------повторный прогон для актуализации-----------------------------------------#
    steam_url=get_user_steam()
    if steam_url == '':
        cold_start_user, steamid_cold = lfr.get_user_games_cold_start(df_cold_start)
        matrix_cs, df_cs = lfr.get_csr_matrix_for_all_users(cold_start_user)
        model = lfr.fit_model(matrix_cs, epochs=10)
        top_10=lfr.sample_recommendation_user(model, df_cs, steamid_cold, threshold = 0, nrec_items = 10,show=False)
    else:
        new_user, steamid = lfr.get_user_games(steam_url)
        matrix, df = lfr.get_csr_matrix_for_all_users(new_user)
        model = lfr.fit_model(matrix, epochs=10)
        top_10=lfr.sample_recommendation_user(model, df, steamid, threshold = 0, nrec_items = 10,show=False)

    lfm_reccomendations=lfm_games_with_descriptions(top_10)
# ----------------------------------повторный прогон для актуализации-----------------------------------------#
    print("steam id: ", steam_url)
    for record in lfm_reccomendations:
        print(record[0])
    return render_template('completed.html', lfm_reccomendations=lfm_reccomendations)

def save_rating(game, rating):
    print("run save_rating")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game TEXT,
                        rating INTEGER
                    )''')

    cursor.execute("INSERT INTO ratings (game, rating) VALUES (?, ?)", (game, rating))

    conn.commit()
    conn.close()

@app.route('/rate', methods=['POST'])
def rate():
    print("start rate")
    rating = int(request.form['rating'])
    action = request.form['action']
    

    if action == 'Next':    
        print("old rating saved")
        save_rating(game_app.get_current_game(), rating) 
        #мы берем новую игру при выполнении recommendations()
        #game = game_app.get_next_game()

        if game_app.has_more_games():
            print("New game received")              
            return redirect(url_for('recommendations'))
        else:
            print("No new game")
            return redirect(url_for('completed'))
    elif action == 'Stop':
        print("User stopped")
        return redirect(url_for('completed'))


if __name__ == '__main__':
    app.run()